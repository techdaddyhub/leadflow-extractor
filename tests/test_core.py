"""
Unit test verification for LeadFlow core pipeline.
"""

import sys
import shutil
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.core.extractor import EmailExtractor
from src.core.filter import LeadFilter
from src.core.exporter import LeadExporter
from src.utils.config import CrawlConfig


def test_extractor_and_filter():
    print("--> 1. Testing Extractor...")
    extractor = EmailExtractor(enable_obfuscation=True)

    sample_html = """
    <html>
    <body>
      <h1>Contact Acme Enterprise</h1>
      <p>Founder & CEO: <a href="mailto:sarah.connor@acme.co.uk?subject=Hello">Sarah Connor</a></p>
      <p>Sales Inquiries: sales@acme.co.uk</p>
      <p>Hidden Team: press [at] acme [dot] com</p>
      <p>Garbage: logo@2x.png, test@example.com, and noreply@acme.com</p>
    </body>
    </html>
    """

    results = extractor.extract_from_html(sample_html, "https://acme.co.uk")
    assert len(results) > 0, "No emails extracted!"
    print(f"    Extracted {len(results)} raw candidates.")

    print("\n--> 2. Testing Filter Pipeline...")
    cfg = CrawlConfig()
    filter_engine = LeadFilter(cfg)
    filtered = []

    for email, name, conf in results:
        res = filter_engine.process(email, name, "https://acme.co.uk", 200, conf)
        if res:
            filtered.append(res)
            print(f"    [ACCEPTED] {res[0]} | Name: {res[1]} | Role: {res[3]} | Country: {res[4]} | Conf: {res[5]}%")
        else:
            print(f"    [REJECTED] {email}")

    # Check that bogus emails were rejected
    emails = [r[0] for r in filtered]
    assert "logo@2x.png" not in emails
    assert "test@example.com" not in emails
    assert "noreply@acme.com" not in emails

    # Check that valid were accepted
    assert "sarah.connor@acme.co.uk" in emails
    assert "sales@acme.co.uk" in emails
    assert "press@acme.com" in emails

    print(f"\n--> 3. Filter successfully verified: {len(filtered)} valid leads preserved.")

    print("\n--> 4. Testing Exporter...")
    tmp_dir = ROOT_DIR / "test_exports"
    tmp_dir.mkdir(exist_ok=True)

    sample_leads = [
        {
            "email": r[0],
            "extracted_name": r[1],
            "domain": r[2],
            "role": r[3],
            "country_tld": r[4],
            "confidence_score": r[5],
            "source_url": "https://acme.co.uk",
            "http_status": 200,
            "timestamp": "2026-10-08 12:00:00",
        }
        for r in filtered
    ]

    csv_file = LeadExporter.to_csv(sample_leads, tmp_dir / "test.csv")
    xlsx_file = LeadExporter.to_excel(sample_leads, tmp_dir / "test.xlsx")
    json_file = LeadExporter.to_json(sample_leads, tmp_dir / "test.json")

    assert Path(csv_file).exists() and Path(csv_file).stat().st_size > 0
    assert Path(xlsx_file).exists() and Path(xlsx_file).stat().st_size > 0
    assert Path(json_file).exists() and Path(json_file).stat().st_size > 0

    print(f"    Exported CSV: {Path(csv_file).stat().st_size} bytes")
    print(f"    Exported Excel: {Path(xlsx_file).stat().st_size} bytes")
    print(f"    Exported JSON: {Path(json_file).stat().st_size} bytes")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    print("\n--> 5. Exporter verification PASSED.")


if __name__ == "__main__":
    test_extractor_and_filter()
    print("\n==========================================")
    print("  ALL CORE ENGINE TESTS PASSED CLEANLY!   ")
    print("==========================================")

