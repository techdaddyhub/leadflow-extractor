"""
LeadFlow Intelligence Suite - User-Agent & Header Rotation Engine
Provides modern desktop and mobile user agents, client hint headers, and randomized rotation.
"""

from __future__ import annotations
import random
from typing import Dict, List, Optional

CHROME_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

FIREFOX_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
]

EDGE_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

SAFARI_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
]

ALL_USER_AGENTS = CHROME_USER_AGENTS + EDGE_USER_AGENTS + FIREFOX_USER_AGENTS + SAFARI_USER_AGENTS


class UserAgentRotator:
    """Manages User-Agent pools and generates realistic HTTP headers."""

    def __init__(self, mode: str = "Rotating (Modern Browsers)"):
        self.mode = mode
        self._index = 0
        self._pool = self._build_pool(mode)

    def _build_pool(self, mode: str) -> List[str]:
        if "Chrome" in mode:
            return list(CHROME_USER_AGENTS)
        elif "Firefox" in mode:
            return list(FIREFOX_USER_AGENTS)
        elif "Edge" in mode:
            return list(EDGE_USER_AGENTS)
        return list(ALL_USER_AGENTS)

    def get_user_agent(self) -> str:
        """Returns a randomized or round-robin User-Agent."""
        if not self._pool:
            return ALL_USER_AGENTS[0]
        return random.choice(self._pool)

    def get_headers(self, referer: Optional[str] = None) -> Dict[str, str]:
        """Generates realistic browser headers to prevent basic bot filtering."""
        ua = self.get_user_agent()
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site" if referer else "none",
            "Sec-Fetch-User": "?1",
        }
        if referer:
            headers["Referer"] = referer

        if "Chrome" in ua or "Edg" in ua:
            headers["Sec-Ch-Ua"] = '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
            headers["Sec-Ch-Ua-Mobile"] = "?0"
            headers["Sec-Ch-Ua-Platform"] = '"Windows"'

        return headers

