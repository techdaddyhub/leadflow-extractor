"""
LeadFlow Email Extractor & Intelligence Suite - PyInstaller Build Automation Script
Compiles a standalone, single-executable Windows application (.exe) with embedded assets.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def build():
    root_dir = Path(__file__).resolve().parent
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    icon_file = root_dir / "assets" / "icon.ico"
    entry_point = root_dir / "main.py"

    print("=" * 65)
    print("  LeadFlow Intelligence Suite - Windows Packaging Engine")
    print("=" * 65)

    if not entry_point.exists():
        print(f"[ERROR] Entry point {entry_point} not found!")
        sys.exit(1)

    # Clean existing builds
    if dist_dir.exists():
        print("[INFO] Cleaning prior dist/ directory...")
        shutil.rmtree(dist_dir, ignore_errors=True)
    if build_dir.exists():
        print("[INFO] Cleaning prior build/ directory...")
        shutil.rmtree(build_dir, ignore_errors=True)

    # Base PyInstaller command arguments
    pyinstaller_args = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=LeadFlow-Extractor",
        "--noconsole",
        "--onefile",
        "--clean",
    ]

    # Add icon if available
    if icon_file.exists():
        pyinstaller_args.append(f"--icon={icon_file}")
        # Add assets folder to bundle
        sep = ";" if sys.platform == "win32" else ":"
        pyinstaller_args.append(f"--add-data={icon_file}{sep}assets")

    # Add hidden imports
    hidden_imports = [
        "PyQt6",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "PyQt6.sip",
        "httpx",
        "httpcore",
        "h2",
        "hpack",
        "hyperframe",
        "aiohttp",
        "bs4",
        "lxml",
        "email_validator",
        "tldextract",
        "dns",
        "dns.resolver",
        "pandas",
        "openpyxl",
        "qasync",
    ]

    for hi in hidden_imports:
        pyinstaller_args.append(f"--hidden-import={hi}")

    # Add target entrypoint
    pyinstaller_args.append(str(entry_point))

    print(f"[INFO] Invoking PyInstaller for {entry_point.name}...")
    print(f"[INFO] Command: {' '.join(pyinstaller_args)}\n")

    result = subprocess.run(pyinstaller_args, cwd=str(root_dir))
    if result.returncode != 0:
        print("\n[ERROR] Build failed with return code:", result.returncode)
        sys.exit(result.returncode)

    exe_path = dist_dir / "LeadFlow-Extractor.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 65)
        print("  BUILD SUCCESSFUL!")
        print(f"  Binary: {exe_path}")
        print(f"  Size:   {size_mb:.2f} MB")
        print("=" * 65)
    else:
        print("[WARNING] Executable was not found in dist directory.")


if __name__ == "__main__":
    build()

