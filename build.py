#!/usr/bin/env python3
"""
Build script
"""

import shutil
import subprocess
import sys
from pathlib import Path

# =========================
# Configuration
# =========================

VERSION = "2.0.0-alpha.1"

APP_NAME = "VCC"
CLI_ENTRY_POINT = "cli.py"
GUI_ENTRY_POINT = "gui.py"

CLI_EXECUTABLE = f"{APP_NAME}-cli-{VERSION}.exe"
GUI_EXECUTABLE = f"{APP_NAME}-gui-{VERSION}.exe"

FFMPEG_NAME = "ffmpeg.exe"

LICENSE_NAME = "LICENSE"
THIRD_PARTY_LICENSE_NAME = "LGPLv3.txt"

# =========================
# Paths
# =========================

ROOT = Path(__file__).resolve().parent
CLI_ENTRY = ROOT / CLI_ENTRY_POINT
GUI_ENTRY = ROOT / GUI_ENTRY_POINT
FFMPEG = ROOT / FFMPEG_NAME
LICENSE = ROOT / LICENSE_NAME
THIRD_PARTY_LICENSE = ROOT / "LICENSES" / THIRD_PARTY_LICENSE_NAME

DIST = ROOT / "dist"
CLI_DIST = DIST / "cli.dist"
GUI_DIST = DIST / "gui.dist"

BUILD = ROOT / "build"


def run(command):
    print("\n>", " ".join(map(str, command)))
    subprocess.run(
        command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def build_cli():
    if not CLI_ENTRY.exists():
        print(f"ERROR: {CLI_ENTRY} not found.")
        sys.exit(1)

    if not FFMPEG.exists():
        print(f"ERROR: {FFMPEG_NAME} not found")
        sys.exit(1)

        # Clean previous build.
        for path in (DIST, BUILD):
            if path.exists():
                print(f"Removing {path}")
                shutil.rmtree(path)

    DIST.mkdir(exist_ok=True)

    command = [
        "uv",
        "run",
        "nuitka",
        "--standalone",
        f"--output-filename={CLI_EXECUTABLE}",
        f"--output-dir={DIST}",
        f"--include-data-files={FFMPEG}={FFMPEG_NAME}",
        f"--include-data-files={LICENSE}={LICENSE_NAME}",
        f"--include-data-files={THIRD_PARTY_LICENSE}={THIRD_PARTY_LICENSE_NAME}",
        str(CLI_ENTRY),
    ]

    run(command)

    executable = CLI_DIST / CLI_EXECUTABLE

    if executable.exists():
        print("\n========================================")
        print("BUILD SUCCESSFUL")
        print("========================================")
        print(f"Executable: {executable}")
        print()
        print("ffmpeg.exe is bundled into the executable.")
    else:
        print("\nBuild finished, but the expected executable was not found.")
        sys.exit(1)


def build_gui():
    if not GUI_ENTRY.exists():
        print(f"ERROR: {GUI_ENTRY} not found.")
        sys.exit(1)

    if not FFMPEG.exists():
        print(f"ERROR: {FFMPEG_NAME} not found")
        sys.exit(1)

        # Clean previous build.
        for path in (DIST, BUILD):
            if path.exists():
                print(f"Removing {path}")
                shutil.rmtree(path)

    DIST.mkdir(exist_ok=True)

    command = [
        "uv",
        "run",
        "nuitka",
        "--standalone",
        "--windows-console-mode=disable",
        "--enable-plugin=pyside6",
        f"--output-filename={GUI_EXECUTABLE}",
        f"--output-dir={DIST}",
        f"--include-data-files={FFMPEG}={FFMPEG_NAME}",
        f"--include-data-files={LICENSE}={LICENSE_NAME}",
        f"--include-data-files={THIRD_PARTY_LICENSE}={THIRD_PARTY_LICENSE_NAME}",
        str(GUI_ENTRY),
    ]

    run(command)

    executable = GUI_DIST / GUI_EXECUTABLE

    if executable.exists():
        print("\n========================================")
        print("BUILD SUCCESSFUL")
        print("========================================")
        print(f"Executable: {executable}")
        print()
        print("ffmpeg.exe is bundled into the executable.")
    else:
        print("\nBuild finished, but the expected executable was not found.")
        sys.exit(1)


def main():
    build_cli()
    build_gui()


if __name__ == "__main__":
    main()
