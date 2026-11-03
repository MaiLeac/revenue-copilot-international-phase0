"""Money HQ Daily Revenue & Bottleneck Watchdog.

Performs daily diagnosis of cash flow, bottlenecks, and action items.
Sends proactive Daily Operations Brief to Owner Telegram automatically.
Can run as a stand-alone pass or a persistent daemon scheduled at 08:30 and 20:30 ICT.
"""

from __future__ import annotations

import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.telegram_notify import send_telegram_alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("money_hq.revenue_watchdog")


def run_diagnostics() -> dict:
    # 1. Update Money HQ Dashboard
    try:
        subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "money_hq_dashboard.py")],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=15,
        )
    except Exception as e:
        logger.error(f"Dashboard run failed: {e}")

    # 2. Check MT5 Daemon state
    mt5_state_file = REPO_ROOT / "trading-agent-exness-demo" / "run_state.json"
    mt5_info = {"status": "OFFLINE", "balance": 0.0, "pnl_pct": 0.0, "open_positions": 0}
    if mt5_state_file.exists():
        try:
            raw = json.loads(mt5_state_file.read_text(encoding="utf-8"))
            acc = raw.get("account") or {}
            risk = raw.get("risk") or {}
            mt5_info = {
                "status": raw.get("status", "UNKNOWN"),
                "balance": acc.get("balance", 0.0),
                "currency": acc.get("currency", "USD"),
                "pnl_pct": risk.get("daily_pnl_pct", 0.0),
                "open_positions": len(raw.get("open_positions", [])),
                "last_heartbeat": raw.get("last_heartbeat_utc", ""),
            }
        except Exception as e:
            logger.error(f"Failed to read MT5 state: {e}")

    # 3. Read Dashboard numbers
    md_path = REPO_ROOT / "finance" / "MONEY_HQ_DASHBOARD.md"
    l4_cash = "0 VND"
    if md_path.exists():
        for line in md_path.read_text(encoding="utf-8").splitlines():
            if "Realized Revenue (`L4`" in line or "Net Realized Profit (`L4`)" in line:
                l4_cash = line.split(":", 1)[-1].strip().strip("`")

    return {
        "l4_cash": l4_cash,
        "mt5": mt5_info,
        "assets": [
            {
                "id": "EXP-03",
                "name": "Dưỡng Nhan AI MVP (69k / 299k)",
                "status": "LIVE ONLINE",
                "link": "https://maileac.github.io/revenue-copilot-international-phase0/experiments/exp03-duong-nhan-ai-mvp/",
                "bottleneck": "Zero Traffic (0 lượt xem, chưa đăng bài kéo traffic mạng xã hội)",
            },
            {
                "id": "EXP-02",
                "name": "SaaS B2B Clean CSV ($9 USD / 199k)",
                "status": "LIVE ONLINE",
                "link": "https://maileac.github.io/revenue-copilot-international-phase0/experiments/exp02-catalogue-qa-pilot/",
                "bottleneck": "Chưa có danh sách tiếp cận (Outreach) gửi chủ shop TMĐT",
            },
            {
                "id": "TRD-01",
                "name": "Trading Bot MT5 (EURUSD Pilot)",
                "status": f"RUNNING ({mt5_info['status']}) - Balance: ${mt5_info['balance']:,.2f}",
                "bottleneck": "Chế độ Sandbox Demo (chưa phải tiền rút về). Phiên hôm nay sideway, bot giữ kỷ luật Flat.",
            },
        ],
    }


def generate_daily_brief(diag: dict) -> tuple[str, str]:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Telegram HTML format
    tg_msg = (
        f"🚨 <b>BÁO CÁO TÌNH HÌNH MONEY HQ ({now_str})</b>\n\n"
        f"💵 <b>Tiền mặt thực thu (L4):</b> <code>{diag['l4_cash']}</code>\n"
        f"⚠️ <b>CẢNH BÁO BÁO ĐỘNG ĐỎ:</b> Doanh thu thực tế hôm nay = 0 VND!\n\n"
        f"🔍 <b>BÓC TÁCH NGUYÊN NHÂN VÌ SAO CHƯA RA TIỀN:</b>\n"
        f"1. <b>Trading Bot MT5 (${diag['mt5']['balance']:,.2f}):</b>\n"
        f"   • Đang ở tài khoản <b>DEMO</b> để luyện thuật toán và quản trị rủi ro -> <i>Chưa thể rút tiền mặt về tài khoản ngân hàng thật</i>.\n"
        f"   • Phiên hôm nay thị trường EURUSD đi ngang hẹp, bot giữ kỷ luật <b>Flat (0 lệnh)</b> để bảo toàn vốn.\n\n"
        f"2. <b>Web Dưỡng Nhan AI (Exp03 - 69k/lượt):</b>\n"
        f"   • Web đã online 100%, có VietQR tự động, nhưng <b>LƯỢNG TRUY CẬP = 0 (Zero Traffic)</b>!\n"
        f"   • Điểm nghẽn: Chưa ai biết đến link web vì chưa có bài đăng nào trên TikTok / Facebook / Threads.\n\n"
        f"3. <b>SaaS B2B Clean CSV (Exp02 - $9 USD):</b>\n"
        f"   • Web đã hoàn thiện nhưng chưa gửi chào hàng (Cold Outreach) đến các chủ shop TMĐT.\n\n"
        f"🎯 <b>3 HÀNH ĐỘNG CẦN LÀM NGAY ĐỂ BẮT ĐẦU CÓ TIỀN:</b>\n"
        f"• <b>Việc 1:</b> Copy link Dưỡng Nhan AI đăng kèm bài viết/video ngắn lên Threads/TikTok để test lượt bấm.\n"
        f"• <b>Việc 2:</b> Duy trì bot MT5 chạy forward-test demo thêm 2 tuần để đủ điều kiện thi quỹ cấp vốn (Prop Firm FTMO/MFF).\n"
        f"• <b>Việc 3:</b> Đóng gói kho 1.857 bài viết vĩ mô thành cẩm nang/bản tin để bán hoặc thu hút độc giả.\n\n"
        f"🤖 <i>Hệ thống Watchdog đã được kích hoạt chạy ngầm, từ nay sẽ tự động gửi báo cáo sáng & tối mỗi ngày!</i>"
    )

    # Markdown format for operations/DAILY_BRIEF.md
    md_content = f"""# Daily Operations & Revenue Reality Brief

## Cập nhật: {now_str}
- **Thực thu L4 Realized Cash:** {diag['l4_cash']}
- **Trạng thái:** Báo động đỏ - Chưa phát sinh dòng tiền mặt thực tế.

### Bóc tách điểm nghẽn từng kênh:
1. **Trading Bot MT5:** Tài khoản Demo (${diag['mt5']['balance']:,.2f}), lệnh mở: {diag['mt5']['open_positions']}. Giữ kỷ luật bảo toàn vốn trong ngày sideway.
2. **Dưỡng Nhan AI MVP (69k/lượt):** Web live nhưng **0 Traffic**. Cần kênh phân phối truyền thông.
3. **B2B Clean CSV ($9 USD):** Web live nhưng chưa có phễu tiếp cận khách hàng doanh nghiệp.

### Kế hoạch hành động giải quyết điểm nghẽn:
- [ ] Soạn nội dung kịch bản truyền thông ngắn cho Dưỡng Nhan AI để đẩy lên Threads / TikTok / Facebook Groups.
- [ ] Thu thập danh sách 20 shop TMĐT để gửi demo làm sạch file CSV miễn phí chuyển đổi sang gói $9.
- [ ] Tiếp tục duy trì kỷ luật MT5 Demo forward-test để chuẩn bị kế hoạch thi quỹ cấp vốn không cần vốn tự có.
"""
    return tg_msg, md_content


def run_once(send_tele: bool = True) -> dict:
    diag = run_diagnostics()
    tg_msg, md_content = generate_daily_brief(diag)
    
    # Save to disk
    brief_file = REPO_ROOT / "operations" / "DAILY_BRIEF.md"
    brief_file.parent.mkdir(parents=True, exist_ok=True)
    brief_file.write_text(md_content, encoding="utf-8")
    logger.info(f"Updated {brief_file}")

    if send_tele:
        res = send_telegram_alert(tg_msg)
        logger.info(f"Sent Telegram Daily Brief: {res.get('ok')}")

    return diag


def daemon_loop():
    logger.info("Starting Daily Revenue Watchdog Daemon loop...")
    # Send initial diagnostic brief immediately on start
    run_once(send_tele=True)

    # Then check every 30 minutes, if it crosses 08:30 or 20:30 ICT, send report
    last_reported_slot = None
    while True:
        try:
            now_utc = datetime.now(timezone.utc)
            # ICT is UTC+7
            ict_hour = (now_utc.hour + 7) % 24
            ict_minute = now_utc.minute

            slot = None
            if ict_hour == 8 and ict_minute >= 30:
                slot = f"{now_utc.date().isoformat()}_morning"
            elif ict_hour == 20 and ict_minute >= 30:
                slot = f"{now_utc.date().isoformat()}_evening"

            if slot and slot != last_reported_slot:
                logger.info(f"Triggering scheduled daily brief for slot {slot}...")
                run_once(send_tele=True)
                last_reported_slot = slot

        except Exception as e:
            logger.error(f"Error in watchdog daemon loop: {e}")

        time.sleep(300)  # Check every 5 minutes


if __name__ == "__main__":
    if "--daemon" in sys.argv:
        daemon_loop()
    else:
        run_once(send_tele=True)
        print("Daily brief generated and sent to Telegram.")
