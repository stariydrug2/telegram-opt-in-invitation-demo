"""Consent-aware CSV preview for the TeleFlow inviting demo."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

MAX_ROWS = 5
USERNAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{3,30}[A-Za-z0-9]$")
REQUIRED = {"username", "consent", "consent_source"}


def preview(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        fields = {name.strip().lower() for name in (reader.fieldnames or [])}
        missing = REQUIRED - fields
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
        rows = []
        seen = set()
        for row in reader:
            username = (row.get("username") or "").strip().removeprefix("@").lower()
            consent = (row.get("consent") or "").strip().lower()
            source = (row.get("consent_source") or "").strip()
            if consent not in {"yes", "true", "1"} or not source:
                raise ValueError("Every row must include explicit consent and its source.")
            if not USERNAME_RE.fullmatch(username):
                raise ValueError(f"Invalid Telegram username: {username!r}")
            if username in seen:
                continue
            seen.add(username)
            rows.append({"username": "@" + username, "name": (row.get("name") or "").strip()[:80], "consent_source": source[:160]})
            if len(rows) > MAX_ROWS:
                raise ValueError("Demo preview is limited to five unique contacts. Full workflow: https://teleflow.space/")
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python app.py audience.csv")
        return 2
    try:
        rows = preview(Path(sys.argv[1]))
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        return 1
    print(f"Preview only: {len(rows)} consented contacts. No invitations are sent.\n")
    for row in rows:
        print(f"{row['username']}  {row['name']}  consent: {row['consent_source']}")
    print("\nFor campaign setup and full Telegram integration: https://teleflow.space/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
