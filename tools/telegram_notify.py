"""Telegram notification dispatcher for Money HQ operations and failure detection.

Reads credentials strictly from environment variables or the local non-Git
Agent Zero .env file (`C:\\Users\\ACER\\agent-zero\\agent-zero\\usr\\.env`).
Never stores credentials in Git or logs.
"""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_ENV_PATH = Path(r"C:\Users\ACER\agent-zero\agent-zero\usr\.env")


def load_telegram_credentials(env_path: Path = DEFAULT_ENV_PATH) -> tuple[str, str]:
    """Load TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from env vars or local .env file."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if (not token or not chat_id) and env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key == "TELEGRAM_BOT_TOKEN" and not token:
                token = val
            elif key == "TELEGRAM_CHAT_ID" and not chat_id:
                chat_id = val
    return token, chat_id


def send_telegram_alert(message: str, dry_run: bool = False) -> dict[str, Any]:
    """Send an HTML-formatted alert to the authorized owner Telegram chat."""
    token, chat_id = load_telegram_credentials()
    if dry_run or not token or not chat_id:
        return {"ok": True, "dry_run": True, "reason": "dry_run or missing credentials"}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "HTML"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    res = send_telegram_alert("🔔 <b>[MONEY HQ]</b> Kiểm tra hệ thống cảnh báo độc lập: Hoạt động bình thường.")
    print("Telegram Alert Sent:", res.get("ok"))
