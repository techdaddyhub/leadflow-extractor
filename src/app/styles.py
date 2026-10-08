"""
LeadFlow Intelligence Suite - Modern Fluent Dark QSS Theme
Provides Windows 11 Fluent & Material design dark styling for PyQt6.
"""

DARK_THEME_QSS = """
/* Global Application Styles */
QWidget {
    background-color: #121316;
    color: #e2e8f0;
    font-family: "Segoe UI", "Segoe UI Variable Text", system-ui, -apple-system, sans-serif;
    font-size: 13px;
    selection-background-color: #6366f1;
    selection-color: #ffffff;
}

/* Main Window */
QMainWindow {
    background-color: #0f1013;
}

/* Card / Container Panels */
QFrame#MetricCard, QFrame#PanelCard {
    background-color: #1a1c23;
    border: 1px solid #282b37;
    border-radius: 10px;
}

QFrame#MetricCard:hover {
    border: 1px solid #3d4256;
}

/* Headers and Labels */
QLabel {
    background-color: transparent;
    color: #cbd5e1;
}

QLabel#CardTitle {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel#CardValue {
    color: #f8fafc;
    font-size: 22px;
    font-weight: 700;
}

QLabel#AppTitle {
    color: #f8fafc;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.3px;
}

QLabel#AppSubtitle {
    color: #818cf8;
    font-size: 11px;
    font-weight: 600;
}

/* Tab Widget & Bar */
QTabWidget::pane {
    border: 1px solid #232631;
    background-color: #16181f;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background-color: #121316;
    color: #94a3b8;
    padding: 10px 20px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid transparent;
    font-weight: 600;
    min-width: 120px;
}

QTabBar::tab:hover {
    background-color: #1c1e24;
    color: #f1f5f9;
}

QTabBar::tab:selected {
    background-color: #16181f;
    color: #818cf8;
    border: 1px solid #232631;
    border-bottom: 2px solid #6366f1;
}

/* Buttons */
QPushButton {
    background-color: #242733;
    color: #f8fafc;
    border: 1px solid #333849;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    min-height: 18px;
}

QPushButton:hover {
    background-color: #2f3445;
    border-color: #4b526d;
}

QPushButton:pressed {
    background-color: #1e212b;
}

QPushButton:disabled {
    background-color: #17181e;
    color: #4b5563;
    border-color: #232631;
}

/* Primary Action Button (Start) */
QPushButton#PrimaryBtn {
    background-color: #10b981;
    color: #ffffff;
    border: none;
    font-weight: 700;
}

QPushButton#PrimaryBtn:hover {
    background-color: #059669;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #047857;
}

/* Warning Button (Pause) */
QPushButton#WarningBtn {
    background-color: #f59e0b;
    color: #000000;
    border: none;
    font-weight: 700;
}

QPushButton#WarningBtn:hover {
    background-color: #d97706;
}

QPushButton#WarningBtn:pressed {
    background-color: #b45309;
}

/* Danger Button (Stop) */
QPushButton#DangerBtn {
    background-color: #ef4444;
    color: #ffffff;
    border: none;
    font-weight: 700;
}

QPushButton#DangerBtn:hover {
    background-color: #dc2626;
}

QPushButton#DangerBtn:pressed {
    background-color: #b91c1c;
}

/* Secondary Highlight Button (Export) */
QPushButton#AccentBtn {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    font-weight: 700;
}

QPushButton#AccentBtn:hover {
    background-color: #4f46e5;
}

QPushButton#AccentBtn:pressed {
    background-color: #4338ca;
}

/* Line Edits & Text Areas */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {
    background-color: #1c1e24;
    border: 1px solid #2a2e3d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f8fafc;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #6366f1;
    background-color: #1f2129;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left: 1px solid #2a2e3d;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}

QComboBox QAbstractItemView {
    background-color: #1a1c23;
    border: 1px solid #2a2e3d;
    color: #f8fafc;
    selection-background-color: #6366f1;
    selection-color: #ffffff;
    padding: 4px;
}

/* Data Table */
QTableWidget {
    background-color: #16181f;
    border: 1px solid #232631;
    border-radius: 8px;
    gridline-color: #1e212b;
    color: #e2e8f0;
    alternate-background-color: #191b22;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #1e212b;
}

QTableWidget::item:selected {
    background-color: #2b304c;
    color: #818cf8;
}

QHeaderView::section {
    background-color: #1c1e25;
    color: #94a3b8;
    padding: 8px 10px;
    border: none;
    border-right: 1px solid #242733;
    border-bottom: 2px solid #2b2f3d;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 11px;
}

/* Progress Bar */
QProgressBar {
    background-color: #1e212b;
    border: 1px solid #2a2e3d;
    border-radius: 8px;
    text-align: center;
    color: #f8fafc;
    font-weight: 700;
    height: 20px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #10b981);
    border-radius: 7px;
}

/* CheckBoxes & Radio Buttons */
QCheckBox, QRadioButton {
    spacing: 8px;
    color: #cbd5e1;
    font-weight: 500;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #3d4256;
    background-color: #1c1e24;
    border-radius: 4px;
}

QRadioButton::indicator {
    border-radius: 9px;
}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: #6366f1;
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
}

/* Group Boxes */
QGroupBox {
    border: 1px solid #282b37;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: 700;
    color: #cbd5e1;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #818cf8;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #121316;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #2b2e3b;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #3f4457;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #121316;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #2b2e3b;
    min-width: 24px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #3f4457;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #0f1013;
    color: #94a3b8;
    border-top: 1px solid #1e212b;
}

/* Log Console Text Area */
QPlainTextEdit#LogConsole {
    background-color: #0c0d10;
    color: #38bdf8;
    font-family: "Consolas", "Cascadia Code", "Courier New", monospace;
    font-size: 12px;
    border: 1px solid #232631;
    border-radius: 6px;
}

/* Tooltips */
QToolTip {
    background-color: #1c1e24;
    color: #f8fafc;
    border: 1px solid #333849;
    padding: 6px 10px;
    border-radius: 4px;
}
"""

