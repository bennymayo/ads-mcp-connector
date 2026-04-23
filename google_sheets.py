"""Google Sheets integration for trafficking sheet read/write.

Auth: service account JSON key file. Set GOOGLE_SHEETS_CREDENTIALS_PATH in .env.
The service account needs to be granted Viewer (for reads) or Editor (for reads +
status write-back) on the target spreadsheet.

How to get credentials:
1. Go to console.cloud.google.com → APIs & Services → Credentials
2. Create a Service Account, download the JSON key
3. Set GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/key.json in .env
4. Share the Google Sheet with the service account email (found in the JSON key)
"""

from __future__ import annotations

import os
from typing import Optional

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Canonical column names the trafficking sheet is expected to have.
# Variants (case-insensitive, stripped) are resolved on read.
REQUIRED_COLUMNS = [
    "Campaign ID",
    "Ad Set ID",
    "Ad Name",
    "Headline",
    "Body Copy",
    "Asset URL",
    "Destination URL",
    "Page ID",
    "CTA",
    "Status",
]

OPTIONAL_COLUMNS = [
    "Campaign Name",
    "Ad Set Name",
    "Description",
    "Asset Type",   # "image" or "video" — auto-detected if absent
    "Ad ID",        # written back after launch
    "Error",        # written back on failure
]

STATUS_READY    = "READY"
STATUS_LAUNCHED = "LAUNCHED"
STATUS_ERROR    = "ERROR"
STATUS_SKIP     = "SKIP"


def _credentials_path() -> str:
    path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "")
    if not path:
        raise EnvironmentError(
            "GOOGLE_SHEETS_CREDENTIALS_PATH not set. "
            "Add it to .env pointing at your service account JSON key file."
        )
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Service account key not found at: {path}. "
            "Download it from Google Cloud Console → APIs & Services → Credentials."
        )
    return path


def _build_service():
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError(
            "Google Sheets dependencies not installed. "
            "Run: pip install google-api-python-client google-auth"
        )
    creds = Credentials.from_service_account_file(_credentials_path(), scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def _resolve_headers(headers: list[str]) -> dict[str, int]:
    """Map canonical column name → zero-based column index, case-insensitive."""
    normalized = {h.strip().lower(): i for i, h in enumerate(headers)}
    result = {}
    for col in REQUIRED_COLUMNS + OPTIONAL_COLUMNS:
        key = col.strip().lower()
        if key in normalized:
            result[col] = normalized[key]
    return result


def check_config() -> Optional[dict]:
    """Return an error dict if Sheets credentials are not configured, else None."""
    try:
        _credentials_path()
        return None
    except (EnvironmentError, FileNotFoundError) as e:
        return {"error": "SHEETS_CONFIG_ERROR", "message": str(e)}


def read_trafficking_sheet(sheet_id: str, tab_name: str = "Trafficking") -> dict:
    """Read all rows from a trafficking sheet tab.

    Returns:
        {
            "rows": [
                {
                    "row_index": 2,          # 1-based sheet row (row 1 = header)
                    "Campaign ID": "...",
                    "Ad Set ID": "...",
                    "Ad Name": "...",
                    "Headline": "...",
                    "Body Copy": "...",
                    "Asset URL": "...",
                    "Destination URL": "...",
                    "Page ID": "...",
                    "CTA": "LEARN_MORE",
                    "Status": "READY",
                    # optional columns present if found in sheet
                }
            ],
            "total": N,
            "ready": N,
            "sheet_id": "...",
            "tab_name": "...",
            "missing_columns": [...]   # required columns not found in header
        }
    """
    try:
        service = _build_service()
    except (ImportError, EnvironmentError, FileNotFoundError) as e:
        return {"error": "SHEETS_CONFIG_ERROR", "message": str(e)}

    try:
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=tab_name)
            .execute()
        )
    except Exception as e:
        return {"error": "SHEETS_READ_ERROR", "message": str(e),
                "hint": "Check that the sheet ID is correct and the service account has access."}

    values = result.get("values", [])
    if not values:
        return {"error": "SHEETS_EMPTY", "message": f"Tab '{tab_name}' is empty or not found."}

    headers = values[0]
    col_map = _resolve_headers(headers)

    missing = [c for c in REQUIRED_COLUMNS if c not in col_map]

    rows = []
    for i, row in enumerate(values[1:], start=2):  # row_index is 1-based; row 1 = header
        def cell(col: str) -> str:
            idx = col_map.get(col)
            if idx is None or idx >= len(row):
                return ""
            return str(row[idx]).strip()

        rows.append({
            "row_index": i,
            **{col: cell(col) for col in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if col in col_map},
        })

    ready = [r for r in rows if r.get("Status", "").upper() == STATUS_READY]

    return {
        "rows": rows,
        "total": len(rows),
        "ready": len(ready),
        "sheet_id": sheet_id,
        "tab_name": tab_name,
        "missing_columns": missing,
    }


def update_row_status(
    sheet_id: str,
    tab_name: str,
    row_index: int,
    status: str,
    ad_id: str = "",
    error: str = "",
) -> dict:
    """Write status, ad_id, and error back to a trafficking sheet row.

    row_index: 1-based sheet row number (as returned by read_trafficking_sheet).
    """
    try:
        service = _build_service()
    except (ImportError, EnvironmentError, FileNotFoundError) as e:
        return {"error": "SHEETS_CONFIG_ERROR", "message": str(e)}

    # We need the header row to find the column positions for Status / Ad ID / Error
    try:
        header_result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"{tab_name}!1:1")
            .execute()
        )
    except Exception as e:
        return {"error": "SHEETS_READ_ERROR", "message": str(e)}

    headers = header_result.get("values", [[]])[0]
    col_map = _resolve_headers(headers)

    updates = []
    def _a1(col_name: str) -> Optional[str]:
        idx = col_map.get(col_name)
        if idx is None:
            return None
        col_letter = _col_letter(idx)
        return f"{tab_name}!{col_letter}{row_index}"

    if _a1("Status"):
        updates.append({"range": _a1("Status"), "values": [[status]]})
    if ad_id and _a1("Ad ID"):
        updates.append({"range": _a1("Ad ID"), "values": [[ad_id]]})
    if error and _a1("Error"):
        updates.append({"range": _a1("Error"), "values": [[error]]})

    if not updates:
        return {"error": "SHEETS_WRITE_ERROR",
                "message": "Could not find Status, Ad ID, or Error columns in sheet header."}

    try:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=sheet_id,
            body={"valueInputOption": "RAW", "data": updates},
        ).execute()
    except Exception as e:
        return {"error": "SHEETS_WRITE_ERROR", "message": str(e)}

    return {"updated": True, "row_index": row_index, "status": status}


def _col_letter(index: int) -> str:
    """Convert a zero-based column index to A1 notation letter (0→A, 25→Z, 26→AA)."""
    result = ""
    index += 1
    while index > 0:
        index, rem = divmod(index - 1, 26)
        result = chr(65 + rem) + result
    return result
