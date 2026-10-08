# LeadFlow Email Extractor & Intelligence Suite 🚀

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg?logo=windows)](https://www.microsoft.com/windows/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6%20Fluent-6366f1.svg?logo=qt)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, multithreaded Windows desktop application for high-throughput public contact extraction, RFC 5322 parsing, obfuscation unmasking, and lead intelligence analysis.

---

## 🌟 Key Capabilities

### 1. High-Performance Multi-Input Discovery
- **Website & Domain Deep Crawl**: Target URLs with configurable link depth (Levels 1–3) and internal link boundary confinement.
- **Search Engine Discovery**: Query DuckDuckGo and search engines dynamically filtered by Country TLD (`.uk`, `.ca`, `.ng`, `.de`, `.fr`, etc.), Industry Niche, and Executive/Role Name.
- **Bulk Domain List Ingestion**: Import `.txt` or `.csv` domain lists to process thousands of targets concurrently.

### 2. Multi-Stage Intelligence & Smart Filtering Pipeline
- **RFC 5322 & Obfuscation Parser**: Unmasks standard emails, mailto links with anchor text analysis, and obfuscated formats (e.g. `user [at] domain [dot] com`, HTML entities).
- **Honeypot & Garbage Protection**: Automatically excludes media assets (`.png`, `.webp`, `.jpg`), CMS dummy emails (`example.com`, `sentry.io`), and generic image assets incorrectly flagged as emails.
- **Executive Role Matcher**: Automatically categorizes contacts into *Founders/C-Level*, *Sales/BizDev*, *Press/Media*, *Support/Ops*, and *Personal*.
- **DNS MX & Syntax Verification**: In-memory cached MX record checks and email syntax validation.
- **In-Memory Hash Deduplication**: Zero duplicate leads across sessions.

### 3. Asynchronous Non-Blocking Engine
- Built with **`httpx` (HTTP/2 async engine)** running inside a dedicated `QThread` event loop.
- **Pause, Resume, and Stop controls** ensuring 60 FPS responsive UI without freezes.
- Configurable ethical rate limiting (100ms–3000ms jitter) and **`robots.txt` compliance**.

### 4. Enterprise Export
- One-click export to **CSV (UTF-8 BOM for native Microsoft Excel support)**, **Microsoft Excel (.xlsx)**, and **JSON**.
- Comprehensive metrics summary breakdown by role, country, and domain.

---

## 🏗 Project Architecture

```
leadflow-extractor/
├── .github/
│   └── workflows/
│       └── build-windows-exe.yml     # GitHub Actions workflow for Windows release compilation
├── assets/
│   └── icon.ico                      # Multi-resolution application icon
├── src/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main_window.py            # PyQt6 UI layout, KPI metrics & reactive state
│   │   ├── workers.py                # QThread-based asynchronous crawl worker
│   │   └── styles.py                 # Windows 11 Fluent dark theme QSS stylesheet
│   ├── core/
│   │   ├── __init__.py
│   │   ├── crawler.py                # Async HTTP/2 web request engine & rate limiting
│   │   ├── extractor.py              # Regex, DOM, and obfuscation parsers
│   │   ├── filter.py                 # TLD classifier, honeypot filters & MX verification
│   │   └── exporter.py               # CSV/XLSX/JSON export handlers
│   └── utils/
│       ├── __init__.py
│       ├── user_agents.py            # User-Agent rotation pool & browser client hints
│       └── config.py                 # Configuration schemas & persistent settings
├── build_exe.py                      # PyInstaller packaging automation script
├── generate_icon.py                  # High-resolution icon generation script
├── main.py                           # Application entry point
├── requirements.txt                  # Production dependencies
├── .gitignore                        # Git exclusion rules
├── LICENSE                           # MIT License
└── README.md                         # Product documentation
```

---

## 🚀 Quickstart & Installation

### Prerequisites
- Windows 10 / 11 (64-bit)
- Python 3.11+

### Step-by-Step Setup
1. **Clone the repository**:
   ```powershell
   git clone https://github.com/your-org/leadflow-extractor.git
   cd leadflow-extractor
   ```

2. **Create a virtual environment**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Launch the application**:
   ```powershell
   python main.py
   ```

---

## 📦 Building Standalone Windows Executable (.exe)

LeadFlow includes an automated PyInstaller packaging pipeline with hidden import resolution and asset bundling:

```powershell
python build_exe.py
```

This compiles a standalone, single-file Windows executable:
```
dist/LeadFlow-Extractor.exe
```
Flags utilized:
- `--noconsole`: Launches clean GUI without background terminal window.
- `--onefile`: Self-contained standalone binary with all DLLs bundled.
- `--icon=assets/icon.ico`: High-DPI Windows application icon.
- `--hidden-import`: Automatically resolves PyQt6, httpx, lxml, and openpyxl components.

---

## 🛡️ Ethical Usage & Legal Notice
LeadFlow Email Extractor is intended for legitimate B2B sales development, academic research, and public directory indexing. Users are responsible for complying with applicable privacy regulations (such as GDPR, CAN-SPAM, and CASL) and respecting target website terms of service and `robots.txt` directives.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

