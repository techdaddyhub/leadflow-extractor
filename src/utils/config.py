"""
LeadFlow Intelligence Suite - Configuration & Settings
Defines application constants, session configurations, and persistence helpers.
"""

from __future__ import annotations
import json
import os
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional


class CrawlMode(str, Enum):
    DOMAIN_CRAWL = "Domain Deep Crawl"
    KEYWORD_SEARCH = "Keyword & Query Search"
    BULK_LIST = "Bulk Domain List"


ROLE_PATTERNS: Dict[str, List[str]] = {
    "Founders / C-Level": [
        "ceo", "founder", "cofounder", "co-founder", "owner", "president",
        "partner", "director", "managing", "principal", "cto", "cfo", "coo", "cmo"
    ],
    "Sales / BizDev": [
        "sales", "business", "bizdev", "deals", "partnerships", "growth",
        "leads", "commercial", "enterprise", "account", "inquiries"
    ],
    "Press / Media": [
        "press", "media", "pr", "news", "journalists", "comms", "editorial"
    ],
    "Support / Operations": [
        "support", "help", "service", "billing", "desk", "customerservice",
        "client", "care", "ops", "office", "admin"
    ],
    "General / Info": [
        "info", "contact", "hello", "team", "office", "mail", "general"
    ],
}

DEFAULT_COLUMNS = [
    "Email",
    "Extracted Name",
    "Domain",
    "Role",
    "Country/TLD",
    "Confidence Score",
    "Source URL",
    "HTTP Status",
    "Timestamp",
]

COMMON_COUNTRY_TLDS = {
    "All Countries": "",
    "United Kingdom (.uk)": "uk",
    "Germany (.de)": "de",
    "Nigeria (.ng)": "ng",
    "Canada (.ca)": "ca",
    "Australia (.au)": "au",
    "France (.fr)": "fr",
    "Netherlands (.nl)": "nl",
    "Spain (.es)": "es",
    "Italy (.it)": "it",
    "Switzerland (.ch)": "ch",
    "South Africa (.za)": "za",
    "India (.in)": "in",
    "Brazil (.br)": "br",
    "United States (.us / .com)": "us",
}


@dataclass
class CrawlConfig:
    """Session configuration for scraping engine."""
    mode: CrawlMode = CrawlMode.DOMAIN_CRAWL
    target_urls: List[str] = field(default_factory=list)
    search_query: str = ""
    country_tld: str = ""
    industry_niche: str = ""
    role_query: str = ""
    
    max_depth: int = 2
    batch_target: int = 500
    hard_stop_ceiling: int = 5000
    
    request_delay_ms: int = 400
    jitter_ms: int = 200
    concurrency_limit: int = 8
    timeout_seconds: int = 15
    
    respect_robots_txt: bool = False
    follow_internal_only: bool = True
    enable_obfuscation_decoding: bool = True
    enable_mx_validation: bool = False
    enable_deduplication: bool = True
    enable_garbage_filtering: bool = True
    
    selected_roles: List[str] = field(default_factory=lambda: list(ROLE_PATTERNS.keys()))
    user_agent_mode: str = "Rotating (Modern Browsers)"


class AppConfig:
    """Manages application state, directories, and persistence."""
    APP_NAME = "LeadFlow Email Extractor & Intelligence Suite"
    APP_VERSION = "1.0.0"
    ORGANIZATION = "LeadFlow Intelligence"

    @classmethod
    def get_data_dir(cls) -> Path:
        """Returns standard local app data directory for LeadFlow."""
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        path = Path(base) / "LeadFlow"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_settings_file(cls) -> Path:
        return cls.get_data_dir() / "settings.json"

    @classmethod
    def load_config(cls) -> CrawlConfig:
        filepath = cls.get_settings_file()
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "mode" in data:
                        data["mode"] = CrawlMode(data["mode"])
                    return CrawlConfig(**data)
            except Exception:
                pass
        return CrawlConfig()

    @classmethod
    def save_config(cls, config: CrawlConfig) -> None:
        filepath = cls.get_settings_file()
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                raw = asdict(config)
                raw["mode"] = config.mode.value
                json.dump(raw, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")

