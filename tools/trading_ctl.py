"""Trading Controller CLI & Deterministic Bridge.

Provides a fast, zero-dependency interface to inspect and control
the autonomous MT5 trading daemon running on the Windows host.
Can be safely executed by Agent Zero inside Docker or by humans in terminal.
Zero external library requirements (does NOT import MetaTrader5).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def get_repo_root() -> Path:
    # Try finding repo root from script location or common mount paths
    cur = Path(__file__).resolve().parent.parent
    if (cur / "trading-agent-exness-demo").exists():
        return cur
    # Docker mount fallback
    alt = Path("/a0/usr/projects/money-hq")
    if alt.exists():
        return alt
    return cur


REPO_ROOT = get_repo_root()
RUN_STATE_FILE = REPO_ROOT / "trading-agent-exness-demo" / "run_state.json"
JOURNAL_FILE = REPO_ROOT / "trading-agent-exness-demo" / "research" / "LIVE_DEMO_JOURNAL.md"


def load_state() -> dict:
    if not RUN_STATE_FILE.exists():
        return {}
    try:
        return json.loads(RUN_STATE_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"Failed to read run_state.json: {e}"}


def save_state(state: dict) -> bool:
    tmp_path = RUN_STATE_FILE.with_suffix(".tmp")
    try:
        tmp_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp_path.replace(RUN_STATE_FILE)
        return True
    except Exception as e:
        print(f"Error saving state: {e}", file=sys.stderr)
        return False


def format_status(state: dict, as_json: bool = False) -> str:
    if as_json:
        return json.dumps(state, indent=2, ensure_ascii=False)

    if not state:
        return (
            "⚠️ <b>CHƯA CÓ TRẠNG THÁI RUN_STATE.JSON</b>\n"
            "Daemon giao dịch MT5 trên Windows Host chưa được khởi tạo."
        )

    status = state.get("status", "UNKNOWN")
    active = state.get("active", False)
    command = state.get("command", "none")
    heartbeat_str = state.get("last_heartbeat_utc", "")

    # Calculate heartbeat freshness
    age_sec = -1
    if heartbeat_str:
        try:
            hb_dt = datetime.fromisoformat(heartbeat_str)
            now_dt = datetime.now(timezone.utc)
            age_sec = int((now_dt - hb_dt).total_seconds())
        except Exception:
            pass

    if age_sec >= 0:
        if age_sec < 60:
            hb_label = f"🟢 Vừa cập nhật ({age_sec}s trước)"
        elif age_sec < 300:
            hb_label = f"🟡 Bình thường ({age_sec}s trước)"
        else:
            hb_label = f"🔴 Mất tín hiệu ({age_sec}s trước - daemon có thể đã tắt trên Windows Host)"
    else:
        hb_label = "⚪ Chưa có thông tin"

    account = state.get("account", {})
    login = account.get("login", "N/A")
    server = account.get("server", "N/A")
    balance = account.get("balance", 0.0)
    equity = account.get("equity", 0.0)
    mode = account.get("trade_mode_label", "DEMO")

    risk = state.get("risk", {})
    daily_pnl = risk.get("daily_pnl_pct", 0.0)
    drawdown = risk.get("drawdown_pct", 0.0)

    open_pos = state.get("open_positions", [])

    lines = [
        "📊 <b>TRẠNG THÁI BOT GIAO DỊCH (EXNESS DEMO):</b>",
        f"• <b>Trạng thái:</b> <code>{status}</code> (Lệnh điều khiển: <code>{command}</code>)",
        f"• <b>Heartbeat:</b> {hb_label}",
        f"• <b>Tài khoản:</b> #{login} ({server} - <b>{mode} ONLY</b>)",
        f"• <b>Số dư (Balance):</b> ${balance:,.2f} USD",
        f"• <b>Tài sản ròng (Equity):</b> ${equity:,.2f} USD",
        f"• <b>Lãi/lỗ hôm nay:</b> {daily_pnl:+.2f}%",
        f"• <b>Sụt giảm (Drawdown):</b> {drawdown:.2f}%",
        f"• <b>Lệnh đang mở:</b> {len(open_pos)} lệnh",
        "• <b>Cặp tiền hoạt động:</b> <code>EURUSD</code>",
        "• <b>Chiến lược:</b> Trend-Following Pullback (H4 Trend EMA 50/200 + H1 Pullback EMA 21/50 + Rejection Trigger)",
        "• <b>Nguyên tắc an toàn:</b> Khóa rủi ro cố định 0.25%/lệnh, SL cứng, chặn tài khoản Real.",
    ]

    if open_pos:
        lines.append("\n<b>Chi tiết lệnh đang mở:</b>")
        for p in open_pos:
            t = p.get("type", "N/A")
            sym = p.get("symbol", "N/A")
            vol = p.get("volume", 0.0)
            entry = p.get("price_open", 0.0)
            sl = p.get("sl", 0.0)
            tp = p.get("tp", 0.0)
            pnl = p.get("profit", 0.0)
            lines.append(f"- #{p.get('ticket')}: {t} {vol} lot {sym} @ {entry} (SL: {sl}, TP: {tp}, Lãi: ${pnl:+.2f})")

    return "\n".join(lines)


def cmd_status(args: argparse.Namespace) -> int:
    state = load_state()
    print(format_status(state, as_json=args.json))
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    state = load_state()
    state["command"] = "start"
    state["active"] = True
    if state.get("status") == "PAUSED":
        state["status"] = "RUNNING"
    save_state(state)
    print("✅ Đã thiết lập lệnh START cho bot trading trong run_state.json.")
    print("Daemon trên Windows Host sẽ tự động nhận lệnh trong chu kỳ quét tiếp theo.")
    print("\n" + format_status(state, as_json=args.json))
    return 0


def cmd_pause(args: argparse.Namespace) -> int:
    state = load_state()
    state["command"] = "pause"
    state["status"] = "PAUSED"
    state["active"] = False
    save_state(state)
    print("⏸️ Đã tạm dừng quét tín hiệu giao dịch mới (PAUSED).")
    print("\n" + format_status(state, as_json=args.json))
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    state = load_state()
    state["command"] = "stop"
    state["status"] = "STOPPED"
    state["active"] = False
    save_state(state)
    print("⏹️ Đã phát lệnh STOP cho daemon giao dịch trong run_state.json.")
    print("\n" + format_status(state, as_json=args.json))
    return 0


def cmd_journal(args: argparse.Namespace) -> int:
    if not JOURNAL_FILE.exists():
        print("Chưa có nhật ký giao dịch LIVE_DEMO_JOURNAL.md.")
        return 0
    lines = JOURNAL_FILE.read_text(encoding="utf-8").splitlines()
    count = args.lines or 20
    tail = lines[-count:]
    print("\n".join(tail))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Money HQ MT5 Trading Controller")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    subparsers = parser.add_subparsers(dest="command")

    sub_status = subparsers.add_parser("status", help="Get daemon and account status")
    sub_status.set_defaults(func=cmd_status)

    sub_start = subparsers.add_parser("start", help="Resume or start trading daemon")
    sub_start.set_defaults(func=cmd_start)

    sub_pause = subparsers.add_parser("pause", help="Pause new trades without exiting daemon")
    sub_pause.set_defaults(func=cmd_pause)

    sub_stop = subparsers.add_parser("stop", help="Stop daemon completely")
    sub_stop.set_defaults(func=cmd_stop)

    sub_journal = subparsers.add_parser("journal", help="View recent trading journal entries")
    sub_journal.add_argument("-n", "--lines", type=int, default=20, help="Number of lines")
    sub_journal.set_defaults(func=cmd_journal)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        return cmd_status(args)

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
