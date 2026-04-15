#!/usr/bin/env python3
"""
install.py — ads-mcp-connector cross-platform installer

Works on Mac, Linux, and Windows. Pure Python stdlib — no dependencies needed.

Mac / Linux:
  curl -fsSL https://raw.githubusercontent.com/benheis/ads-mcp-connector/main/install.py | python3

Windows (Command Prompt or PowerShell):
  curl -fsSL https://raw.githubusercontent.com/benheis/ads-mcp-connector/main/install.py | python
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# ─── Platform detection ───────────────────────────────────────────────────────

IS_WINDOWS = sys.platform == "win32"
IS_MAC     = sys.platform == "darwin"

# ─── Colors ───────────────────────────────────────────────────────────────────

def _enable_windows_ansi():
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass  # older Windows — colors won't show but script still runs fine

if IS_WINDOWS:
    _enable_windows_ansi()

BOLD   = "\033[1m"
GREEN  = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN   = "\033[0;36m"
RED    = "\033[0;31m"
RESET  = "\033[0m"

def info(msg: str):    print(f"{CYAN}[info]{RESET}  {msg}")
def success(msg: str): print(f"{GREEN}[done]{RESET}  {msg}")
def warn(msg: str):    print(f"{YELLOW}[warn]{RESET}  {msg}")
def error(msg: str):   print(f"{RED}[error]{RESET} {msg}")

# ─── Banner ───────────────────────────────────────────────────────────────────

print()
print(f"  {BOLD}ads-mcp-connector{RESET}")
print(f"  Connect Claude Code to Meta Ads + Google Ads")
print(f"  {'─' * 45}")
print()

# ─── Step 1: Python version check ────────────────────────────────────────────

info("Checking Python version...")

if sys.version_info < (3, 10):
    error(f"Python 3.10 or newer is required (you have {sys.version.split()[0]}).")
    print()
    print("  Download it free at: https://www.python.org/downloads/")
    print("  It takes about 3 minutes to install.")
    print("  Then run this installer again.")
    print()
    sys.exit(1)

success(f"Python found: {sys.version.split()[0]}")

# ─── Step 2: Install directory ────────────────────────────────────────────────

DEFAULT_INSTALL_DIR = Path.home() / "ads-mcp-connector"

print()
print(f"  {BOLD}Where should ads-mcp-connector be installed?{RESET}")
print(f"  Default: {DEFAULT_INSTALL_DIR}")
print(f"  Press Enter to use the default, or type a different path.")
print()

try:
    user_input = input("  Install path: ").strip()
except EOFError:
    # Running non-interactively (e.g. piped) — use default
    user_input = ""
    print()

INSTALL_DIR = Path(user_input).expanduser() if user_input else DEFAULT_INSTALL_DIR
if not str(INSTALL_DIR).strip():
    INSTALL_DIR = DEFAULT_INSTALL_DIR

print()
info(f"Installing to: {INSTALL_DIR}")

# ─── Step 2b: Platform selection ─────────────────────────────────────────────

print()
print(f"  {BOLD}Which AI tool are you using?{RESET}")
print()
print(f"  \u2460  Claude Code")
print(f"  \u2461  Claude Desktop / Cowork")
print(f"  \u2462  Cursor")
print(f"  \u2463  All of the above")
print()

PLATFORM_CHOICE = ""
while not PLATFORM_CHOICE:
    try:
        raw = input("  Enter 1, 2, 3, or 4: ").strip()
    except EOFError:
        raw = "1"
    if raw in ("1", "2", "3", "4"):
        PLATFORM_CHOICE = raw
    else:
        print(f"  {YELLOW}Please enter 1, 2, 3, or 4.{RESET}")

_labels = {"1": "Claude Code", "2": "Claude Desktop / Cowork", "3": "Cursor", "4": "all tools"}
print()
info(f"Installing for {_labels[PLATFORM_CHOICE]}")

# ─── Step 3: Clone or update repo ────────────────────────────────────────────

REPO_URL = "https://github.com/benheis/ads-mcp-connector.git"
ZIP_URL  = "https://github.com/benheis/ads-mcp-connector/archive/refs/heads/main.zip"

INSTALL_DIR.parent.mkdir(parents=True, exist_ok=True)

if (INSTALL_DIR / ".git").is_dir():
    info("Found existing installation — updating...")
    subprocess.run(["git", "-C", str(INSTALL_DIR), "pull", "--quiet"], check=True)
    success("Updated to latest version")
elif (INSTALL_DIR / "server.py").exists():
    success(f"Source files found at {INSTALL_DIR}")
else:
    git_available = subprocess.run(
        ["git", "--version"], capture_output=True
    ).returncode == 0

    if git_available:
        info("Downloading ads-mcp-connector...")
        subprocess.run(["git", "clone", "--quiet", REPO_URL, str(INSTALL_DIR)], check=True)
        success(f"Downloaded to {INSTALL_DIR}")
    else:
        warn("git not found — downloading zip instead...")
        import urllib.request
        INSTALL_DIR.mkdir(parents=True, exist_ok=True)
        tmp_zip = Path(tempfile.mktemp(suffix=".zip"))
        urllib.request.urlretrieve(ZIP_URL, tmp_zip)
        with zipfile.ZipFile(tmp_zip) as zf:
            for member in zf.namelist():
                parts = Path(member).parts
                if len(parts) > 1:
                    target = INSTALL_DIR / Path(*parts[1:])
                    if member.endswith("/"):
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(zf.read(member))
        tmp_zip.unlink(missing_ok=True)
        success(f"Downloaded and extracted to {INSTALL_DIR}")

# ─── Step 4: Virtual environment ─────────────────────────────────────────────

VENV_DIR = INSTALL_DIR / "venv"
VENV_PYTHON = (
    VENV_DIR / "Scripts" / "python.exe" if IS_WINDOWS
    else VENV_DIR / "bin" / "python"
)

if not VENV_DIR.exists():
    info("Creating Python environment...")
    print("  (Think of this as a dedicated workspace just for this tool —")
    print("   it keeps everything isolated and tidy.)")
    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    success("Python environment created")
else:
    success("Python environment already exists")

# ─── Step 5: Install dependencies ────────────────────────────────────────────

info("Installing dependencies...")
subprocess.run(
    [str(VENV_PYTHON), "-m", "pip", "install", "--quiet", "--upgrade", "pip"],
    check=True,
)
subprocess.run(
    [str(VENV_PYTHON), "-m", "pip", "install", "--quiet", "-r",
     str(INSTALL_DIR / "requirements.txt")],
    check=True,
)
success("Dependencies installed")

# ─── Step 6: Copy .env.example → .env ────────────────────────────────────────

ENV_FILE    = INSTALL_DIR / ".env"
ENV_EXAMPLE = INSTALL_DIR / ".env.example"

if not ENV_FILE.exists():
    shutil.copy(ENV_EXAMPLE, ENV_FILE)
    success(f"Created credentials file at {ENV_FILE}")
else:
    success("Credentials file already exists (not overwritten)")

# ─── Step 7: Platform paths ───────────────────────────────────────────────────

HOME = Path.home()

if IS_WINDOWS:
    _appdata = Path(os.environ.get("APPDATA", HOME / "AppData" / "Roaming"))
    CLAUDE_SETTINGS     = HOME / ".claude" / "settings.json"
    CLAUDE_DESKTOP      = _appdata / "Claude" / "claude_desktop_config.json"
    CURSOR_CONFIG       = _appdata / "Cursor" / "mcp.json"
elif IS_MAC:
    CLAUDE_SETTINGS     = HOME / ".claude" / "settings.json"
    CLAUDE_DESKTOP      = HOME / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    CURSOR_CONFIG       = HOME / ".cursor" / "mcp.json"
else:  # Linux
    CLAUDE_SETTINGS     = HOME / ".claude" / "settings.json"
    CLAUDE_DESKTOP      = HOME / ".config" / "Claude" / "claude_desktop_config.json"
    CURSOR_CONFIG       = HOME / ".cursor" / "mcp.json"

CLAUDE_SKILLS_DIR = HOME / ".claude" / "skills" / "ads-connect"

# ─── Step 8: Register MCP server ─────────────────────────────────────────────

def register_mcp(config_path: Path, label: str) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    data.setdefault("mcpServers", {})
    data["mcpServers"]["ads-mcp-connector"] = {
        "command": str(VENV_PYTHON),
        "args": [str(INSTALL_DIR / "server.py")],
        "env": {},
    }
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    success(f"Registered with {label}")


if PLATFORM_CHOICE in ("1", "4"):
    register_mcp(CLAUDE_SETTINGS, "Claude Code (~/.claude/settings.json)")
if PLATFORM_CHOICE in ("2", "4"):
    register_mcp(CLAUDE_DESKTOP, "Claude Desktop / Cowork")
if PLATFORM_CHOICE in ("3", "4"):
    register_mcp(CURSOR_CONFIG, "Cursor")

# ─── Step 9: Install Claude skill ────────────────────────────────────────────

if PLATFORM_CHOICE in ("1", "4"):
    skill_src = INSTALL_DIR / "SKILL.md"
    if skill_src.exists():
        CLAUDE_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(skill_src, CLAUDE_SKILLS_DIR / "SKILL.md")
        success("Installed /ads-connect skill to ~/.claude/skills/")
    else:
        warn("SKILL.md not found — skill not installed")

# ─── Step 10: Pre-commit security hook ───────────────────────────────────────

GIT_HOOKS_DIR = INSTALL_DIR / ".git" / "hooks"
HOOK_SOURCE   = INSTALL_DIR / "hooks" / "pre-commit"

if GIT_HOOKS_DIR.is_dir() and HOOK_SOURCE.exists():
    dest = GIT_HOOKS_DIR / "pre-commit"
    shutil.copy(HOOK_SOURCE, dest)
    if not IS_WINDOWS:
        dest.chmod(0o755)
    success("Security hook installed (scans for API keys before every commit)")
else:
    warn("No .git directory found — skipping security hook.")
    print("  If you connect this to GitHub later, run install.py")
    print("  again to install the security hook.")

# ─── Step 11: Connection status ──────────────────────────────────────────────

print()
subprocess.run(
    [str(VENV_PYTHON), str(INSTALL_DIR / "auth_check.py"),
     "--platform", PLATFORM_CHOICE]
)

# ─── Done ─────────────────────────────────────────────────────────────────────

_DIV = "━" * 49

print()
print(_DIV)
print()
print(f"  {BOLD}ads-mcp-connector is installed.{RESET}")
print()
print("  Your ad accounts are not connected yet —")
print("  the next step is to authenticate.")
print("  Here is exactly how to do that in your tool.")
print()
print(_DIV)

# ── Claude Code ───────────────────────────────────────────────────────────────
if PLATFORM_CHOICE in ("1", "4"):
    print()
    print(f"  {BOLD}{CYAN}CLAUDE CODE{RESET}")
    print()
    print("  1. Open a new terminal window")
    if IS_WINDOWS:
        print("     (Search \"Command Prompt\" in the Start menu)")
    else:
        print("     (Press Cmd+Space and type Terminal)")
    print()
    print("  2. Type this and press Enter:")
    print(f"     {CYAN}claude{RESET}")
    print()
    print("  3. Once Claude Code opens, type:")
    print(f"     {CYAN}/ads-connect{RESET}")
    print()
    print("  The skill will walk you through connecting")
    print("  Meta Ads and/or Google Ads step by step.")
    print("  It takes about 5-15 minutes depending")
    print("  on which platforms you're setting up.")

# ── Claude Desktop / Cowork ───────────────────────────────────────────────────
if PLATFORM_CHOICE in ("2", "4"):
    if PLATFORM_CHOICE == "4":
        print(f"  {'─' * 45}")
    print()
    print(f"  {BOLD}{CYAN}CLAUDE DESKTOP / COWORK{RESET}")
    print()
    print("  1. Quit Claude Desktop completely")
    if IS_WINDOWS:
        print("     (Right-click its icon in the taskbar → Quit)")
    else:
        print("     (Menu bar → Quit, or Cmd+Q)")
    print("     This is required — the MCP connector")
    print("     only loads on startup.")
    print()
    print("  2. Reopen Claude Desktop")
    print()
    print("  3. Start a new Cowork task and type:")
    print(f"     {CYAN}Connect my Meta Ads account{RESET}")
    print("     or")
    print(f"     {CYAN}Connect my Google Ads account{RESET}")
    print()
    print("  Claude will guide you through the setup.")

# ── Cursor ────────────────────────────────────────────────────────────────────
if PLATFORM_CHOICE in ("3", "4"):
    if PLATFORM_CHOICE == "4":
        print(f"  {'─' * 45}")
    print()
    print(f"  {BOLD}{CYAN}CURSOR{RESET}")
    print()
    print("  1. Quit Cursor completely")
    if IS_WINDOWS:
        print("     (Right-click its icon in the taskbar → Quit)")
    else:
        print("     (Cmd+Q)")
    print("     MCP servers only load on startup.")
    print()
    print("  2. Reopen Cursor and open any project")
    print("     (or open a new empty folder)")
    print()
    print("  3. Open Agent mode:")
    if IS_WINDOWS:
        print(f"     Press {CYAN}Ctrl+I{RESET} (or click the sparkle icon)")
    else:
        print(f"     Press {CYAN}Cmd+I{RESET} (or click the sparkle icon)")
    print(f"     Make sure the mode shows {CYAN}Agent{RESET}")
    print()
    print("  4. Type:")
    print(f"     {CYAN}Connect my Meta Ads account{RESET}")
    print("     or")
    print(f"     {CYAN}Connect my Google Ads account{RESET}")

print()
print(_DIV)
print()
print(f"  {BOLD}Where your credentials are stored:{RESET}")
print(f"  {INSTALL_DIR / '.env'}")
print()
print("  This file is NOT uploaded anywhere.")
print("  It stays on your computer only.")
print("  Nothing is sent except directly to Meta")
print("  and Google's own APIs.")
print("  (\"Gitignored\" = GitHub will never include")
print("  this file, even if you share your code.)")
print()
print("  Questions or issues:")
print("  github.com/benheis/ads-mcp-connector")
print()
print(_DIV)
print()
print(f"  {BOLD}\u2191  SCROLL UP to read your next steps.{RESET}")
print("  Everything you need is printed above.")
print()
