"""
LeadFlow Intelligence Suite - Modern Fluent Dark QSS Theme
Provides Windows 11 Fluent & Material design dark styling for PyQt6.
Features ultra-visible high-contrast input boxes, crisp indicators, and sleek buttons.
"""

import sys
from pathlib import Path


def get_dark_theme_qss() -> str:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys._MEIPASS)
    else:
        base_dir = Path(__file__).resolve().parent.parent.parent

    check_icon = (base_dir / "assets" / "check.png").as_posix()
    radio_icon = (base_dir / "assets" / "radio_dot.png").as_posix()

    return f"""
/* Global Application Styles */
QWidget {{
    background-color: #121316;
    color: #e2e8f0;
    font-family: "Segoe UI", "Segoe UI Variable Text", system-ui, -apple-system, sans-serif;
    font-size: 13px;
    selection-background-color: #6366f1;
    selection-color: #ffffff;
}}

/* Main Window */
QMainWindow {{
    background-color: #0f1013;
}}

/* Card / Container Panels */
QFrame#MetricCard, QFrame#PanelCard {{
    background-color: #1a1c23;
    border: 1px solid #282b37;
    border-radius: 10px;
}}

QFrame#MetricCard:hover {{
    border: 1px solid #3d4256;
}}

/* Headers and Labels */
QLabel {{
    background-color: transparent;
    color: #cbd5e1;
}}

QLabel#CardTitle {{
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel#CardValue {{
    color: #f8fafc;
    font-size: 22px;
    font-weight: 700;
}}

QLabel#AppTitle {{
    color: #f8fafc;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.3px;
}}

QLabel#AppSubtitle {{
    color: #818cf8;
    font-size: 11px;
    font-weight: 600;
}}

/* Tab Widget & Bar */
QTabWidget::pane {{
    border: 1px solid #232631;
    background-color: #16181f;
    border-radius: 8px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: #121316;
    color: #94a3b8;
    padding: 10px 20px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid transparent;
    font-weight: 600;
    min-width: 120px;
}}

QTabBar::tab:hover {{
    background-color: #1c1e24;
    color: #f1f5f9;
}}

QTabBar::tab:selected {{
    background-color: #16181f;
    color: #818cf8;
    border: 1px solid #232631;
    border-bottom: 2px solid #6366f1;
}}

/* Buttons */
QPushButton {{
    background-color: #242733;
    color: #f8fafc;
    border: 1px solid #333849;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    min-height: 22px;
}}

QPushButton:hover {{
    background-color: #2f3445;
    border-color: #4b526d;
}}

QPushButton:pressed {{
    background-color: #1e212b;
}}

QPushButton:disabled {{
    background-color: #17181e;
    color: #4b5563;
    border-color: #232631;
}}

/* Primary Action Button (Start) */
QPushButton#PrimaryBtn {{
    background-color: #10b981;
    color: #ffffff;
    border: none;
    font-weight: 700;
}}

QPushButton#PrimaryBtn:hover {{
    background-color: #059669;
}}

QPushButton#PrimaryBtn:pressed {{
    background-color: #047857;
}}

/* Warning Button (Pause) */
QPushButton#WarningBtn {{
    background-color: #f59e0b;
    color: #000000;
    border: none;
    font-weight: 700;
}}

QPushButton#WarningBtn:hover {{
    background-color: #d97706;
}}

QPushButton#WarningBtn:pressed {{
    background-color: #b45309;
}}

/* Danger Button (Stop) */
QPushButton#DangerBtn {{
    background-color: #ef4444;
    color: #ffffff;
    border: none;
    font-weight: 700;
}}

QPushButton#DangerBtn:hover {{
    background-color: #dc2626;
}}

QPushButton#DangerBtn:pressed {{
    background-color: #b91c1c;
}}

/* Secondary Highlight Button (Export & View Leads) */
QPushButton#AccentBtn {{
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    font-weight: 700;
}}

QPushButton#AccentBtn:hover {{
    background-color: #4f46e5;
}}

QPushButton#AccentBtn:pressed {{
    background-color: #4338ca;
}}

/* ========================================================
   HIGH-VISIBILITY INPUT BOXES (ALL INPUTS EXTREMELY VISIBLE)
   ======================================================== */
QLineEdit {{
    background-color: #111625;
    border: 2px solid #6366f1;
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 500;
    min-height: 28px;
}}

QLineEdit:hover {{
    border: 2px solid #818cf8;
    background-color: #151b2d;
}}

QLineEdit:focus {{
    border: 2px solid #38bdf8;
    background-color: #171f34;
}}

QSpinBox {{
    background-color: #111625;
    border: 2px solid #6366f1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 500;
    min-height: 28px;
    min-width: 90px;
}}

QSpinBox:hover {{
    border: 2px solid #818cf8;
    background-color: #151b2d;
}}

QSpinBox:focus {{
    border: 2px solid #38bdf8;
    background-color: #171f34;
}}

/* Spinbox Up/Down Controls */
QSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1.5px solid #6366f1;
    border-bottom: 1px solid #4338ca;
    background-color: #1e263d;
    border-top-right-radius: 4px;
}}

QSpinBox::up-button:hover {{
    background-color: #4338ca;
}}

QSpinBox::up-arrow {{
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #ffffff;
}}

QSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 22px;
    border-left: 1.5px solid #6366f1;
    background-color: #1e263d;
    border-bottom-right-radius: 4px;
}}

QSpinBox::down-button:hover {{
    background-color: #4338ca;
}}

QSpinBox::down-arrow {{
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #ffffff;
}}

QComboBox {{
    background-color: #111625;
    border: 2px solid #6366f1;
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    font-size: 13px;
    font-weight: 500;
    min-height: 28px;
}}

QComboBox:hover {{
    border: 2px solid #818cf8;
    background-color: #151b2d;
}}

QComboBox:focus {{
    border: 2px solid #38bdf8;
    background-color: #171f34;
}}

QComboBox::drop-down {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 26px;
    border-left: 1.5px solid #6366f1;
    background-color: #1e263d;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}}

QComboBox::drop-down:hover {{
    background-color: #4338ca;
}}

QComboBox::down-arrow {{
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #ffffff;
}}

QComboBox QAbstractItemView {{
    background-color: #111625;
    border: 2px solid #6366f1;
    color: #ffffff;
    selection-background-color: #4f46e5;
    selection-color: #ffffff;
    padding: 6px;
}}

QTextEdit, QPlainTextEdit {{
    background-color: #0b0f1c;
    border: 2px solid #6366f1;
    border-radius: 8px;
    padding: 10px 12px;
    color: #ffffff;
    font-size: 13px;
    font-family: Consolas, "Segoe UI", monospace;
}}

QTextEdit:hover, QPlainTextEdit:hover {{
    border: 2px solid #818cf8;
    background-color: #0f1527;
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid #38bdf8;
    background-color: #11182c;
}}

/* Target Input Box Specific Accent */
QTextEdit#TargetInputBox {{
    background-color: #070914;
    border: 2px solid #818cf8;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    font-family: Consolas, "Segoe UI", monospace;
    font-weight: 500;
    color: #ffffff;
}}

QLineEdit#TargetInputBox {{
    background-color: #070914;
    border: 2px solid #818cf8;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 500;
    color: #ffffff;
    min-height: 28px;
}}

QTextEdit#TargetInputBox:focus, QLineEdit#TargetInputBox:focus {{
    border: 2.5px solid #38bdf8;
    background-color: #0d1222;
}}

/* Preset Quick Action Buttons */
QPushButton#PresetBtn {{
    background-color: #1e1b4b;
    color: #e0e7ff;
    border: 1.5px solid #6366f1;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 700;
    font-size: 12px;
    min-height: 22px;
}}

QPushButton#PresetBtn:hover {{
    background-color: #3730a3;
    color: #ffffff;
    border-color: #a5b4fc;
}}

QPushButton#PresetBtn:pressed {{
    background-color: #4338ca;
}}

QPushButton#ClearBtn {{
    background-color: #27272a;
    color: #cbd5e1;
    border: 1px solid #3f3f46;
    border-radius: 6px;
    padding: 7px 12px;
    font-weight: 600;
    font-size: 12px;
    min-height: 22px;
}}

QPushButton#ClearBtn:hover {{
    background-color: #3f3f46;
    color: #ffffff;
}}

/* Target Section Title */
QLabel#TargetSectionHeader {{
    color: #a5b4fc;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QLabel#TargetSectionHelp {{
    color: #94a3b8;
    font-size: 12px;
}}

/* Data Table */
QTableWidget {{
    background-color: #16181f;
    border: 1px solid #232631;
    border-radius: 8px;
    gridline-color: #1e212b;
    color: #e2e8f0;
    alternate-background-color: #191b22;
}}

QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid #1e212b;
}}

QTableWidget::item:selected {{
    background-color: #2b304c;
    color: #818cf8;
}}

QHeaderView::section {{
    background-color: #1c1e25;
    color: #94a3b8;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #242733;
    border-bottom: 2px solid #2b2f3d;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 11px;
}}

/* Progress Bar */
QProgressBar {{
    background-color: #1e212b;
    border: 1px solid #2a2e3d;
    border-radius: 8px;
    text-align: center;
    color: #f8fafc;
    font-weight: 700;
    height: 20px;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #10b981);
    border-radius: 7px;
}}

/* CheckBoxes - Crisp & Distinct */
QCheckBox {{
    spacing: 12px;
    color: #e2e8f0;
    font-weight: 500;
    font-size: 13px;
    min-height: 26px;
}}

QCheckBox:hover {{
    color: #ffffff;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid #6366f1;
    border-radius: 4px;
    background-color: #101422;
}}

QCheckBox::indicator:hover {{
    border-color: #818cf8;
    background-color: #171e33;
}}

QCheckBox::indicator:checked {{
    background-color: #4f46e5;
    border: 2px solid #818cf8;
    image: url({check_icon});
}}

/* Radio Buttons - Clean & Distinct */
QRadioButton {{
    spacing: 10px;
    color: #e2e8f0;
    font-weight: 600;
    font-size: 13px;
    min-height: 26px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid #6366f1;
    border-radius: 10px;
    background-color: #101422;
}}

QRadioButton::indicator:hover {{
    border-color: #a5b4fc;
    background-color: #171e33;
}}

QRadioButton::indicator:checked {{
    background-color: #4f46e5;
    border: 2px solid #818cf8;
    image: url({radio_icon});
}}

/* Group Boxes */
QGroupBox {{
    border: 1.5px solid #2e3346;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 18px;
    font-weight: 700;
    color: #cbd5e1;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #a5b4fc;
    font-weight: 700;
    font-size: 12px;
}}

/* Scroll Bars */
QScrollBar:vertical {{
    background-color: #121316;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: #2b2e3b;
    min-height: 24px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #3f4457;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: #121316;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: #2b2e3b;
    min-width: 24px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #3f4457;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Activity Console */
QPlainTextEdit#LogConsole {{
    background-color: #0b0d14;
    border: 2px solid #2e3346;
    border-radius: 8px;
    color: #38bdf8;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 12px;
    padding: 8px;
}}
"""


DARK_THEME_QSS = get_dark_theme_qss()
