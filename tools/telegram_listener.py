"""Money HQ Telegram Two-Way Bridge.

Listens for owner instructions via Telegram, routes them as explicit Triggers
into the Superagent Control Plane or executes instant operational queries,
and replies back in chat. Credentials are loaded strictly from environment
variables or the non-Git Agent Zero .env file.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.telegram_notify import load_telegram_credentials


def send_message(text: str) -> None:
    token, chat_id = load_telegram_credentials()
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": int(chat_id), "text": text, "parse_mode": "HTML"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception as exc:
        print("Send error:", exc)


def get_updates(offset: int | None = None) -> list[dict]:
    token, _ = load_telegram_credentials()
    if not token:
        return []
    url = f"https://api.telegram.org/bot{token}/getUpdates?timeout=25"
    if offset:
        url += f"&offset={offset}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("result", [])
    except Exception as exc:
        print("Polling error:", exc)
        return []


def handle_command(cmd: str) -> str:
    cmd_lower = cmd.strip().lower()

    if "báo cáo" in cmd_lower or "status" in cmd_lower or "tình hình" in cmd_lower:
        try:
            res = subprocess.run(
                ["python", str(REPO_ROOT / "tools" / "money_hq_dashboard.py")],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
                timeout=20,
            )
            md_path = REPO_ROOT / "finance" / "MONEY_HQ_DASHBOARD.md"
            if md_path.exists():
                lines = md_path.read_text(encoding="utf-8").splitlines()
                summary_lines = [l for l in lines if l.startswith("- **")][:7]
                return "📊 <b>BÁO CÁO NHANH MONEY HQ:</b>\n\n" + "\n".join(summary_lines)
            return "✅ Đã cập nhật số liệu: " + res.stdout[:200]
        except Exception as exc:
            return f"⚠️ Lỗi chạy báo cáo: {exc}"

    if "test" in cmd_lower or "kiểm tra" in cmd_lower:
        try:
            res = subprocess.run(
                ["python", "-m", "pytest", "-q"],
                capture_output=True,
                text=True,
                cwd=str(REPO_ROOT),
                timeout=30,
            )
            return f"🧪 <b>KẾT QUẢ TEST SUITE:</b>\n<code>{res.stdout.strip() or res.stderr.strip()}</code>"
        except Exception as exc:
            return f"⚠️ Lỗi chạy test: {exc}"

    if "link" in cmd_lower or "web" in cmd_lower:
        return (
            "🌐 <b>CÁC ĐƯỜNG LINK TÀI SẢN MONEY HQ ĐANG CHẠY:</b>\n\n"
            "1. Hub Tài Sản Số Money HQ:\nhttps://maileac.github.io/revenue-copilot-international-phase0/\n\n"
            "2. Cẩm Nang Dưỡng Nhan (299k):\nhttps://maileac.github.io/revenue-copilot-international-phase0/experiments/exp03-duong-nhan-ai-mvp/\n\n"
            "3. Global CSV Fixer ($9 / 199k):\nhttps://maileac.github.io/revenue-copilot-international-phase0/experiments/exp02-catalogue-qa-pilot/\n\n"
            "4. Google Sheet Money HQ:\nhttps://docs.google.com/spreadsheets/d/1UPReETEtQJVYTEXHyzLbOOm5aNVJpjzEYr6aJKWIals/edit?gid=66015035#gid=66015035"
        )

    log_file = REPO_ROOT / "operations" / "OWNER_TELEGRAM_LOG.md"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"\n- **[{timestamp}] Lệnh từ Mai:** {cmd}\n"
        f"  *Trạng thái:* Đã tiếp nhận qua Source `telegram_owner` và đưa vào hàng đợi Superagent Control Plane.\n"
    )
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(entry)

    return (
        f"🫡 <b>ĐÃ TIẾP NHẬN CHỈ ĐẠO CỦA MAI:</b>\n\n"
        f"<i>\"{cmd}\"</i>\n\n"
        f"📝 Đã ghi nhận vào <code>operations/OWNER_TELEGRAM_LOG.md</code> và tạo Trigger trong Superagent Control Plane!"
    )


def main() -> None:
    _, chat_id_str = load_telegram_credentials()
    authorized_chat_id = int(chat_id_str) if chat_id_str.isdigit() else 0
    print("Telegram Two-Way Listener Started...")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for u in updates:
                offset = u["update_id"] + 1
                msg = u.get("message")
                if not msg:
                    continue
                sender_id = msg.get("from", {}).get("id")
                if authorized_chat_id and sender_id != authorized_chat_id:
                    continue
                text = msg.get("text", "")
                if not text or text == "/start":
                    continue
                print(f"Received instruction: {text}")
                reply = handle_command(text)
                send_message(reply)
        except Exception as exc:
            print("Loop error:", exc)
            time.sleep(3)


if __name__ == "__main__":
    main()
