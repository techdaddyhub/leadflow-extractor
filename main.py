"""
LeadFlow Email Extractor & Intelligence Suite - Desktop Application Entry Point
"""

import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from src.app.main_window import MainWindow


def main():
    # Enable crisp Windows taskbar app identification
    if sys.platform == "win32":
        try:
            import ctypes
            myappid = "leadflow.intelligence.extractor.suite.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("LeadFlow Email Extractor & Intelligence Suite")
    app.setOrganizationName("LeadFlow Intelligence")

    icon_path = BASE_DIR / "assets" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

