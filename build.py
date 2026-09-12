#!/usr/bin/env python3
"""
Build script
"""

import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
import zipfile


def get_version():
    with open(Path(__file__).parent / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


__version__ = get_version()

# =========================
# Configuration
# =========================

APP_NAME = "VCC"
CLI_ENTRY_POINT = "cli.py"
GUI_ENTRY_POINT = "gui.py"

CLI_NAME = f"{APP_NAME}-cli-{__version__}"
CLI_NAME_FFMPEG = f"{APP_NAME}-cli-FFMPEG-{__version__}"
GUI_NAME = f"{APP_NAME}-gui-{__version__}"
GUI_NAME_FFMPEG = f"{APP_NAME}-gui-FFMPEG-{__version__}"

FFMPEG_NAME = "ffmpeg.exe"

LICENSE_NAME = "LICENSE"
THIRD_PARTY_LICENSE_NAME = "LGPLv3.txt"

# =========================
# Paths
# =========================

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
BIN = ROOT / "bin"

CLI_ENTRY = SRC / CLI_ENTRY_POINT
GUI_ENTRY = SRC / GUI_ENTRY_POINT
FFMPEG = BIN / FFMPEG_NAME
LICENSE = ROOT / LICENSE_NAME
THIRD_PARTY_LICENSE = ROOT / "LICENSES" / THIRD_PARTY_LICENSE_NAME
VERSION_FILE = SRC / "VERSION"

BUILD = ROOT / "build"
DIST = ROOT / "dist"
CLI_BUILD_DIST = BUILD / "cli.dist"
GUI_BUILD_DIST = BUILD / "gui.dist"

CLI_DIST = DIST / CLI_NAME
GUI_DIST = DIST / GUI_NAME

CLI_ZIP = DIST / (CLI_NAME + ".zip")
CLI_ZIP_FFMPEG = DIST / (CLI_NAME_FFMPEG + ".zip")
GUI_ZIP = DIST / (GUI_NAME + ".zip")
GUI_ZIP_FFMPEG = DIST / (GUI_NAME_FFMPEG + ".zip")

def run(command):
    print("\n>", " ".join(map(str, command)))
    process = subprocess.Popen(command, text=False)
    return process.wait()


def build_cli(include_ffmpeg: bool = True):
    if not CLI_ENTRY.exists():
        print(f"ERROR: {CLI_ENTRY} not found.")
        sys.exit(1)

    if not FFMPEG.exists():
        print(f"ERROR: {FFMPEG_NAME} not found")
        sys.exit(1)

    for path in BUILD.iterdir():
        if path.name.startswith("cli"):
            print("Removing", path)
            shutil.rmtree(path)

    BUILD.mkdir(exist_ok=True)

    command = [
        "uv",
        "run",
        "nuitka",
        "--standalone",
        f"--output-filename={CLI_NAME}.exe",
        f"--output-dir={BUILD}",
    ]

    if include_ffmpeg:
        command += [f"--include-data-files={FFMPEG}={FFMPEG_NAME}"]

    command += [
        f"--include-data-files={LICENSE}={LICENSE_NAME}",
        f"--include-data-files={THIRD_PARTY_LICENSE}={THIRD_PARTY_LICENSE_NAME}",
        f"--include-data-files={VERSION_FILE}=VERSION",
        str(CLI_ENTRY),
    ]

    code = run(command)
    if code:
        print("Nuitka failed")
        sys.exit(1)

    CLI_DIST.mkdir(exist_ok=True)

    shutil.copytree(CLI_BUILD_DIST, CLI_DIST, dirs_exist_ok=True)

    zip_file = CLI_ZIP_FFMPEG if include_ffmpeg else CLI_ZIP

    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for path in CLI_BUILD_DIST.rglob("*"):
            if path.is_file():
                # Store paths relative to the source directory
                zipf.write(path, path.relative_to(CLI_BUILD_DIST))


def build_gui(include_ffmpeg: bool = True):
    if not GUI_ENTRY.exists():
        print(f"ERROR: {GUI_ENTRY} not found.")
        sys.exit(1)

    if not FFMPEG.exists():
        print(f"ERROR: {FFMPEG_NAME} not found")
        sys.exit(1)

    for path in BUILD.iterdir():
        if path.name.startswith("gui"):
            print("Removing", path)
            shutil.rmtree(path)

    BUILD.mkdir(exist_ok=True)

    command = [
        "uv",
        "run",
        "nuitka",
        "--standalone",
        "--windows-console-mode=disable",
        "--enable-plugin=pyside6",
        f"--output-filename={GUI_NAME}.exe",
        f"--output-dir={BUILD}",
    ]

    if include_ffmpeg:
        command += [
            f"--include-data-files={FFMPEG}={FFMPEG_NAME}",
        ]

    command += [
        f"--include-data-files={LICENSE}={LICENSE_NAME}",
        f"--include-data-files={THIRD_PARTY_LICENSE}={THIRD_PARTY_LICENSE_NAME}",
        f"--include-data-files={VERSION_FILE}=VERSION",
        str(GUI_ENTRY),
    ]

    code = run(command)
    if code:
        print("Nuitka failed")
        sys.exit(1)

    GUI_DIST.mkdir(exist_ok=True)

    shutil.copytree(GUI_BUILD_DIST, GUI_DIST, dirs_exist_ok=True)

    zip_file = GUI_ZIP_FFMPEG if include_ffmpeg else GUI_ZIP

    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for path in GUI_BUILD_DIST.rglob("*"):
            if path.is_file():
                # Store paths relative to the source directory
                zipf.write(path, path.relative_to(GUI_BUILD_DIST))


def main():
    build_cli()
    build_cli(include_ffmpeg=False)
    build_gui()
    build_gui(include_ffmpeg=False)


if __name__ == "__main__":
    main()
