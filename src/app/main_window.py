"""
LeadFlow Email Extractor & Intelligence Suite - Main Application Window
Full-featured PyQt6 desktop interface with reactive state management,
multithreading, live table rendering, and enterprise export capabilities.
"""

from __future__ import annotations
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QColor, QFont, QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..core.exporter import LeadExporter
from ..utils.config import (
    AppConfig,
    COMMON_COUNTRY_TLDS,
    CrawlConfig,
    CrawlMode,
    DEFAULT_COLUMNS,
    ROLE_PATTERNS,
)
from .styles import DARK_THEME_QSS
from .workers import CrawlWorker


class MainWindow(QMainWindow):
    """Primary application window for LeadFlow Suite."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LeadFlow Email Extractor & Intelligence Suite")
        self.resize(1280, 840)
        self.setMinimumSize(1040, 680)

        self.config: CrawlConfig = AppConfig.load_config()
        self.worker: Optional[CrawlWorker] = None
        self.leads_data: List[Dict[str, Any]] = []

        # Load Icon if present
        icon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._init_ui()
        self.setStyleSheet(DARK_THEME_QSS)
        self._log("INFO", "LeadFlow Engine initialized. System ready for extraction.")

    def _init_ui(self) -> None:
        """Constructs layout hierarchy."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        root_layout = QVBoxLayout(main_widget)
        root_layout.setContentsMargins(16, 14, 16, 12)
        root_layout.setSpacing(12)

        # 1. Top Header & Metrics Dashboard
        root_layout.addWidget(self._create_header_section())
        root_layout.addWidget(self._create_metrics_dashboard())

        # 2. Main Tabbed Workspace
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_target_tab(), "🎯 Target Discovery & Crawl")
        self.tab_widget.addTab(self._create_grid_tab(), "📋 Live Leads Grid")
        self.tab_widget.addTab(self._create_pipeline_tab(), "⚙️ AI & Smart Filters")
        self.tab_widget.addTab(self._create_export_tab(), "📤 Export & Intelligence")
        self.tab_widget.addTab(self._create_logs_tab(), "💻 Activity Console")
        root_layout.addWidget(self.tab_widget, stretch=1)

        # 3. Global Control Bar & Progress
        root_layout.addWidget(self._create_control_panel())

        # 4. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        self.current_url_label = QLabel("")
        self.current_url_label.setStyleSheet("color: #64748b; font-size: 11px;")
        self.status_bar.addPermanentWidget(self.current_url_label)

    # ---------------------------------------------------------
    # UI Component Builders
    # ---------------------------------------------------------
    def _create_header_section(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title & Subtitle
        v_title = QVBoxLayout()
        v_title.setSpacing(2)
        title = QLabel("LEADFLOW EMAIL EXTRACTOR & INTELLIGENCE SUITE")
        title.setObjectName("AppTitle")
        subtitle = QLabel("High-Throughput Multithreaded Public Contact Extraction • RFC 5322 Engine")
        subtitle.setObjectName("AppSubtitle")
        v_title.addWidget(title)
        v_title.addWidget(subtitle)
        layout.addLayout(v_title)

        layout.addStretch()

        # Engine Badge
        self.engine_status_badge = QLabel("STATUS: IDLE")
        self.engine_status_badge.setStyleSheet(
            "background-color: #1e293b; color: #94a3b8; padding: 6px 14px; border-radius: 6px; font-weight: 700; font-size: 11px;"
        )
        layout.addWidget(self.engine_status_badge)

        return container

    def _create_metrics_dashboard(self) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Metric 1: Leads Found
        self.card_leads = self._build_kpi_card("TOTAL LEADS FOUND", "0", "#10b981")
        # Metric 2: Rate
        self.card_rate = self._build_kpi_card("EXTRACTION RATE", "0.0 / min", "#6366f1")
        # Metric 3: Scanned Pages
        self.card_scanned = self._build_kpi_card("PAGES SCANNED", "0", "#38bdf8")
        # Metric 4: Avg Confidence
        self.card_conf = self._build_kpi_card("AVG CONFIDENCE", "0%", "#f59e0b")

        layout.addWidget(self.card_leads)
        layout.addWidget(self.card_rate)
        layout.addWidget(self.card_scanned)
        layout.addWidget(self.card_conf)

        return container

    def _build_kpi_card(self, title_text: str, default_val: str, accent_color: str) -> QFrame:
        card = QFrame()
        card.setObjectName("MetricCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        t_lbl = QLabel(title_text)
        t_lbl.setObjectName("CardTitle")

        v_lbl = QLabel(default_val)
        v_lbl.setObjectName("CardValue")
        v_lbl.setStyleSheet(f"color: {accent_color};")

        layout.addWidget(t_lbl)
        layout.addWidget(v_lbl)
        card.value_label = v_lbl  # Store ref
        return card

    def _create_control_panel(self) -> QWidget:
        container = QFrame()
        container.setObjectName("PanelCard")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Progress: 0 / 500 Leads (0%)")
        layout.addWidget(self.progress_bar)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_start = QPushButton("▶  Start Extraction")
        self.btn_start.setObjectName("PrimaryBtn")
        self.btn_start.clicked.connect(self._start_crawl)

        self.btn_pause = QPushButton("⏸  Pause")
        self.btn_pause.setObjectName("WarningBtn")
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self._toggle_pause)

        self.btn_stop = QPushButton("⏹  Stop")
        self.btn_stop.setObjectName("DangerBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_crawl)

        self.btn_clear = QPushButton("🗑  Clear Records")
        self.btn_clear.clicked.connect(self._clear_records)

        btn_row.addWidget(self.btn_start, stretch=2)
        btn_row.addWidget(self.btn_pause, stretch=1)
        btn_row.addWidget(self.btn_stop, stretch=1)
        btn_row.addWidget(self.btn_clear, stretch=1)

        layout.addLayout(btn_row)
        return container

    # ---------------------------------------------------------
    # TAB 1: Target Discovery & Setup
    # ---------------------------------------------------------
    def _create_target_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Mode Selection
        mode_box = QGroupBox("Target Input Mode")
        mode_layout = QHBoxLayout(mode_box)
        self.radio_domain = QRadioButton("Domain / Website Deep Crawl")
        self.radio_search = QRadioButton("Keyword & Query Search Engine Discovery")
        self.radio_bulk = QRadioButton("Bulk Domain List (File / Text)")
        self.radio_domain.setChecked(True)

        self.radio_domain.toggled.connect(self._on_mode_changed)
        self.radio_search.toggled.connect(self._on_mode_changed)
        self.radio_bulk.toggled.connect(self._on_mode_changed)

        mode_layout.addWidget(self.radio_domain)
        mode_layout.addWidget(self.radio_search)
        mode_layout.addWidget(self.radio_bulk)
        layout.addWidget(mode_box)

        # Stacked / Dynamic Input Area
        self.input_card = QFrame()
        self.input_card.setObjectName("PanelCard")
        self.card_layout = QVBoxLayout(self.input_card)

        # --- Sub-panel 1: Domain Crawl ---
        self.panel_domain = QWidget()
        v_dom = QVBoxLayout(self.panel_domain)
        v_dom.setContentsMargins(0, 0, 0, 0)
        v_dom.addWidget(QLabel("Target URL(s) (One per line or comma-separated):"))
        self.txt_domain_targets = QTextEdit()
        self.txt_domain_targets.setPlaceholderText(
            "Enter target websites (one per line). Examples:\n"
            "https://www.churchfinder.com\n"
            "https://saddleback.com\n"
            "https://elevationchurch.org"
        )
        self.txt_domain_targets.setMaximumHeight(100)
        v_dom.addWidget(self.txt_domain_targets)

        dom_options = QHBoxLayout()
        dom_options.addWidget(QLabel("Crawl Depth:"))
        self.spin_depth = QSpinBox()
        self.spin_depth.setRange(1, 3)
        self.spin_depth.setValue(2)
        dom_options.addWidget(self.spin_depth)

        self.chk_internal_only = QCheckBox("Restrict boundary to internal domain links only")
        self.chk_internal_only.setChecked(True)
        dom_options.addWidget(self.chk_internal_only)
        dom_options.addStretch()
        v_dom.addLayout(dom_options)

        # --- Sub-panel 2: Search Engine Discovery ---
        self.panel_search = QWidget()
        v_search = QGridLayout(self.panel_search)
        v_search.setContentsMargins(0, 0, 0, 0)
        v_search.addWidget(QLabel("Primary Keywords:"), 0, 0)
        self.edit_keywords = QLineEdit()
        self.edit_keywords.setPlaceholderText("e.g. Artificial Intelligence SaaS agency")
        v_search.addWidget(self.edit_keywords, 0, 1)

        v_search.addWidget(QLabel("Industry / Niche:"), 1, 0)
        self.edit_industry = QLineEdit()
        self.edit_industry.setPlaceholderText("e.g. Fintech, Healthcare, B2B Marketing")
        v_search.addWidget(self.edit_industry, 1, 1)

        v_search.addWidget(QLabel("Target Executive / Role:"), 2, 0)
        self.edit_role_query = QLineEdit()
        self.edit_role_query.setPlaceholderText("e.g. CEO, Founder, VP Sales")
        v_search.addWidget(self.edit_role_query, 2, 1)

        v_search.addWidget(QLabel("Country TLD Filter:"), 3, 0)
        self.combo_country = QComboBox()
        for label, val in COMMON_COUNTRY_TLDS.items():
            self.combo_country.addItem(label, val)
        v_search.addWidget(self.combo_country, 3, 1)

        # Quick Presets Row
        v_search.addWidget(QLabel("Niche Presets:"), 4, 0)
        preset_row = QHBoxLayout()
        btn_preset_pastor = QPushButton("✝️ Pastors & Churches")
        btn_preset_pastor.clicked.connect(lambda: self._apply_preset("pastors church directory", "Churches", "Pastor"))
        
        btn_preset_founder = QPushButton("🚀 Tech Founders")
        btn_preset_founder.clicked.connect(lambda: self._apply_preset("software SaaS startups", "Technology", "CEO / Founder"))
        
        btn_preset_sales = QPushButton("💼 Sales & Marketing")
        btn_preset_sales.clicked.connect(lambda: self._apply_preset("b2b marketing agency", "Marketing", "VP Sales"))

        preset_row.addWidget(btn_preset_pastor)
        preset_row.addWidget(btn_preset_founder)
        preset_row.addWidget(btn_preset_sales)
        preset_row.addStretch()
        v_search.addLayout(preset_row, 4, 1)

        # --- Sub-panel 3: Bulk Domain List ---
        self.panel_bulk = QWidget()
        v_bulk = QVBoxLayout(self.panel_bulk)
        v_bulk.setContentsMargins(0, 0, 0, 0)
        bulk_btn_row = QHBoxLayout()
        self.btn_import_file = QPushButton("📁 Import Domain TXT / CSV File...")
        self.btn_import_file.clicked.connect(self._import_bulk_file)
        self.lbl_bulk_count = QLabel("0 domains loaded")
        self.lbl_bulk_count.setStyleSheet("color: #818cf8; font-weight: 600;")
        bulk_btn_row.addWidget(self.btn_import_file)
        bulk_btn_row.addWidget(self.lbl_bulk_count)
        bulk_btn_row.addStretch()
        v_bulk.addLayout(bulk_btn_row)

        self.txt_bulk_domains = QTextEdit()
        self.txt_bulk_domains.setPlaceholderText("Paste domain list here or use import button above...\nstripe.com\nshopify.com\ngithub.com")
        self.txt_bulk_domains.setMaximumHeight(100)
        v_bulk.addWidget(self.txt_bulk_domains)

        self.card_layout.addWidget(self.panel_domain)
        self.card_layout.addWidget(self.panel_search)
        self.card_layout.addWidget(self.panel_bulk)
        self.panel_search.setVisible(False)
        self.panel_bulk.setVisible(False)

        layout.addWidget(self.input_card)

        # Extraction Capacity & Limits
        limits_box = QGroupBox("Extraction Capacity & Batch Stops")
        limits_layout = QHBoxLayout(limits_box)

        limits_layout.addWidget(QLabel("Target Batch Limit:"))
        self.spin_batch_target = QSpinBox()
        self.spin_batch_target.setRange(10, 5000)
        self.spin_batch_target.setValue(500)
        self.spin_batch_target.setSingleStep(100)
        limits_layout.addWidget(self.spin_batch_target)

        limits_layout.addSpacing(20)

        limits_layout.addWidget(QLabel("Hard Stop Ceiling (Max 5,000):"))
        self.spin_ceiling = QSpinBox()
        self.spin_ceiling.setRange(50, 5000)
        self.spin_ceiling.setValue(5000)
        self.spin_ceiling.setSingleStep(500)
        limits_layout.addWidget(self.spin_ceiling)

        limits_layout.addStretch()
        layout.addWidget(limits_box)

        layout.addStretch()
        return tab

    def _on_mode_changed(self) -> None:
        self.panel_domain.setVisible(self.radio_domain.isChecked())
        self.panel_search.setVisible(self.radio_search.isChecked())
        self.panel_bulk.setVisible(self.radio_bulk.isChecked())

    def _import_bulk_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Domain List", "", "Text & CSV Files (*.txt *.csv);;All Files (*.*)"
        )
        if not file_path:
            return

        try:
            domains: List[str] = []
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    entry = line.strip().strip(",")
                    if entry and not entry.startswith("#") and "." in entry:
                        domains.append(entry)

            self.txt_bulk_domains.setPlainText("\n".join(domains))
            self.lbl_bulk_count.setText(f"{len(domains)} domains loaded from file")
            self._log("SUCCESS", f"Loaded {len(domains)} domains from {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to read file: {e}")

    # ---------------------------------------------------------
    # TAB 2: Live Leads Grid
    # ---------------------------------------------------------
    def _create_grid_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Search / Quick Filter Bar
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("🔍 Quick Filter:"))
        self.edit_table_filter = QLineEdit()
        self.edit_table_filter.setPlaceholderText("Filter by email, domain, role, or country...")
        self.edit_table_filter.textChanged.connect(self._apply_table_filter)
        filter_bar.addWidget(self.edit_table_filter, stretch=2)

        self.lbl_record_count = QLabel("Showing 0 leads")
        self.lbl_record_count.setStyleSheet("color: #94a3b8; font-weight: 600;")
        filter_bar.addWidget(self.lbl_record_count)
        layout.addLayout(filter_bar)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(len(DEFAULT_COLUMNS))
        self.table.setHorizontalHeaderLabels(DEFAULT_COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_table_context_menu)
        self.table.doubleClicked.connect(self._on_table_double_click)

        # Set specific default widths
        self.table.setColumnWidth(0, 220)  # Email
        self.table.setColumnWidth(1, 140)  # Extracted Name
        self.table.setColumnWidth(2, 150)  # Domain
        self.table.setColumnWidth(3, 130)  # Role
        self.table.setColumnWidth(4, 120)  # Country/TLD
        self.table.setColumnWidth(5, 110)  # Confidence
        self.table.setColumnWidth(6, 200)  # Source URL
        self.table.setColumnWidth(7, 85)   # HTTP Status
        self.table.setColumnWidth(8, 140)  # Timestamp

        layout.addWidget(self.table)
        return tab

    def _show_table_context_menu(self, pos) -> None:
        menu = QMenu(self)
        action_copy_email = QAction("📋 Copy Email Address", self)
        action_copy_row = QAction("📄 Copy Full Record", self)
        action_open_url = QAction("🌐 Open Source URL in Browser", self)
        action_delete = QAction("🗑 Delete Selected Row", self)

        row = self.table.currentRow()
        if row < 0:
            return

        action_copy_email.triggered.connect(lambda: self._copy_table_cell(row, 0))
        action_copy_row.triggered.connect(lambda: self._copy_table_row(row))
        action_open_url.triggered.connect(lambda: self._open_source_url(row))
        action_delete.triggered.connect(lambda: self._delete_table_row(row))

        menu.addAction(action_copy_email)
        menu.addAction(action_copy_row)
        menu.addAction(action_open_url)
        menu.addSeparator()
        menu.addAction(action_delete)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _copy_table_cell(self, row: int, col: int) -> None:
        item = self.table.item(row, col)
        if item:
            QApplication.clipboard().setText(item.text())
            self._log("INFO", f"Copied to clipboard: {item.text()}")

    def _copy_table_row(self, row: int) -> None:
        vals = [self.table.item(row, c).text() if self.table.item(row, c) else "" for c in range(self.table.columnCount())]
        QApplication.clipboard().setText("\t".join(vals))
        self._log("INFO", "Copied full row to clipboard.")

    def _open_source_url(self, row: int) -> None:
        item = self.table.item(row, 6)
        if item and item.text().startswith("http"):
            webbrowser.open(item.text())

    def _delete_table_row(self, row: int) -> None:
        if 0 <= row < len(self.leads_data):
            self.leads_data.pop(row)
        self.table.removeRow(row)
        self._update_record_count_label()

    def _on_table_double_click(self, index) -> None:
        self._copy_table_cell(index.row(), 0)

    def _apply_table_filter(self, text: str) -> None:
        query = text.strip().lower()
        visible_count = 0
        for r in range(self.table.rowCount()):
            match = False
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item and query in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(r, not match)
            if match:
                visible_count += 1
        self.lbl_record_count.setText(f"Showing {visible_count} of {self.table.rowCount()} leads")

    def _update_record_count_label(self) -> None:
        self.lbl_record_count.setText(f"Showing {self.table.rowCount()} leads")

    # ---------------------------------------------------------
    # TAB 3: AI & Smart Filters
    # ---------------------------------------------------------
    def _create_pipeline_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Smart Extraction Filters
        filter_box = QGroupBox("Extraction & Cleaning Filters")
        v_filter = QVBoxLayout(filter_box)
        v_filter.setSpacing(10)

        self.chk_dedup = QCheckBox("In-Memory Deduplication: Prevent duplicate emails during crawl")
        self.chk_dedup.setChecked(True)
        v_filter.addWidget(self.chk_dedup)

        self.chk_garbage = QCheckBox("Garbage & Honeypot Filtering: Strip media assets (.png, .webp), dummy emails, and honeypots")
        self.chk_garbage.setChecked(True)
        v_filter.addWidget(self.chk_garbage)

        self.chk_obfuscation = QCheckBox("Obfuscation Unmasking: Decode patterns like 'user [at] domain [dot] com' and entities")
        self.chk_obfuscation.setChecked(True)
        v_filter.addWidget(self.chk_obfuscation)

        self.chk_mx = QCheckBox("Domain MX Record Validation: Perform DNS verification to check if domain receives mail")
        self.chk_mx.setChecked(False)
        v_filter.addWidget(self.chk_mx)

        layout.addWidget(filter_box)

        # Role Matcher Preferences
        roles_box = QGroupBox("Executive & Corporate Role Matcher")
        v_roles = QGridLayout(roles_box)
        self.role_checkboxes: Dict[str, QCheckBox] = {}
        row, col = 0, 0
        for role_name in ROLE_PATTERNS.keys():
            cb = QCheckBox(f"{role_name}")
            cb.setChecked(True)
            self.role_checkboxes[role_name] = cb
            v_roles.addWidget(cb, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addWidget(roles_box)

        # Ethical & Operational Safeguards
        safe_box = QGroupBox("Ethical & Operational Safeguards")
        v_safe = QGridLayout(safe_box)
        v_safe.setSpacing(12)

        self.chk_robots = QCheckBox("Respect robots.txt: Comply with site crawl restrictions")
        self.chk_robots.setChecked(True)
        v_safe.addWidget(self.chk_robots, 0, 0, 1, 2)

        v_safe.addWidget(QLabel("Request Delay Jitter (ms):"), 1, 0)
        delay_layout = QHBoxLayout()
        self.spin_delay = QSpinBox()
        self.spin_delay.setRange(100, 3000)
        self.spin_delay.setValue(400)
        self.spin_delay.setSingleStep(50)
        delay_layout.addWidget(self.spin_delay)
        delay_layout.addWidget(QLabel("ms  +"))

        self.spin_jitter = QSpinBox()
        self.spin_jitter.setRange(0, 1000)
        self.spin_jitter.setValue(200)
        self.spin_jitter.setSingleStep(50)
        delay_layout.addWidget(self.spin_jitter)
        delay_layout.addWidget(QLabel("ms random jitter"))
        delay_layout.addStretch()
        v_safe.addLayout(delay_layout, 1, 1)

        v_safe.addWidget(QLabel("User-Agent Rotation:"), 2, 0)
        self.combo_ua = QComboBox()
        self.combo_ua.addItems([
            "Rotating (Modern Browsers)",
            "Chrome Only (Windows/Mac)",
            "Firefox Only",
            "Edge Only",
        ])
        v_safe.addWidget(self.combo_ua, 2, 1)

        v_safe.addWidget(QLabel("Worker Concurrency Limit:"), 3, 0)
        self.spin_concurrency = QSpinBox()
        self.spin_concurrency.setRange(1, 20)
        self.spin_concurrency.setValue(8)
        v_safe.addWidget(self.spin_concurrency, 3, 1)

        layout.addWidget(safe_box)
        layout.addStretch()
        return tab

    # ---------------------------------------------------------
    # TAB 4: Export & Intelligence
    # ---------------------------------------------------------
    def _create_export_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        export_box = QGroupBox("One-Click Data Export")
        v_exp = QVBoxLayout(export_box)
        v_exp.setSpacing(12)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        btn_csv = QPushButton("📄 Export to CSV (.csv)")
        btn_csv.setObjectName("AccentBtn")
        btn_csv.clicked.connect(self._export_csv)

        btn_xlsx = QPushButton("📊 Export to Excel (.xlsx)")
        btn_xlsx.setObjectName("PrimaryBtn")
        btn_xlsx.clicked.connect(self._export_excel)

        btn_json = QPushButton("⚙️ Export to JSON (.json)")
        btn_json.clicked.connect(self._export_json)

        btn_copy_all = QPushButton("📋 Copy All Emails to Clipboard")
        btn_copy_all.clicked.connect(self._copy_all_emails)

        btn_row.addWidget(btn_csv)
        btn_row.addWidget(btn_xlsx)
        btn_row.addWidget(btn_json)
        btn_row.addWidget(btn_copy_all)

        v_exp.addLayout(btn_row)
        layout.addWidget(export_box)

        # Intelligence Summary Card
        summary_box = QGroupBox("Harvested Intelligence Summary")
        v_sum = QVBoxLayout(summary_box)
        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        self.txt_summary.setPlaceholderText("Extraction statistics and role distribution will populate here after crawling...")
        v_sum.addWidget(self.txt_summary)

        layout.addWidget(summary_box)
        return tab

    def _export_csv(self) -> None:
        if not self.leads_data:
            QMessageBox.information(self, "No Data", "No leads to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Leads as CSV", f"LeadFlow_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "CSV Files (*.csv)"
        )
        if file_path:
            try:
                res = LeadExporter.to_csv(self.leads_data, file_path)
                self._log("SUCCESS", f"Exported {len(self.leads_data)} records to CSV: {res}")
                QMessageBox.information(self, "Export Complete", f"Successfully exported {len(self.leads_data)} records to CSV!\n\n{res}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Error exporting CSV: {e}")

    def _export_excel(self) -> None:
        if not self.leads_data:
            QMessageBox.information(self, "No Data", "No leads to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Leads as Excel Workbook", f"LeadFlow_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", "Excel Files (*.xlsx)"
        )
        if file_path:
            try:
                res = LeadExporter.to_excel(self.leads_data, file_path)
                self._log("SUCCESS", f"Exported {len(self.leads_data)} records to Excel: {res}")
                QMessageBox.information(self, "Export Complete", f"Successfully exported {len(self.leads_data)} records to Excel!\n\n{res}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Error exporting Excel: {e}")

    def _export_json(self) -> None:
        if not self.leads_data:
            QMessageBox.information(self, "No Data", "No leads to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Leads as JSON", f"LeadFlow_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "JSON Files (*.json)"
        )
        if file_path:
            try:
                res = LeadExporter.to_json(self.leads_data, file_path)
                self._log("SUCCESS", f"Exported {len(self.leads_data)} records to JSON: {res}")
                QMessageBox.information(self, "Export Complete", f"Successfully exported {len(self.leads_data)} records to JSON!\n\n{res}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Error exporting JSON: {e}")

    def _copy_all_emails(self) -> None:
        if not self.leads_data:
            QMessageBox.information(self, "No Data", "No leads available.")
            return

        emails = [r["email"] for r in self.leads_data if "email" in r]
        unique_emails = list(dict.fromkeys(emails))
        QApplication.clipboard().setText("\n".join(unique_emails))
        self._log("SUCCESS", f"Copied {len(unique_emails)} unique email addresses to clipboard.")
        QMessageBox.information(self, "Clipboard", f"Copied {len(unique_emails)} email addresses to clipboard!")

    def _update_intelligence_summary(self) -> None:
        total = len(self.leads_data)
        if total == 0:
            self.txt_summary.setPlainText("No data available.")
            return

        roles: Dict[str, int] = {}
        countries: Dict[str, int] = {}
        domains: Dict[str, int] = {}

        for lead in self.leads_data:
            r = lead.get("role", "Unknown")
            roles[r] = roles.get(r, 0) + 1

            c = lead.get("country_tld", "Unknown")
            countries[c] = countries.get(c, 0) + 1

            d = lead.get("domain", "Unknown")
            domains[d] = domains.get(d, 0) + 1

        lines = [
            f"=== LEADFLOW HARVEST INTELLIGENCE REPORT ===",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Validated Leads: {total}",
            f"Unique Domains Harvested: {len(domains)}",
            "",
            "--- ROLE DISTRIBUTION ---"
        ]
        for role, count in sorted(roles.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total) * 100
            lines.append(f"  • {role}: {count} ({pct:.1f}%)")

        lines.append("")
        lines.append("--- TOP DOMAIN SOURCES ---")
        for dom, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
            lines.append(f"  • {dom}: {count} leads")

        lines.append("")
        lines.append("--- GEOGRAPHIC / TLD DISTRIBUTION ---")
        for ctry, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:8]:
            pct = (count / total) * 100
            lines.append(f"  • {ctry}: {count} ({pct:.1f}%)")

        self.txt_summary.setPlainText("\n".join(lines))

    # ---------------------------------------------------------
    # TAB 5: Activity Console
    # ---------------------------------------------------------
    def _create_logs_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Live System Output & Diagnostics:"))
        top_row.addStretch()

        btn_clear_log = QPushButton("Clear Console")
        btn_clear_log.clicked.connect(lambda: self.console.clear())
        top_row.addWidget(btn_clear_log)

        layout.addLayout(top_row)

        self.console = QPlainTextEdit()
        self.console.setObjectName("LogConsole")
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        return tab

    def _log(self, level: str, message: str) -> None:
        now = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{now}] [{level}]"
        self.console.appendPlainText(f"{prefix} {message}")
        # Scroll to bottom
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    # ---------------------------------------------------------
    # Crawl Execution & Reactive State Handlers
    # ---------------------------------------------------------
    def _compile_current_config(self) -> CrawlConfig:
        config = CrawlConfig()

        if self.radio_search.isChecked():
            config.mode = CrawlMode.KEYWORD_SEARCH
            config.search_query = self.edit_keywords.text().strip()
            config.industry_niche = self.edit_industry.text().strip()
            config.role_query = self.edit_role_query.text().strip()
            config.country_tld = self.combo_country.currentData() or ""
        elif self.radio_bulk.isChecked():
            config.mode = CrawlMode.BULK_LIST
            raw = self.txt_bulk_domains.toPlainText()
            config.target_urls = [line.strip() for line in raw.splitlines() if line.strip()]
        else:
            config.mode = CrawlMode.DOMAIN_CRAWL
            raw = self.txt_domain_targets.toPlainText()
            config.target_urls = [u.strip() for u in raw.splitlines() if u.strip()]

        config.max_depth = self.spin_depth.value()
        config.batch_target = self.spin_batch_target.value()
        config.hard_stop_ceiling = self.spin_ceiling.value()

        config.follow_internal_only = self.chk_internal_only.isChecked()
        config.enable_deduplication = self.chk_dedup.isChecked()
        config.enable_garbage_filtering = self.chk_garbage.isChecked()
        config.enable_obfuscation_decoding = self.chk_obfuscation.isChecked()
        config.enable_mx_validation = self.chk_mx.isChecked()

        config.respect_robots_txt = self.chk_robots.isChecked()
        config.request_delay_ms = self.spin_delay.value()
        config.jitter_ms = self.spin_jitter.value()
        config.concurrency_limit = self.spin_concurrency.value()
        config.user_agent_mode = self.combo_ua.currentText()

        selected_roles = [k for k, cb in self.role_checkboxes.items() if cb.isChecked()]
        config.selected_roles = selected_roles

        return config

    def _apply_preset(self, keywords: str, niche: str, role: str) -> None:
        self.edit_keywords.setText(keywords)
        self.edit_industry.setText(niche)
        self.edit_role_query.setText(role)
        self._log("INFO", f"Applied search preset: '{keywords}' (Role: {role})")

    def _start_crawl(self) -> None:
        cfg = self._compile_current_config()

        # Sanity check targets
        if cfg.mode == CrawlMode.DOMAIN_CRAWL:
            if not cfg.target_urls:
                QMessageBox.warning(self, "Missing Target", "Please specify at least one target website URL.\n\nExample:\nhttps://www.churchfinder.com\nhttps://saddleback.com")
                return
            if all("example.com" in u.lower() for u in cfg.target_urls):
                QMessageBox.information(
                    self,
                    "Placeholder Domain Notice",
                    "'example.com' is an empty reserved domain with no contact information.\n\n"
                    "Please enter real websites (such as church, business, agency, or directory URLs) to extract leads."
                )
                return

        if cfg.mode == CrawlMode.KEYWORD_SEARCH and not cfg.search_query:
            QMessageBox.warning(self, "Missing Query", "Please specify search keywords for discovery (or click a Niche Preset).")
            return
        if cfg.mode == CrawlMode.BULK_LIST and not cfg.target_urls:
            QMessageBox.warning(self, "Missing Domain List", "Please load or enter at least one target domain.")
            return

        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_pause.setText("⏸  Pause")
        self.btn_stop.setEnabled(True)

        self.worker = CrawlWorker(cfg, self)
        self.worker.lead_found.connect(self._handle_lead_found)
        self.worker.progress_updated.connect(self._handle_progress_update)
        self.worker.log_message.connect(self._log)
        self.worker.status_changed.connect(self._handle_status_change)
        self.worker.finished_crawl.connect(self._handle_crawl_finished)
        self.worker.error_occurred.connect(self._handle_worker_error)

        self.worker.start()
        self._log("INFO", f"Extraction initiated. Mode: {cfg.mode.value} | Batch Target: {cfg.batch_target}")

    def _toggle_pause(self) -> None:
        if not self.worker:
            return
        if self.worker.is_paused:
            self.worker.resume()
            self.btn_pause.setText("⏸  Pause")
        else:
            self.worker.pause()
            self.btn_pause.setText("▶  Resume")

    def _stop_crawl(self) -> None:
        if self.worker:
            self.worker.stop()
            self.btn_stop.setEnabled(False)

    def _clear_records(self) -> None:
        if self.leads_data:
            confirm = QMessageBox.question(
                self, "Confirm Clear", "Clear all scraped leads from the session data grid?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

        self.leads_data.clear()
        self.table.setRowCount(0)
        self._update_record_count_label()
        self.card_leads.value_label.setText("0")
        self.card_rate.value_label.setText("0.0 / min")
        self.card_conf.value_label.setText("0%")
        self.txt_summary.clear()
        self.progress_bar.setValue(0)
        self._log("INFO", "Data grid reset.")

    def _handle_lead_found(self, lead_dict: Dict[str, Any]) -> None:
        """Appends new lead row to table grid reactively."""
        self.leads_data.append(lead_dict)

        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)

        # Columns: Email, Name, Domain, Role, Country/TLD, Confidence, Source URL, Status, Timestamp
        items = [
            lead_dict.get("email", ""),
            lead_dict.get("extracted_name", ""),
            lead_dict.get("domain", ""),
            lead_dict.get("role", ""),
            lead_dict.get("country_tld", ""),
            f"{lead_dict.get('confidence_score', 0)}%",
            lead_dict.get("source_url", ""),
            str(lead_dict.get("http_status", "")),
            lead_dict.get("timestamp", ""),
        ]

        for col_idx, text in enumerate(items):
            item = QTableWidgetItem(text)
            # Center specific columns
            if col_idx in [3, 4, 5, 7]:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if col_idx == 0:
                item.setForeground(QColor("#818cf8"))
                item.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
            elif col_idx == 5:
                # Color code confidence
                score = lead_dict.get("confidence_score", 0)
                if score >= 85:
                    item.setForeground(QColor("#10b981"))
                elif score >= 70:
                    item.setForeground(QColor("#38bdf8"))
                else:
                    item.setForeground(QColor("#f59e0b"))

            self.table.setItem(row_idx, col_idx, item)

        self._update_record_count_label()

        # Update average confidence KPI
        conf_scores = [d.get("confidence_score", 0) for d in self.leads_data]
        if conf_scores:
            avg_conf = sum(conf_scores) / len(conf_scores)
            self.card_conf.value_label.setText(f"{avg_conf:.0f}%")

    def _handle_progress_update(self, stats: Dict[str, Any]) -> None:
        leads_count = stats.get("leads_count", 0)
        scanned_count = stats.get("scanned_count", 0)
        rate = stats.get("rate", 0.0)
        current_url = stats.get("current_url", "")

        # Update KPI cards
        self.card_leads.value_label.setText(str(leads_count))
        self.card_scanned.value_label.setText(str(scanned_count))
        self.card_rate.value_label.setText(f"{rate:.1f} / min")

        # Update Progress Bar
        batch_target = self.spin_batch_target.value()
        pct = min(100, int((leads_count / max(1, batch_target)) * 100))
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"Batch Progress: {leads_count} / {batch_target} Leads ({pct}%)")

        # Status label
        self.current_url_label.setText(f"Crawling: {current_url[:75]}..." if len(current_url) > 75 else f"Crawling: {current_url}")

    def _handle_status_change(self, status_text: str) -> None:
        self.status_label.setText(f"Worker: {status_text}")
        if status_text == "Running":
            self.engine_status_badge.setText("STATUS: ACTIVE")
            self.engine_status_badge.setStyleSheet(
                "background-color: #064e3b; color: #34d399; padding: 6px 14px; border-radius: 6px; font-weight: 700; font-size: 11px;"
            )
        elif status_text == "Paused":
            self.engine_status_badge.setText("STATUS: PAUSED")
            self.engine_status_badge.setStyleSheet(
                "background-color: #78350f; color: #fbbf24; padding: 6px 14px; border-radius: 6px; font-weight: 700; font-size: 11px;"
            )
        else:
            self.engine_status_badge.setText(f"STATUS: {status_text.upper()}")
            self.engine_status_badge.setStyleSheet(
                "background-color: #1e293b; color: #94a3b8; padding: 6px 14px; border-radius: 6px; font-weight: 700; font-size: 11px;"
            )

    def _handle_crawl_finished(self) -> None:
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.current_url_label.setText("")
        self._update_intelligence_summary()
        self._log("INFO", "Crawl worker finished.")

    def _handle_worker_error(self, error_msg: str) -> None:
        self._log("ERROR", f"Worker error: {error_msg}")
        QMessageBox.warning(self, "Worker Notice", f"An error occurred during extraction:\n{error_msg}")

