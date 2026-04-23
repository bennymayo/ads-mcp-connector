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

## What it can do

### Pull your data (ask questions)
- See campaign, ad set, and ad performance across Meta and Google — spend, CPA, ROAS, CTR, reach, frequency
- Break down any campaign by age, gender, placement, or device
- See the exact search terms triggering your Google Ads
- Pull monthly reach trends for audience saturation analysis

### Make changes (take action)
No more switching tabs. You can now do all of this from Claude:

**Meta Ads**
- Pause or enable campaigns, ad sets, and individual ads
- Update budgets — daily or lifetime, on campaigns or ad sets
- Set per-ad-set spend minimums and maximums inside CBO campaigns
- Build new campaigns end-to-end: create the campaign → ad set → upload your image or video → build the creative → launch the ad

**Google Ads**
- Pause or enable campaigns and ad groups
- Add and remove negative keywords (campaign or ad group level)
- Update keyword bids
- Update campaign budgets
- Create new campaigns, ad groups, and responsive search ads

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
| Google Sheets | Service account key | Never |

---

## Uploading ads from Google Sheets (agency workflow)

If your team tracks campaigns in a Google Sheet, you can launch ads directly from the sheet without touching Ads Manager.

### How it works

1. Your sheet has one row per ad to launch — campaign, ad set, ad name, headline, copy, asset URL, CTA
2. Set `Status = READY` on rows you want to launch
3. Ask Claude: *"Launch the READY rows in my trafficking sheet"*
4. Claude shows you a preview of what it will create (dry run)
5. You confirm — Claude uploads each asset, builds the creative, creates the ad as PAUSED
6. The sheet gets updated: `Status = LAUNCHED` with the new Ad ID, or `Status = ERROR` with the reason

### Sheet format

| Column | Required | Notes |
|--------|----------|-------|
| Campaign ID | Yes | From `meta_get_campaigns` |
| Ad Set ID | Yes | From `meta_get_ad_sets` |
| Ad Name | Yes | Your naming convention, used exactly as-is |
| Headline | Yes | Ad headline |
| Body Copy | Yes | Primary ad copy |
| Asset URL | Yes | Google Drive sharing link or direct HTTPS URL |
| Destination URL | Yes | Landing page |
| Page ID | Yes | Your Facebook Page ID |
| CTA | Yes | LEARN_MORE, SHOP_NOW, SIGN_UP, etc. |
| Description | No | Optional ad description |
| Asset Type | No | `image` or `video` — auto-detected if blank |
| Status | Yes | READY → launches. LAUNCHED / ERROR / SKIP → skipped |
| Ad ID | No | Written back by Claude after launch |
| Error | No | Written back by Claude if launch fails |

### Google Sheets setup (one-time, ~10 minutes)

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → **APIs & Services** → **Enable APIs** → enable **Google Sheets API**
2. Go to **Credentials** → **Create credentials** → **Service account** → download the JSON key
3. Add to your `.env`:
   ```
   GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/your-service-account-key.json
   ```
4. Share your Google Sheet with the service account email (found inside the JSON key) — grant **Editor** access so Claude can write status back

### Asset URLs

Assets can come from anywhere:
- **Google Drive**: share the file → copy link → paste the `drive.google.com/file/d/...` URL directly into the sheet
- **Direct URL**: any `https://` link to a `.jpg`, `.png`, `.mp4`, or `.mov` file

---

## Security

Every commit to this repo is scanned automatically for exposed credentials.

If you accidentally paste an API key into a source file and try to commit it, the commit will be blocked with a plain-English explanation of what to do.

To run a manual scan:
```bash
python secrets_check.py
```

---

## Tools reference

Everything Claude can do with your ad accounts. The AI picks the right tool automatically — you just ask in plain English.

### Meta Ads — Read
| Tool | What it does |
|------|-------------|
| `meta_get_account_overview` | Total spend, reach, and performance at a glance |
| `meta_get_campaigns` | All campaigns with spend and performance |
| `meta_get_ad_sets` | Ad sets with targeting, reach, and delivery |
| `meta_get_ads` | Every ad with spend, CPA, and creative age |
| `meta_get_insights` | Break down any campaign by age, gender, placement, or device |
| `meta_get_monthly_reach` | Month-by-month reach for the last 13 months |
| `meta_get_ad_images` | Browse your uploaded image library |

### Meta Ads — Make changes
| Tool | What it does |
|------|-------------|
| `meta_update_campaign_status` | Pause or enable a campaign |
| `meta_update_ad_set_status` | Pause or enable an ad set |
| `meta_update_ad_status` | Pause or enable an individual ad |
| `meta_update_budget` | Change daily or lifetime budget; set per-ad-set spend limits in CBO |
| `meta_create_campaign` | Create a new campaign |
| `meta_create_ad_set` | Create an ad set with targeting and budget |
| `meta_upload_image` | Upload a JPG or PNG from your computer |
| `meta_upload_video` | Upload an MP4 or MOV from your computer |
| `meta_create_ad_creative` | Build an ad creative from an uploaded image or video |
| `meta_create_ad` | Create an ad and attach it to a creative |

### Google Ads — Read
| Tool | What it does |
|------|-------------|
| `google_get_account_overview` | Total cost, conversions, ROAS, and impression share |
| `google_get_campaigns` | All campaigns with cost, clicks, and ROAS |
| `google_get_ad_groups` | Ad group breakdown |
| `google_get_keywords` | Keywords with Quality Score, bids, and performance |
| `google_get_search_terms` | Actual search queries triggering your ads |
| `google_list_negative_keywords` | See all existing negative keywords and their IDs |

### Google Ads — Make changes
| Tool | What it does |
|------|-------------|
| `google_update_campaign_status` | Pause or enable a campaign |
| `google_update_ad_group_status` | Pause or enable an ad group |
| `google_update_keyword_bid` | Change the max CPC for a keyword |
| `google_update_campaign_budget` | Change a campaign's daily budget |
| `google_add_negative_keywords` | Add negatives at campaign or ad group level |
| `google_remove_negative_keywords` | Remove negatives by ID |
| `google_create_campaign` | Create a new campaign with bidding strategy |
| `google_create_ad_group` | Create an ad group inside a campaign |
| `google_create_responsive_search_ad` | Build a responsive search ad with headlines and descriptions |

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

## Related

**[meta-account-diagnostics](https://github.com/benheis/meta-account-diagnostics)** — a companion skill (`/meta-diagnostics`) that runs a full 7-analysis Meta Ads account audit and generates a Streamlit dashboard. Plug it into any AI tool that supports MCP.

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
