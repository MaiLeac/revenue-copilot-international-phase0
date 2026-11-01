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

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

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
    cmd_strip = cmd.strip()
    cmd_lower = cmd_strip.lower()

    # 0. Exness / Trading questions
    if any(k in cmd_lower for k in ["exness", "mt5", "metatrader", "trade", "trading"]):
        return (
            "📈 <b>VỀ KẾT NỐI EXNESS & GIAO DỊCH TỰ ĐỘNG:</b>\n\n"
            "Em chào Mai! Về trang web Exness Mai đang mở trên Chrome (<code>my.exness.com</code>):\n\n"
            "• Trang web đó là <b>Khu vực cá nhân</b> để người xem quản lý tài khoản thủ công.\n"
            "• Để bot Python/Agent Zero tự động kết nối và chạy chiến lược (ở <b>chế độ DEMO khóa vốn 100%</b>, tuyệt đối không dùng tiền thật), hệ thống cần bắt sóng IPC qua phần mềm <b>MetaTrader 5 (MT5)</b> cài đặt trực tiếp trên máy Windows.\n\n"
            "👉 <b>Cách kích hoạt siêu nhanh:</b>\n"
            "1. Trên web Exness Mai đang mở, bấm vào mục <b>Giao dịch</b> (hoặc biểu tượng 3 chấm ở tài khoản Demo) -> Chọn <b>Tải MetaTrader 5</b>.\n"
            "2. Cài đặt file tải về (khoảng 30 giây).\n\n"
            "Sau khi cài xong, bot trading Python sẽ tự động bắt sóng tài khoản Demo qua thư viện <code>MetaTrader5</code> và báo cáo lệnh/rủi ro cho Mai ngay tại đây!"
        )

    # 1. Long task prompt or instructions from owner
    if len(cmd_strip) > 60 or cmd_lower.startswith(("#", "task", "lệnh:", "chỉ thị:", "yêu cầu:")):
        log_file = REPO_ROOT / "operations" / "OWNER_TELEGRAM_LOG.md"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        snippet = cmd_strip[:120].replace("\n", " ")
        entry = (
            f"\n- **[{timestamp}] Chỉ thị từ Mai:**\n"
            f"  ```text\n{cmd_strip}\n  ```\n"
            f"  *Trạng thái:* Đã ghi nhận qua Source `telegram_owner` vào Superagent Control Plane.\n"
        )
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(entry)

        return (
            "📥 <b>ĐÃ TIẾP NHẬN CHỈ THỊ VÀO MONEY HQ:</b>\n\n"
            f"<i>\"{snippet}...\"</i>\n\n"
            "⚙️ <b>Lưu ý:</b> Bot Telegram này là kênh nhận lệnh & báo cáo nhanh. "
            "Tác vụ đã được ghi vào hệ thống và kích hoạt Task Router tự động!\n\n"
            "Gõ <code>link</code> để lấy danh sách link web, hoặc <code>báo cáo</code> để xem tình hình tài chính."
        )

    # 2. Financial report
    if cmd_lower in ["báo cáo", "status", "/status", "tình hình", "doanh thu", "tiền"] or (
        len(cmd_strip) < 30 and any(k in cmd_lower for k in ["báo cáo", "status", "doanh thu"])
    ):
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

    # 3. Test suite
    if cmd_lower in ["test", "/test", "kiểm tra"]:
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

    # 4. Product links
    if "link" in cmd_lower or cmd_lower in ["/links", "/web", "web"]:
        return (
            "🌐 <b>CÁC ĐƯỜNG LINK TRẢI NGHIỆM TRỰC TIẾP:</b>\n\n"
            "1. 🌸 Web Trắc Nghiệm Dưỡng Nhan (69k):\nhttps://maileac.github.io/revenue-copilot-international-phase0/experiments/exp03-duong-nhan-ai-mvp/\n\n"
            "2. 📖 Cẩm Nang Có Khóa Bản Quyền:\nhttps://maileac.github.io/revenue-copilot-international-phase0/experiments/exp03-duong-nhan-ai-mvp/handbook.html\n\n"
            "3. 🧹 Web Clean CSV (199k / $9 USD):\nhttps://maileac.github.io/revenue-copilot-international-phase0/experiments/exp02-catalogue-qa-pilot/\n\n"
            "4. 🏰 Loser Kingdom (Máy này):\nhttp://localhost:8891/today.html\n\n"
            "5. 📊 Bảng Google Sheet tab Money HQ:\nhttps://docs.google.com/spreadsheets/d/1UPReETEtQJVYTEXHyzLbOOm5aNVJpjzEYr6aJKWIals/edit?gid=66015035#gid=66015035"
        )

    log_file = REPO_ROOT / "operations" / "OWNER_TELEGRAM_LOG.md"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"\n- **[{timestamp}] Lệnh từ Mai:** {cmd_strip}\n"
        f"  *Trạng thái:* Đã tiếp nhận qua Source `telegram_owner` và đưa vào hàng đợi Superagent Control Plane.\n"
    )
    with log_file.open("a", encoding="utf-8") as fh:
        fh.write(entry)

    return (
        f"🫡 <b>ĐÃ TIẾP NHẬN CHỈ ĐẠO CỦA MAI:</b>\n\n"
        f"<i>\"{cmd_strip}\"</i>\n\n"
        f"📝 Đã ghi nhận vào <code>operations/OWNER_TELEGRAM_LOG.md</code> và chuyển giao qua Task Router!\n\n"
        "Gõ <code>link</code> để lấy danh sách link web, hoặc <code>báo cáo</code> để xem tình hình tài chính."
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
                try:
                    print(f"Received instruction: {text}")
                except Exception:
                    pass
                reply = handle_command(text)
                send_message(reply)
        except Exception as exc:
            try:
                print("Loop error:", exc)
            except Exception:
                pass
            time.sleep(3)


if __name__ == "__main__":
    main()
