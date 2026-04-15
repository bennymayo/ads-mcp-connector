# ads-mcp-connector

Connect Claude Code to Meta Ads and Google Ads. Ask questions about your campaigns in plain English. No CSV exports, no copy-pasting, no manual data pulls.

Built for marketing teams by [@benheiser](https://linkedin.com/in/benheiser).

---

## Installation

Pick your computer type below. The installer asks you a few questions and handles everything else automatically.

---

### On a Mac

**Step 1 — Open Terminal**

Press `Cmd + Space`, type **Terminal**, and press Enter.

A window with a text prompt will appear. That's all you need — it's just a text-based way to give your computer instructions.

**Step 2 — Run the installer**

Copy this line, paste it into Terminal, and press Enter:

```bash
curl -fsSL https://raw.githubusercontent.com/benheis/ads-mcp-connector/main/install.py | python3
```

The installer will walk you through the rest. It takes about 5 minutes.

---

### On Windows

**Step 1 — Make sure Python is installed**

Python is a free program this tool runs on. To check if you already have it:

1. Press the **Windows key**, type **cmd**, and press Enter to open Command Prompt
2. Type this and press Enter:
   ```
   python --version
   ```
3. If you see something like `Python 3.11.0`, you're good — skip to Step 2
4. If you get an error or see a version lower than 3.10, you need to install Python first

**Don't have Python?** Run this in PowerShell to open the download page automatically:
```powershell
python --version 2>$null; if ($LASTEXITCODE -ne 0) { Start-Process "https://www.python.org/downloads/" }
```
Download and install Python (takes about 3 minutes). When installing, check the box that says **"Add Python to PATH"** — this is important. Then come back here.

**Step 2 — Run the installer**

In Command Prompt, copy this line, paste it in, and press Enter:

```
curl -fsSL https://raw.githubusercontent.com/benheis/ads-mcp-connector/main/install.py | python
```

The installer will walk you through the rest. It takes about 5 minutes.

---

**What the installer does:**
- Downloads this connector to your computer (into a folder called `ads-mcp-connector`)
- Sets up a private Python workspace just for this tool
- Connects it to whichever AI tool you choose (Claude Code, Claude Desktop, or Cursor)
- Creates a secure credentials file that never leaves your machine

---

## Supported tools

| Tool | Works | Guided setup skill |
|------|-------|--------------------|
| [Claude Code](https://claude.ai/code) | ✓ | ✓ `/ads-connect` |
| [Claude Desktop / Cowork](https://claude.ai/download) | ✓ | ask in natural language |
| [Cursor](https://cursor.com) | ✓ | ask in agent mode |
| Claude.ai (web) | ✗ | — |

The installer detects which tools you have installed and registers automatically with all of them. If you install a new tool later, just run `bash install.sh` again.

---

## Usage

**Claude Code** — open any project and type:
```
/ads-connect
```
The skill walks you through connecting your ad accounts step by step.

**Claude Desktop / Cowork** — restart after install, then just ask:
```
Connect my Meta Ads account
```

**Cursor** — restart after install, open agent mode, then ask:
```
Connect my ad accounts and show me last month's campaigns
```

Once connected, ask questions in plain English from any of these tools:

```
Show me my campaigns from last month

What search terms are triggering my Google Ads?

Compare Meta and Google spend this week

Break down my top campaign by age and gender

What's my ROAS across both platforms?
```

---

## What gets connected

### Meta Ads
- Campaign performance (spend, impressions, clicks, CTR, CPC)
- Ad set breakdowns (by age, gender, placement, device)
- Individual ad performance with creative details
- Account-level overview

### Google Ads
- Campaign performance (cost, clicks, conversions, ROAS)
- Keyword performance with Quality Scores
- Search term report — see exactly what searches triggered your ads
- Ad group breakdown

---

## How credentials are stored

Your API keys are stored in a `.env` file at `~/ads-mcp-connector/.env`. This file is:
- **Gitignored** — never committed to GitHub
- **Local only** — stays on your machine
- **Written by the skill** — you never need to edit it manually

The `/ads-connect` skill writes your credentials directly from Claude chat to the `.env` file. You paste a token in chat, the skill saves it securely — the full value is never echoed back.

### Credential lifespans

| Platform | Method | Expires |
|----------|--------|---------|
| Meta Ads | System User token (recommended) | Never |
| Meta Ads | Graph API Explorer token (fallback) | 60 days |
| Google Ads | OAuth2 refresh token | Never (unless revoked) |

---

## Security

Every commit to this repo is scanned automatically for exposed credentials.

If you accidentally paste an API key into a source file and try to commit it, the commit will be blocked with a plain-English explanation of what to do.

To run a manual scan:
```bash
python secrets_check.py
```

---

## Connecting to other tools

The MCP server exposes these tools to Claude Code. You can reference them directly in any Claude session:

| Tool | What it does |
|------|-------------|
| `check_connection` | Test credentials for both platforms |
| `meta_get_campaigns` | List campaigns with performance data |
| `meta_get_ad_sets` | Ad sets with targeting and delivery |
| `meta_get_ads` | Individual ads with creative and metrics |
| `meta_get_account_overview` | Top-level account stats |
| `meta_get_insights` | Breakdown by age, gender, placement, device |
| `google_get_campaigns` | Campaigns with cost, conversions, ROAS |
| `google_get_keywords` | Keywords with Quality Score |
| `google_get_search_terms` | Actual searches triggering your ads |
| `google_get_account_overview` | Account-level ROAS and impression share |
| `google_get_ad_groups` | Ad group performance |

---

## Troubleshooting

**Claude Code doesn't recognize `/ads-connect`**
Run `bash ~/ads-mcp-connector/install.sh` again and restart Claude Code.

**Meta token expired**
Run `/ads-connect` — the skill detects expiration automatically and walks you through renewal (2 min). Avoid this entirely by using the System User setup path (token never expires).

**Google returns an auth error**
Your refresh token may have been revoked. Go to [myaccount.google.com/permissions](https://myaccount.google.com/permissions), remove access for your app, then run `python get_google_token.py` to generate a new one.

**Pre-commit hook not running**
Run `bash install.sh` from inside the repo directory to reinstall it.

---

## Related repos

- [Curtis Howland's Facebook ad diagnostic framework](https://linkedin.com/in/curtishowland/) — the companion skill that runs automated ad performance diagnostics using this connector

---

## Advanced: Google's official MCP server

Google maintains their own open-source MCP server for Google Ads:
[developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server](https://developers.google.com/google-ads/api/docs/developer-toolkit/mcp-server)

It also runs locally and is worth knowing about, but it's designed for developers rather than marketers. A few differences to be aware of:

| | This connector | Google's official server |
|---|---|---|
| Setup | Guided wizard via `/ads-connect` | Manual credential files |
| Google Ads tools | 5 purpose-built (campaigns, keywords, search terms, etc.) | 2 generic tools (raw query language) |
| Meta Ads | ✓ included | ✗ not included |
| Maintained by | This repo | Google |

**When you'd choose Google's server:** your team has a developer who wants full GAQL query flexibility and is already comfortable with Google Cloud credentials.

**When you'd choose this connector:** you're a marketer who wants a guided setup and plain-English tools without writing query syntax.

---

## License

MIT — use it, fork it, build on it.
