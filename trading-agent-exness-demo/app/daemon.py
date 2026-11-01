"""Autonomous Trading Daemon (Milestone M2) — Runs on Windows Host with MT5 Terminal.

Monitors enabled symbols, checks Data Quality Gate, evaluates quantitative strategy,
places demo orders with hard SL/TP, and records state to run_state.json and LIVE_DEMO_JOURNAL.md.
Controlled by setting 'command' in run_state.json ('start' | 'stop').
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AGENT_ROOT = Path(__file__).resolve().parents[1]
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import load_config
from app.data.quality_gate import DataQualityGate, DataQualityError, is_market_closed_weekend
from app.logging_setup import setup_logging
from app.mt5.connection import MT5ConnectionManager, MT5ConnectionError, LiveAccountBlockedError
from app.mt5.market_data import MT5MarketDataReader
from app.mt5.execution import DemoExecutionAdapter, OrderResult
from app.risk.kill_switch import KillSwitch
from app.strategies.baseline import BaselineMultiSymbolStrategy

STATE_FILE = AGENT_ROOT / "run_state.json"
JOURNAL_FILE = AGENT_ROOT / "research" / "LIVE_DEMO_JOURNAL.md"


def load_run_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "status": "STOPPED",
        "active": False,
        "command": "start",
        "last_heartbeat_utc": None,
        "account": None,
        "open_positions": [],
        "recent_trades": [],
    }


def save_run_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def append_journal_entry(title: str, content: str) -> None:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"\n### [{now_str}] {title}\n{content}\n"
    if not JOURNAL_FILE.exists():
        JOURNAL_FILE.write_text("# Money HQ Live Demo Trading Journal\n", encoding="utf-8")
    with JOURNAL_FILE.open("a", encoding="utf-8") as f:
        f.write(entry)


def send_alert_safe(msg: str) -> None:
    try:
        from tools.telegram_notify import send_telegram_alert
        send_telegram_alert(msg)
    except Exception as e:
        logging.getLogger("trading_agent.daemon").warning(f"Failed to send Telegram alert: {e}")


def run_daemon_loop(config_path: str = "config/demo.yaml", loop_interval_sec: int = 30) -> None:
    logger = setup_logging(os.environ.get("LOG_LEVEL", "INFO"))
    logger.info("Initializing Autonomous Trading Daemon on Windows host...")

    config = load_config(AGENT_ROOT / config_path)
    kill_switch = KillSwitch(enabled=config.safety.kill_switch)
    conn = MT5ConnectionManager(config=config)

    account_meta = conn.connect()
    reader = MT5MarketDataReader(connection=conn, config=config)
    gate = DataQualityGate(config=config)
    adapter = DemoExecutionAdapter(config=config, connection=conn, kill_switch=kill_switch)
    strategy = BaselineMultiSymbolStrategy()

    logger.info(
        f"Connected to MT5 Demo: #{account_meta.login} ({account_meta.server}) Balance=${account_meta.balance:.2f}"
    )

    state = load_run_state()
    state["status"] = "RUNNING"
    state["active"] = True
    state["account"] = asdict(account_meta)
    save_run_state(state)

    append_journal_entry(
        "Daemon Started",
        f"- **Account:** #{account_meta.login} ({account_meta.server})\n"
        f"- **Balance:** ${account_meta.balance:.2f} {account_meta.currency}\n"
        f"- **Mode:** {config.execution_mode}\n"
        f"- **Enabled Symbols:** {', '.join(config.symbols.enabled) or 'None'}\n"
    )

    send_alert_safe(
        f"🚀 <b>AUTONOMOUS TRADING DAEMON KHỞI ĐỘNG!</b>\n\n"
        f"• Tài khoản: <code>#{account_meta.login}</code> (Demo)\n"
        f"• Server: <code>{account_meta.server}</code>\n"
        f"• Vốn ảo: <b>${account_meta.balance:,.2f} USD</b>\n"
        f"• Cặp theo dõi: <code>{', '.join(config.symbols.enabled)}</code>\n"
        f"• Rủi ro/lệnh: <b>{config.risk.risk_per_trade_pct}%</b>\n"
        f"• Trạng thái: Đang quét thị trường..."
    )

    try:
        while True:
            state = load_run_state()
            if state.get("command") == "stop":
                logger.info("Received 'stop' command. Halting daemon.")
                state["status"] = "STOPPED"
                state["active"] = False
                save_run_state(state)
                send_alert_safe("⏹️ <b>AUTONOMOUS TRADING DAEMON ĐÃ TẠM DỪNG!</b>")
                break

            now_utc = datetime.now(timezone.utc)
            state["last_heartbeat_utc"] = now_utc.isoformat()

            # Update account info
            try:
                acc_info = conn.read_account_metadata()
                state["account"] = asdict(acc_info)
            except Exception as e:
                logger.warning(f"Could not refresh account info: {e}")

            # Check open positions
            try:
                positions = adapter.get_open_positions()
                pos_list = []
                for p in positions:
                    pos_list.append({
                        "ticket": p.ticket,
                        "symbol": p.symbol,
                        "type": "BUY" if p.type == 0 else "SELL",
                        "volume": p.volume,
                        "price_open": p.price_open,
                        "sl": p.sl,
                        "tp": p.tp,
                        "profit": p.profit,
                    })
                state["open_positions"] = pos_list
            except Exception as e:
                logger.warning(f"Could not read open positions: {e}")

            # Scan enabled symbols
            for base_sym in config.symbols.enabled:
                try:
                    spec = reader.read_symbol_spec(base_sym)
                    tick = reader.read_tick(base_sym)
                    candles = reader.read_candles(base_sym, "M15", count=60)

                    # Quality gate check
                    gate.evaluate(base_sym, "M15", tick, candles, now_utc=now_utc)

                    # Evaluate strategy
                    signal = strategy.generate_signal(candles)
                    if signal.direction in ("BUY", "SELL"):
                        logger.info(f"Signal detected for {spec.broker_symbol}: {signal.direction} @ {signal.entry_price}")
                        # Place order
                        order_res: OrderResult = adapter.place_order(signal, spec)
                        if order_res.success:
                            trade_msg = (
                                f"📈 <b>VÀO LỆNH DEMO THÀNH CÔNG!</b>\n\n"
                                f"• Mã: <b>{order_res.symbol}</b>\n"
                                f"• Chiều: <b>{order_res.direction}</b>\n"
                                f"• Khối lượng: <b>{order_res.volume} lot</b>\n"
                                f"• Giá khớp: <b>{order_res.price}</b>\n"
                                f"• Chặn lỗ (SL): <code>{order_res.stop_loss}</code>\n"
                                f"• Chốt lời (TP): <code>{order_res.take_profit}</code>\n"
                                f"• Vé lệnh: <code>#{order_res.ticket}</code>"
                            )
                            send_alert_safe(trade_msg)
                            append_journal_entry(
                                f"Order Executed: {order_res.direction} {order_res.symbol}",
                                f"- **Ticket:** #{order_res.ticket}\n"
                                f"- **Volume:** {order_res.volume} lots @ {order_res.price}\n"
                                f"- **SL:** {order_res.stop_loss} | **TP:** {order_res.take_profit}\n"
                                f"- **Signal Reason:** {signal.reason}\n"
                            )
                            state["recent_trades"].append(asdict(order_res))

                except DataQualityError as dqe:
                    if is_market_closed_weekend(base_sym, now_utc):
                        pass # Normal weekend closure, wait silently
                    else:
                        logger.warning(f"Data quality error for {base_sym}: {dqe}")
                except Exception as e:
                    logger.warning(f"Scan error on {base_sym}: {e}")

            save_run_state(state)
            time.sleep(loop_interval_sec)

    except KeyboardInterrupt:
        logger.info("Daemon interrupted by user.")
    finally:
        state["status"] = "STOPPED"
        state["active"] = False
        save_run_state(state)
        conn.shutdown()
        logger.info("Daemon shutdown cleanly.")


if __name__ == "__main__":
    run_daemon_loop()
