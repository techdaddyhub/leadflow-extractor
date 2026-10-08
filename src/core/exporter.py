"""
LeadFlow Intelligence Suite - Multi-Format Exporter
Supports high-performance export to CSV (UTF-8 BOM), Excel (XLSX), and JSON.
"""

from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Union

from .extractor import ExtractedLead
from ..utils.config import DEFAULT_COLUMNS

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import openpyxl
except ImportError:
    openpyxl = None


class LeadExporter:
    """Exports lead collections to diverse formats."""

    @staticmethod
    def to_csv(leads: List[Union[ExtractedLead, Dict[str, Any]]], filepath: Union[str, Path]) -> str:
        """Exports leads to CSV with utf-8-sig encoding for native Excel compatibility."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        rows = [lead.to_dict() if isinstance(lead, ExtractedLead) else lead for lead in leads]
        if not rows:
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(DEFAULT_COLUMNS)
            return str(path)

        fieldnames = [
            "email", "extracted_name", "domain", "role",
            "country_tld", "confidence_score", "source_url",
            "http_status", "timestamp"
        ]

        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            # Write custom friendly header
            f.write(",".join(f'"{col}"' for col in DEFAULT_COLUMNS) + "\n")
            for r in rows:
                writer.writerow(r)

        return str(path)

    @staticmethod
    def to_excel(leads: List[Union[ExtractedLead, Dict[str, Any]]], filepath: Union[str, Path]) -> str:
        """Exports leads to Microsoft Excel .xlsx workbook."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        rows = [lead.to_dict() if isinstance(lead, ExtractedLead) else lead for lead in leads]

        if pd is not None:
            df = pd.DataFrame(rows)
            # Rename columns to standard display names
            rename_map = {
                "email": "Email",
                "extracted_name": "Extracted Name",
                "domain": "Domain",
                "role": "Role",
                "country_tld": "Country/TLD",
                "confidence_score": "Confidence Score",
                "source_url": "Source URL",
                "http_status": "HTTP Status",
                "timestamp": "Timestamp",
            }
            df = df.rename(columns=rename_map)
            # Reorder to match DEFAULT_COLUMNS if all present
            ordered_cols = [c for c in DEFAULT_COLUMNS if c in df.columns]
            if ordered_cols:
                df = df[ordered_cols]
            df.to_excel(path, index=False, engine="openpyxl")
            return str(path)

        # Fallback to pure CSV if pandas/openpyxl not present
        csv_fallback = path.with_suffix(".csv")
        return LeadExporter.to_csv(leads, csv_fallback)

    @staticmethod
    def to_json(leads: List[Union[ExtractedLead, Dict[str, Any]]], filepath: Union[str, Path], pretty: bool = True) -> str:
        """Exports leads to JSON."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        rows = [lead.to_dict() if isinstance(lead, ExtractedLead) else lead for lead in leads]
        with open(path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(rows, f, indent=2, ensure_ascii=False)
            else:
                json.dump(rows, f, ensure_ascii=False)

        return str(path)

