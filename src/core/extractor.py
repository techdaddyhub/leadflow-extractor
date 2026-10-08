"""
LeadFlow Intelligence Suite - Regex & DOM Email Extractor
Handles standard RFC 5322 patterns, obfuscated emails, mailto links, and context parsing.
"""

from __future__ import annotations
import html
import re
import urllib.parse
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from bs4 import BeautifulSoup


@dataclass
class ExtractedLead:
    """Represents a validated, enriched email lead."""
    email: str
    domain: str
    extracted_name: str
    role: str
    country_tld: str
    confidence_score: int
    source_url: str
    http_status: int
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EmailExtractor:
    """Production-grade email extraction engine."""

    # Standard RFC 5322 compliant email regex
    EMAIL_REGEX = re.compile(
        r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+",
        re.IGNORECASE,
    )

    # Obfuscated email patterns
    OBFUSCATED_PATTERNS = [
        # user [at] domain [dot] com or user (at) domain (dot) com
        re.compile(
            r"([a-zA-Z0-9._%+-]+)\s*(?:\[at\]|\(at\)|\[@\]|@|\s+at\s+)\s*([a-zA-Z0-9.-]+)\s*(?:\[dot\]|\(dot\)|\.|\s+dot\s+)\s*([a-zA-Z]{2,})",
            re.IGNORECASE,
        ),
        # user AT domain DOT com
        re.compile(
            r"\b([a-zA-Z0-9._%+-]+)\s+AT\s+([a-zA-Z0-9.-]+)\s+DOT\s+([a-zA-Z]{2,})\b",
            re.IGNORECASE,
        ),
    ]

    # File extensions commonly found in image URLs that mimic emails
    INVALID_EXTENSIONS = {
        "png", "jpg", "jpeg", "gif", "svg", "webp", "ico", "bmp", "tiff",
        "woff", "woff2", "ttf", "eot", "css", "js", "mp4", "mp3", "pdf",
        "zip", "tar", "gz", "exe", "dmg", "json", "xml", "csv"
    }

    def __init__(self, enable_obfuscation: bool = True):
        self.enable_obfuscation = enable_obfuscation

    def extract_from_html(
        self,
        html_content: str,
        source_url: str = "",
        http_status: int = 200,
    ) -> List[Tuple[str, str, int]]:
        """
        Extracts raw email candidates from HTML.
        Returns a list of tuples: (email, candidate_name, base_confidence)
        """
        candidates: Dict[str, Tuple[str, int]] = {}
        if not html_content:
            return []

        # Decode HTML entities first (e.g. &#64;, &commat;)
        decoded_html = html.unescape(html_content)

        soup = None
        try:
            soup = BeautifulSoup(decoded_html, "html.parser")
        except Exception:
            pass

        # 1. Extract from mailto: links in DOM
        if soup:
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                if href.lower().startswith("mailto:"):
                    clean_mailto = self._parse_mailto(href)
                    if clean_mailto and self._is_valid_syntax(clean_mailto):
                        name = a_tag.get_text(strip=True)
                        if not name or "@" in name or len(name) > 60:
                            name = self._name_from_email(clean_mailto)
                        candidates[clean_mailto.lower()] = (name, 90)

            # Strip non-visible elements (scripts, styles, hidden tags)
            for element in soup(["script", "style", "noscript", "meta"]):
                element.decompose()
            clean_text = soup.get_text(separator=" ")
        else:
            clean_text = decoded_html

        # 2. Extract standard emails from text
        for match in self.EMAIL_REGEX.finditer(clean_text):
            raw_email = match.group(0).strip(".,;:()<>[]\"' ")
            if self._is_valid_syntax(raw_email):
                norm = raw_email.lower()
                if norm not in candidates:
                    candidates[norm] = (self._name_from_email(norm), 80)

        # 3. Extract obfuscated emails if enabled
        if self.enable_obfuscation:
            for pattern in self.OBFUSCATED_PATTERNS:
                for match in pattern.finditer(clean_text):
                    user, domain, tld = match.groups()
                    reconstructed = f"{user}@{domain}.{tld}".strip().lower()
                    if self._is_valid_syntax(reconstructed):
                        if reconstructed not in candidates:
                            candidates[reconstructed] = (
                                self._name_from_email(reconstructed),
                                75,
                            )

        # 4. Search raw HTML attributes (like data-email, data-mailto)
        raw_matches = self.EMAIL_REGEX.findall(decoded_html)
        for raw_email in raw_matches:
            raw_email = raw_email.strip(".,;:()<>[]\"' ")
            if self._is_valid_syntax(raw_email):
                norm = raw_email.lower()
                if norm not in candidates:
                    candidates[norm] = (self._name_from_email(norm), 75)

        return [(email, name, conf) for email, (name, conf) in candidates.items()]

    def _parse_mailto(self, href: str) -> Optional[str]:
        """Extracts clean email address from mailto: URL scheme."""
        try:
            unquoted = urllib.parse.unquote(href)
            email_part = unquoted[7:].split("?")[0].strip()
            # If multiple emails separated by comma or semicolon, take first
            first_email = re.split(r"[,;]", email_part)[0].strip()
            return first_email
        except Exception:
            return None

    def _is_valid_syntax(self, email: str) -> bool:
        """Preliminary syntax filter to drop image assets or malformed patterns."""
        if not email or "@" not in email:
            return False
        if len(email) > 254:
            return False

        parts = email.split("@")
        if len(parts) != 2:
            return False

        local_part, domain_part = parts
        if not local_part or not domain_part:
            return False

        # Must have at least one dot in domain part
        if "." not in domain_part:
            return False

        # Reject CDN paths or URLs in local part
        if "/" in local_part or "\\" in local_part or "jsdelivr" in local_part or "unpkg" in local_part:
            return False

        # Reject phone numbers disguised as domains (e.g. 704.246.0864)
        if re.search(r"\d+\.\d+\.\d+", domain_part):
            return False

        # Extract TLD
        ext = domain_part.rsplit(".", 1)[-1].lower()

        # TLD must be alphabetic and at least 2 chars (no numbers like @3.12.5)
        if not ext.isalpha() or len(ext) < 2:
            return False

        # Exclude false positives ending in static asset extensions (e.g. photo@2x.png)
        if ext in self.INVALID_EXTENSIONS:
            return False

        # Exclude common sentence words captured after period (e.g. email.com.How -> email.com)
        if ext in {"how", "where", "view", "about", "from", "to", "is", "the", "you", "and", "or", "with", "at", "what", "why"}:
            return False

        # Local part cannot start or end with dot
        if local_part.startswith(".") or local_part.endswith("."):
            return False

        return True

    def _name_from_email(self, email: str) -> str:
        """Derives clean human-readable name from local part."""
        local = email.split("@")[0]
        # Remove numbers and common noise
        cleaned = re.sub(r"\d+", "", local)
        # Split on dot, underscore, hyphen
        tokens = [t.capitalize() for t in re.split(r"[._\-+]+", cleaned) if len(t) > 1]
        if tokens:
            return " ".join(tokens)
        return local.capitalize()

