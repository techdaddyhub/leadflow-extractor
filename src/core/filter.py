"""
LeadFlow Intelligence Suite - Smart Filtering & Validation Pipeline
Handles deduplication, country/TLD classification, garbage/honeypot filtering,
role classification, and MX syntax checks.
"""

from __future__ import annotations
import re
import socket
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

try:
    import tldextract
except ImportError:
    tldextract = None

try:
    import dns.resolver
except ImportError:
    dns = None

try:
    from email_validator import validate_email, EmailNotValidError
except ImportError:
    validate_email = None

from ..utils.config import CrawlConfig, ROLE_PATTERNS


COUNTRY_TLD_MAP = {
    "uk": "United Kingdom",
    "co.uk": "United Kingdom",
    "de": "Germany",
    "ng": "Nigeria",
    "ca": "Canada",
    "au": "Australia",
    "com.au": "Australia",
    "fr": "France",
    "nl": "Netherlands",
    "es": "Spain",
    "it": "Italy",
    "ch": "Switzerland",
    "za": "South Africa",
    "co.za": "South Africa",
    "in": "India",
    "co.in": "India",
    "br": "Brazil",
    "com.br": "Brazil",
    "us": "United States",
    "com": "Global (.com)",
    "net": "Global (.net)",
    "org": "Non-Profit (.org)",
    "io": "Tech (.io)",
    "ai": "AI (.ai)",
    "co": "Global (.co)",
}

HONEYPOT_PREFIXES = {
    "test", "tester", "spam", "abuse", "noreply", "no-reply", "donotreply",
    "do-not-reply", "postmaster", "mailer-daemon", "webmaster", "null",
    "nobody", "root", "devnull", "bounce", "bounces", "unsubscribe"
}

HONEYPOT_DOMAINS = {
    "example.com", "example.org", "example.net", "domain.com", "sample.com",
    "test.com", "yoursite.com", "yourdomain.com", "company.com", "email.com",
    "localhost", "sentry.io", "wixpress.com", "schema.org", "w3.org",
    "github.com", "facebook.com", "twitter.com", "linkedin.com", "instagram.com"
}

MEDIA_EXTENSIONS = {
    "png", "jpg", "jpeg", "gif", "svg", "webp", "ico", "bmp", "tiff",
    "woff", "woff2", "ttf", "eot", "css", "js", "mp4", "mp3", "pdf",
    "zip", "tar", "gz", "exe", "dmg", "json", "xml", "csv"
}


class LeadFilter:
    """Multi-stage intelligent filter and classifier."""

    def __init__(self, config: CrawlConfig):
        self.config = config
        self.seen_emails: Set[str] = set()
        self.mx_cache: Dict[str, bool] = {}
        self._tld_extractor = tldextract.TLDExtract(cache_dir=None) if tldextract else None

    def reset(self) -> None:
        """Clears in-memory deduplication set and cache."""
        self.seen_emails.clear()
        self.mx_cache.clear()

    def process(
        self,
        raw_email: str,
        extracted_name: str,
        source_url: str,
        http_status: int = 200,
        base_confidence: int = 80,
    ) -> Optional[Tuple[str, str, str, str, str, int]]:
        """
        Filters and enriches an email candidate.
        Returns:
            (email, name, domain, role, country_tld, confidence) or None if rejected.
        """
        email = raw_email.strip().lower()

        # 1. Deduplication
        if self.config.enable_deduplication:
            if email in self.seen_emails:
                return None

        # 2. Basic format sanity
        if "@" not in email:
            return None
        local, domain = email.split("@", 1)
        if not local or not domain or "." not in domain:
            return None

        # 3. Garbage & Honeypot Filtering
        if self.config.enable_garbage_filtering:
            if not self._passes_garbage_filter(local, domain):
                return None

        # 4. TLD Extraction & Country Classifier
        registered_domain, suffix = self._extract_tld_info(domain)
        country_name = COUNTRY_TLD_MAP.get(suffix, f".{suffix}".upper())

        # Check country TLD restriction if user configured one
        if self.config.country_tld:
            target = self.config.country_tld.lower().strip(".")
            if not suffix.endswith(target):
                return None

        # 5. Syntax validation via email-validator if installed
        confidence = base_confidence
        if validate_email:
            try:
                validate_email(email, check_deliverability=False)
                confidence = min(100, confidence + 5)
            except Exception:
                return None

        # 6. Role Classification
        role_label = self._classify_role(local)

        # Check role restriction if selected in config
        if self.config.selected_roles:
            if role_label not in self.config.selected_roles and role_label != "Personal":
                # If specific roles selected, check if user matches
                pass

        # 7. MX Record verification (if enabled)
        if self.config.enable_mx_validation:
            has_mx = self._check_mx_record(domain)
            if not has_mx:
                return None
            confidence = min(100, confidence + 10)

        # Register deduplication
        if self.config.enable_deduplication:
            self.seen_emails.add(email)

        # Clean name if generic
        if not extracted_name or extracted_name.lower() == local.lower():
            extracted_name = self._format_name(local)

        return (email, extracted_name, domain, role_label, country_name, confidence)

    def _passes_garbage_filter(self, local: str, domain: str) -> bool:
        """Determines if email looks like honeypot or image artifact."""
        # Honeypot domains
        if domain in HONEYPOT_DOMAINS:
            return False

        # Honeypot prefixes
        if local in HONEYPOT_PREFIXES:
            return False

        # Suspicious artifact tokens
        if any(token in local for token in ["u002f", "u003c", "webpack", "react", "avatar"]):
            return False

        # Ending in media extension
        ext = domain.rsplit(".", 1)[-1].lower()
        if ext in MEDIA_EXTENSIONS:
            return False

        # Obvious image resolution strings (e.g. 200x200, 2x, etc.)
        if re.search(r"\d+x\d+", local) or local.endswith("@2x"):
            return False

        # Disallow non-ASCII weirdness in standard domains
        if any(c in local for c in [" ", "\t", "\n", "\r", "\\", "/", "<", ">"]):
            return False

        return True

    def _extract_tld_info(self, domain: str) -> Tuple[str, str]:
        """Returns (registered_domain, suffix)."""
        if self._tld_extractor:
            ext = self._tld_extractor(domain)
            registered = ext.registered_domain or domain
            suffix = ext.suffix or domain.rsplit(".", 1)[-1]
            return registered, suffix
        parts = domain.rsplit(".", 1)
        suffix = parts[-1] if len(parts) > 1 else ""
        return domain, suffix

    def _classify_role(self, local: str) -> str:
        """Identifies corporate role from local mailbox prefix."""
        cleaned = re.sub(r"[^a-zA-Z]", "", local).lower()

        for role_name, patterns in ROLE_PATTERNS.items():
            for pat in patterns:
                if pat == cleaned or cleaned.startswith(pat) or cleaned.endswith(pat):
                    return role_name

        # If it contains dots or underscores and typical name length, mark as Personal
        if ("." in local or "_" in local) and len(local) > 4:
            return "Personal"

        return "General / Inquiries"

    def _check_mx_record(self, domain: str) -> bool:
        """Queries DNS MX records for domain with in-memory caching."""
        if domain in self.mx_cache:
            return self.mx_cache[domain]

        # Use dnspython if installed
        if dns:
            try:
                answers = dns.resolver.resolve(domain, "MX", lifetime=3.0)
                if len(answers) > 0:
                    self.mx_cache[domain] = True
                    return True
            except Exception:
                pass

        # Socket fallback
        try:
            socket.getaddrinfo(domain, 80, socket.AF_UNSPEC, socket.SOCK_STREAM)
            self.mx_cache[domain] = True
            return True
        except Exception:
            self.mx_cache[domain] = False
            return False

    def _format_name(self, local: str) -> str:
        """Transforms sarah.connor into Sarah Connor."""
        cleaned = re.sub(r"\d+", "", local)
        parts = [p.capitalize() for p in re.split(r"[._\-+]+", cleaned) if len(p) > 1]
        return " ".join(parts) if parts else local.capitalize()

