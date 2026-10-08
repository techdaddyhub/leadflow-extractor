"""
Headless/Offscreen GUI verification for PyQt6 MainWindow.
"""

import os
import sys
from pathlib import Path

# Set offscreen platform for automated test runs
os.environ["QT_QPA_PLATFORM"] = "offscreen"

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.app.main_window import MainWindow


def test_ui():
    print("--> Initializing QApplication (offscreen mode)...")
    app = QApplication(sys.argv)

    print("--> Instantiating MainWindow...")
    window = MainWindow()

    # Verify initial components
    assert window.windowTitle() == "LeadFlow Email Extractor & Intelligence Suite"
    assert window.tab_widget.count() == 5
    assert window.table.columnCount() == 9
    assert window.table.rowCount() == 0

    print("--> Simulating receiving a lead...")
    test_lead = {
        "email": "alex.mercer@innovate.co.uk",
        "extracted_name": "Alex Mercer",
        "domain": "innovate.co.uk",
        "role": "Founders / C-Level",
        "country_tld": "United Kingdom",
        "confidence_score": 92,
        "source_url": "https://innovate.co.uk/team",
        "http_status": 200,
        "timestamp": "2026-10-08 12:30:00",
    }
    window._handle_lead_found(test_lead)

    assert window.table.rowCount() == 1
    assert window.table.item(0, 0).text() == "alex.mercer@innovate.co.uk"
    assert window.card_leads.value_label.text() == "0"  # Will update via progress
    print("    Lead inserted into table successfully.")

    print("--> Simulating progress update...")
    window._handle_progress_update({
        "leads_count": 1,
        "scanned_count": 5,
        "rate": 12.0,
        "current_url": "https://innovate.co.uk/contact",
    })
    assert window.card_leads.value_label.text() == "1"
    assert window.card_scanned.value_label.text() == "5"
    assert window.card_rate.value_label.text() == "12.0 / min"
    assert window.card_conf.value_label.text() == "92%"
    print("    KPI metrics and reactive state updated cleanly.")

    print("--> Simulating summary generation...")
    window._update_intelligence_summary()
    assert "Founders / C-Level" in window.txt_summary.toPlainText()
    print("    Intelligence report generated cleanly.")

    # Schedule clean exit
    QTimer.singleShot(500, app.quit)
    app.exec()
    print("\n==========================================")
    print("  GUI HEADLESS LAUNCH VERIFIED CLEANLY!   ")
    print("==========================================")


if __name__ == "__main__":
    test_ui()

