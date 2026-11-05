"""WINK ECOSYSTEM & MONEY HQ — Daily Revenue & Venture Watchdog.

Runs twice daily (08:30 & 20:30 ICT / UTC+7) or on-demand to:
1. Track verified L4 usable cash in bank ledger.
2. Monitor health of all 5 active WINK ventures:
   - Bản Thảo Thấu Thể (:8000)
   - Wink Living (winkhere.com)
   - Vương Quốc Loser (:8888)
   - Little Loop Factory (:3210)
   - Vibe-Trading MT5 (:8899)
3. Audit MT5 Exness quantitative risk parameters (<0.75%).
4. Send high-signal briefings to Telegram without hardcoded illusions or manual labor platforms (0 uTest).
"""

from __future__ import annotations

import json
import logging
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.telegram_notify import send_telegram_alert
from tools.money_hq_dashboard import compute_money_hq_metrics
from tools.risk_review import review_mt5

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("WinkWatchdog")


def check_port_online(url: str, timeout: float = 2.0) -> bool:
    """Check if a local HTTP service responds."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WinkWatchdog/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return res.status in (200, 301, 302)
    except Exception:
        return False


def run_diagnostics() -> dict:
    # 1. Check local server ports
    port_status = {
        "hub_8000": check_port_online("http://127.0.0.1:8000/"),
        "bloom_8000": check_port_online("http://127.0.0.1:8000/experiments/exp03-duong-nhan-ai-mvp/"),
        "checkout_8000": check_port_online("http://127.0.0.1:8000/experiments/exp03-duong-nhan-ai-mvp/checkout.html"),
        "loser_8888": check_port_online("http://127.0.0.1:8888/"),
        "video_3210": check_port_online("http://127.0.0.1:3210/"),
        "vibe_8899": check_port_online("http://127.0.0.1:8899/"),
    }

    # 2. Check MT5 Daemon state & Quant Audit
    mt5_state_file = REPO_ROOT / "trading-agent-exness-demo" / "run_state.json"
    mt5_info = {"status": "UNKNOWN", "balance": None, "pnl_pct": None, "open_positions": None}
    if mt5_state_file.exists():
        try:
            raw = json.loads(mt5_state_file.read_text(encoding="utf-8"))
            acc = raw.get("account") or {}
            risk = raw.get("risk") or {}
            mt5_info = {
                "status": raw.get("status", "UNKNOWN"),
                "balance": acc.get("balance"),
                "currency": acc.get("currency", "USD"),
                "pnl_pct": risk.get("daily_pnl_pct", 0.0),
                "open_positions": len(raw.get("open_positions", [])),
                "last_heartbeat": raw.get("last_heartbeat_utc", ""),
            }
        except Exception as e:
            logger.error(f"Failed to read MT5 state: {e}")

    # Read Quant Backtest Stats
    quant_stats_file = REPO_ROOT / "trading-agent-exness-demo" / "research" / "quant_backtest_stats.json"
    quant_info = {"total_trades": None, "max_drawdown_pct": None, "win_rate": None, "symbols": []}
    if quant_stats_file.exists():
        try:
            q_raw = json.loads(quant_stats_file.read_text(encoding="utf-8"))
            quant_info["total_trades"] = q_raw.get("total_trades")
            quant_info["max_drawdown_pct"] = q_raw.get("max_drawdown_pct")
            quant_info["win_rate"] = q_raw.get("win_rate")
            quant_info["symbols"] = list(q_raw.get("stats_by_symbol", {}).keys())
        except Exception as e:
            logger.error(f"Failed to read Quant Stats: {e}")

    # Compute cash from source rows, never from a stale Markdown export.
    metrics = compute_money_hq_metrics(
        REPO_ROOT / "finance" / "CASH_LEDGER.csv",
        REPO_ROOT / "finance" / "COST_LEDGER.csv",
        REPO_ROOT / "finance" / "AI_USAGE_AND_COST_LOG.csv",
    )
    mt5_findings = review_mt5(REPO_ROOT)
    if any(f["code"] in {"MT5_HEARTBEAT_STALE", "MT5_HEARTBEAT_INVALID", "MT5_DEMO_INACTIVE"} for f in mt5_findings):
        mt5_info["status"] = "NOT VERIFIED RUNNING"

    return {
        "l4_cash": f"{metrics.realized_revenue_l4_vnd:,} VND",
        "incremental_cost_vnd": metrics.variable_costs_vnd + metrics.incremental_tool_api_costs_vnd,
        "mt5_findings": [f["code"] for f in mt5_findings],
        "ports": port_status,
        "mt5": mt5_info,
        "quant": quant_info,
        "urls": {
            "hub": "http://127.0.0.1:8000/",
            "duong_nhan": "http://127.0.0.1:8000/experiments/exp03-duong-nhan-ai-mvp/",
            "checkout": "http://127.0.0.1:8000/experiments/exp03-duong-nhan-ai-mvp/checkout.html",
            "wink_living": "https://winkhere.com/",
            "loser_kingdom": "http://127.0.0.1:8888/",
            "video_factory": "http://127.0.0.1:3210/",
            "vibe_trading": "http://127.0.0.1:8899/",
        },
    }


def generate_daily_brief(diag: dict) -> tuple[str, str]:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    ports = diag["ports"]
    sales_site = "mở được" if ports["bloom_8000"] else "không mở được"
    checkout = "mở được" if ports["checkout_8000"] else "không mở được"
    tg_msg = (
        f"<b>MONEY HQ — {now_str}</b>\n"
        f"Tiền thực nhận L4: <code>{diag['l4_cash']}</code>\n"
        f"Chi phí tăng thêm đã ghi: <code>{diag['incremental_cost_vnd']:,} VND</code>\n"
        f"Sách số: bản nháp {sales_site}; trang xem thử thanh toán {checkout}, chưa mở bán.\n"
        f"MT5 demo: {diag['mt5']['status']} ({', '.join(diag['mt5_findings']) or 'heartbeat mới'}). Không tính tiền demo là thu nhập."
    )
    md_content = (
        f"# Money HQ — kiểm tra {now_str}\n\n"
        f"- Tiền thực nhận L4: {diag['l4_cash']}\n"
        f"- Sách số: bản nháp {sales_site}; trang xem thử thanh toán {checkout}, chưa mở bán\n"
        "- Traffic, checkout và giao sách tự động: chưa đo/kiểm chứng.\n"
        "- MT5 là demo, không phải doanh thu.\n"
        "- Điều kiện tiến triển: thay đổi luồng bán có kiểm chứng, hoặc tiền thực nhận.\n"
    )
    return tg_msg, md_content


def run_once(send_tele: bool = True) -> dict:
    diag = run_diagnostics()
    tg_msg, md_content = generate_daily_brief(diag)

    brief_file = REPO_ROOT / "operations" / "DAILY_BRIEF.md"
    brief_file.parent.mkdir(parents=True, exist_ok=True)
    brief_file.write_text(md_content, encoding="utf-8")
    logger.info(f"Updated {brief_file}")

    if send_tele:
        res = send_telegram_alert(tg_msg)
        logger.info(f"Sent Telegram Daily Brief: {res.get('ok')}")

    return diag


def daemon_loop():
    logger.info("Starting WINK Revenue Watchdog Daemon loop...")
    run_once(send_tele=True)

    while True:
        try:
            now_utc = datetime.now(timezone.utc)
            # Check every 30 minutes
            import time
            time.sleep(1800)
            now_ict_hour = (now_utc.hour + 7) % 24
            now_ict_minute = now_utc.minute
            if now_ict_hour in (8, 20) and now_ict_minute < 35:
                run_once(send_tele=True)
        except Exception as e:
            logger.error(f"Error in daemon loop: {e}")
            import time
            time.sleep(60)


if __name__ == "__main__":
    if "--daemon" in sys.argv:
        daemon_loop()
    else:
        run_once(send_tele=True)
