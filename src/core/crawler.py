"""
LeadFlow Intelligence Suite - Async Crawler & Request Engine
High-throughput, respectful HTTP/2 crawler with rate limiting, robots.txt compliance,
search engine discovery, and domain depth boundaries.
"""

from __future__ import annotations
import asyncio
import random
import re
import time
import urllib.parse
from typing import AsyncGenerator, Callable, Dict, List, Optional, Set, Tuple
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from ..utils.config import CrawlConfig, CrawlMode
from ..utils.user_agents import UserAgentRotator
from .extractor import EmailExtractor, ExtractedLead
from .filter import LeadFilter


class AsyncCrawler:
    """Enterprise async web crawler with intelligent queue management."""

    def __init__(
        self,
        config: CrawlConfig,
        on_lead_found: Optional[Callable[[ExtractedLead], None]] = None,
        on_progress: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_log: Optional[Callable[[str, str], None]] = None,
    ):
        self.config = config
        self.on_lead_found = on_lead_found
        self.on_progress = on_progress
        self.on_log = on_log

        self.ua_rotator = UserAgentRotator(config.user_agent_mode)
        self.extractor = EmailExtractor(enable_obfuscation=config.enable_obfuscation_decoding)
        self.lead_filter = LeadFilter(config)

        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Unpaused initially
        self._stop_requested = False

        self.visited_urls: Set[str] = set()
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.total_leads = 0
        self.total_scanned = 0
        self.start_time: float = 0.0

    def pause(self) -> None:
        self._pause_event.clear()
        self._log("INFO", "Crawl worker paused by user.")

    def resume(self) -> None:
        self._pause_event.set()
        self._log("INFO", "Crawl worker resumed.")

    def stop(self) -> None:
        self._stop_requested = True
        self._pause_event.set()  # Ensure loop unblocks to exit
        self._log("WARN", "Stop requested. Finalizing operations...")

    def _log(self, level: str, message: str) -> None:
        if self.on_log:
            self.on_log(level, message)

    def _update_stats(self, current_url: str) -> None:
        elapsed = max(1.0, time.time() - self.start_time)
        rate = round((self.total_leads / elapsed) * 60, 1)
        if self.on_progress:
            self.on_progress({
                "scanned_count": self.total_scanned,
                "leads_count": self.total_leads,
                "current_url": current_url,
                "rate": rate,
                "elapsed": elapsed,
            })

    async def run(self) -> None:
        """Main crawl execution routine."""
        self.start_time = time.time()
        self.visited_urls.clear()
        self.robots_cache.clear()
        self.lead_filter.reset()
        self.total_leads = 0
        self.total_scanned = 0
        self._stop_requested = False
        self._pause_event.set()

        limits = httpx.Limits(
            max_keepalive_connections=self.config.concurrency_limit * 2,
            max_connections=self.config.concurrency_limit * 3,
        )
        timeout = httpx.Timeout(self.config.timeout_seconds, connect=8.0)

        async with httpx.AsyncClient(
            http2=True,
            limits=limits,
            timeout=timeout,
            follow_redirects=True,
            verify=False,
        ) as client:
            try:
                if self.config.mode == CrawlMode.KEYWORD_SEARCH:
                    await self._run_search_discovery(client)
                elif self.config.mode == CrawlMode.BULK_LIST:
                    await self._run_bulk_crawl(client)
                else:
                    await self._run_deep_domain_crawl(client)
            except asyncio.CancelledError:
                self._log("WARN", "Crawl worker task cancelled.")
            except Exception as e:
                self._log("ERROR", f"Crawl engine unexpected error: {e}")
            finally:
                self._log("SUCCESS", f"Session complete: Extracted {self.total_leads} leads across {self.total_scanned} pages.")

    async def _run_search_discovery(self, client: httpx.AsyncClient) -> None:
        """Performs search engine discovery to collect target URLs, then deep-crawls them."""
        query_terms = [self.config.search_query.strip()]
        if self.config.industry_niche:
            query_terms.append(f'"{self.config.industry_niche.strip()}"')
        if self.config.role_query:
            query_terms.append(f'"{self.config.role_query.strip()}"')
        if self.config.country_tld:
            query_terms.append(f"site:.{self.config.country_tld.strip('.')}")

        # Add contact discovery footprints
        query_terms.append('("contact" OR "about" OR "email" OR "team")')
        full_query = " ".join([t for t in query_terms if t])

        self._log("INFO", f"Searching discovery engine with query: {full_query}")

        discovered_urls: List[str] = []
        try:
            discovered_urls = await self._search_duckduckgo(client, full_query)
            self._log("SUCCESS", f"Search engine returned {len(discovered_urls)} target domains/pages.")
        except Exception as e:
            self._log("ERROR", f"Search query failed: {e}")

        if not discovered_urls:
            self._log("WARN", "No URLs discovered from search engine. Falling back to configured targets.")
            discovered_urls = self.config.target_urls

        await self._crawl_queue(client, discovered_urls)

    async def _search_duckduckgo(self, client: httpx.AsyncClient, query: str) -> List[str]:
        """Queries DuckDuckGo HTML endpoint and extracts target links."""
        url = "https://html.duckduckgo.com/html/"
        data = {"q": query, "b": ""}
        headers = self.ua_rotator.get_headers(referer="https://duckduckgo.com/")

        resp = await client.post(url, data=data, headers=headers)
        if resp.status_code != 200:
            self._log("WARN", f"DuckDuckGo returned HTTP {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        links: List[str] = []
        for a in soup.find_all("a", class_="result__url", href=True):
            raw_href = a["href"]
            parsed_href = self._unwrap_ddg_url(raw_href)
            if parsed_href and parsed_href.startswith("http") and "duckduckgo" not in parsed_href:
                links.append(parsed_href)

        # Fallback to general result snippets if class differs
        if not links:
            for a in soup.find_all("a", class_="result__snippet", href=True):
                raw_href = a["href"]
                parsed_href = self._unwrap_ddg_url(raw_href)
                if parsed_href and parsed_href.startswith("http") and "duckduckgo" not in parsed_href:
                    links.append(parsed_href)

        return list(dict.fromkeys(links))[:30]

    def _unwrap_ddg_url(self, href: str) -> Optional[str]:
        """Extracts the destination URL from DDG redirect url."""
        if "uddg=" in href:
            try:
                parsed = urllib.parse.urlparse(href)
                qs = urllib.parse.parse_qs(parsed.query)
                if "uddg" in qs:
                    return qs["uddg"][0]
            except Exception:
                pass
        if href.startswith("//"):
            return "https:" + href
        return href

    async def _run_bulk_crawl(self, client: httpx.AsyncClient) -> None:
        """Processes a bulk list of seed domains."""
        urls: List[str] = []
        for entry in self.config.target_urls:
            clean = entry.strip()
            if not clean:
                continue
            if not clean.startswith("http://") and not clean.startswith("https://"):
                clean = f"https://{clean}"
            urls.append(clean)

        self._log("INFO", f"Ingested {len(urls)} target seed URLs for batch crawl.")
        await self._crawl_queue(client, urls)

    async def _run_deep_domain_crawl(self, client: httpx.AsyncClient) -> None:
        """Deep crawls single or multiple target websites."""
        await self._crawl_queue(client, self.config.target_urls)

    async def _crawl_queue(self, client: httpx.AsyncClient, seed_urls: List[str]) -> None:
        """Asynchronous BFS link queue with depth tracking and concurrency limit."""
        queue: asyncio.Queue[Tuple[str, int, str]] = asyncio.Queue()
        for u in seed_urls:
            norm = self._normalize_url(u)
            if norm:
                domain = urllib.parse.urlparse(norm).netloc
                await queue.put((norm, 1, domain))

        semaphore = asyncio.Semaphore(self.config.concurrency_limit)

        async def worker() -> None:
            while not queue.empty() and not self._stop_requested:
                await self._pause_event.wait()

                # Check ceiling limit
                if self.total_leads >= self.config.hard_stop_ceiling:
                    self._log("WARN", f"Hard stop ceiling reached ({self.config.hard_stop_ceiling} leads). Halting.")
                    self._stop_requested = True
                    break

                try:
                    url, depth, root_domain = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

                if url in self.visited_urls:
                    queue.task_done()
                    continue

                self.visited_urls.add(url)

                async with semaphore:
                    child_links = await self._process_single_page(client, url, depth, root_domain)

                    # Enqueue child links if within max depth
                    if depth < self.config.max_depth and not self._stop_requested:
                        for child in child_links:
                            if child not in self.visited_urls:
                                await queue.put((child, depth + 1, root_domain))

                queue.task_done()

                # Ethical jitter & rate limiting
                delay = (self.config.request_delay_ms + random.randint(0, self.config.jitter_ms)) / 1000.0
                await asyncio.sleep(delay)

        workers = [asyncio.create_task(worker()) for _ in range(self.config.concurrency_limit)]
        await asyncio.gather(*workers, return_exceptions=True)

    async def _process_single_page(
        self,
        client: httpx.AsyncClient,
        url: str,
        depth: int,
        root_domain: str,
    ) -> List[str]:
        """Fetches page, extracts emails, filters, and discovers internal links."""
        if self._stop_requested:
            return []

        # Check robots.txt compliance if enabled
        if self.config.respect_robots_txt:
            allowed = await self._check_robots_txt(client, url)
            if not allowed:
                self._log("WARN", f"Skipped (disallowed by robots.txt): {url}")
                return []

        self.total_scanned += 1
        self._update_stats(url)

        headers = self.ua_rotator.get_headers()
        http_status = 0
        html_text = ""

        try:
            response = await client.get(url, headers=headers)
            http_status = response.status_code
            if http_status >= 400:
                self._log("WARN", f"[{http_status}] Failed to fetch: {url}")
                return []
            html_text = response.text
        except Exception as e:
            self._log("WARN", f"Request failed for {url}: {e}")
            return []

        # Extract candidates
        raw_candidates = self.extractor.extract_from_html(
            html_content=html_text,
            source_url=url,
            http_status=http_status,
        )

        for raw_email, name, base_conf in raw_candidates:
            if self._stop_requested or self.total_leads >= self.config.hard_stop_ceiling:
                break

            processed = self.lead_filter.process(
                raw_email=raw_email,
                extracted_name=name,
                source_url=url,
                http_status=http_status,
                base_confidence=base_conf,
            )
            if processed:
                email, full_name, domain, role, country_tld, conf = processed
                lead = ExtractedLead(
                    email=email,
                    domain=domain,
                    extracted_name=full_name,
                    role=role,
                    country_tld=country_tld,
                    confidence_score=conf,
                    source_url=url,
                    http_status=http_status,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                )
                self.total_leads += 1
                if self.on_lead_found:
                    self.on_lead_found(lead)
                self._update_stats(url)

        # Discover internal links for deep crawl
        discovered_internal: List[str] = []
        if depth < self.config.max_depth:
            discovered_internal = self._extract_links(html_text, url, root_domain)

        return discovered_internal

    def _extract_links(self, html_text: str, base_url: str, root_domain: str) -> List[str]:
        """Extracts and resolves valid internal hyperlinks."""
        links: List[str] = []
        try:
            soup = BeautifulSoup(html_text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    continue
                resolved = urllib.parse.urljoin(base_url, href)
                parsed = urllib.parse.urlparse(resolved)
                if parsed.scheme not in ("http", "https"):
                    continue

                # Strip query and fragments to normalize
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

                # Boundary check: internal domain only?
                if self.config.follow_internal_only:
                    if not self._is_same_domain(parsed.netloc, root_domain):
                        continue

                # Priority for pages likely containing contact information
                lower_path = parsed.path.lower()
                is_contact_page = any(k in lower_path for k in [
                    "contact", "about", "team", "people", "staff", "management",
                    "leadership", "directory", "impressum", "connect", "reach-us"
                ])

                if is_contact_page:
                    links.insert(0, clean_url)
                else:
                    links.append(clean_url)
        except Exception:
            pass

        return list(dict.fromkeys(links))[:25]  # Cap child fanout per page

    def _is_same_domain(self, netloc1: str, netloc2: str) -> bool:
        """Checks if two hostnames belong to the same registered root."""
        h1 = netloc1.lower().split(":")[0].replace("www.", "")
        h2 = netloc2.lower().split(":")[0].replace("www.", "")
        return h1 == h2 or h1.endswith("." + h2) or h2.endswith("." + h1)

    async def _check_robots_txt(self, client: httpx.AsyncClient, url: str) -> bool:
        """Parses and evaluates robots.txt rules for the domain."""
        parsed = urllib.parse.urlparse(url)
        root = f"{parsed.scheme}://{parsed.netloc}"

        if root in self.robots_cache:
            rp = self.robots_cache[root]
            return rp.can_fetch("*", url)

        robots_url = f"{root}/robots.txt"
        rp = RobotFileParser()
        try:
            resp = await client.get(robots_url, headers=self.ua_rotator.get_headers(), timeout=5.0)
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            else:
                rp.allow_all = True
        except Exception:
            rp.allow_all = True

        self.robots_cache[root] = rp
        return rp.can_fetch("*", url)

    def _normalize_url(self, raw_url: str) -> Optional[str]:
        """Normalizes and validates target URL."""
        if not raw_url:
            return None
        url = raw_url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc:
            return None
        return url

