# MT5 AUTONOMOUS TRADING AGENT (EXNESS DEMO) — AUDIT DOSSIER

> **Mục đích:** Tài liệu kỹ thuật tổng hợp toàn bộ mã nguồn, cấu hình và kiểm thử của hệ thống MT5 trading bot để gửi cho AI độc lập (ChatGPT / Claude / Grok) thực hiện adversarial audit phản biện đa chiều.

## 1. THÔNG TIN HỆ THỐNG & NGUYÊN TẮC BẤT BIẾN (INVARIANTS)
- **Môi trường hoạt động:** DEMO ONLY (`Exness-MT5Trial17`, Login `#464160066`, Balance `$100,000 USD`).
- **Chặn Live Account:** Khóa cứng ở tầng Execution Adapter, kiểm tra `trade_mode == DEMO`, `trade_allowed`, `trade_expert`, chặn tên server chứa 'real/live'.
- **Quản trị rủi ro cố định:** 0.25%/lệnh, SL cứng bắt buộc mọi lệnh, làm tròn lot XUỐNG (`math.floor`), từ chối lệnh nếu `min_vol` vượt ngân sách rủi ro.
- **Cross-check MT5 Native:** Gọi `order_calc_profit()` đối soát với broker trước khi gửi lệnh.
- **Tách quyền hạn:** Strategy chỉ sinh Signal(entry, sl, tp, reason), KHÔNG có quyền đặt lệnh hay tính volume.
- **Bảo toàn trạng thái qua Restart:** KillSwitch và RiskManager ghi trạng thái ra file đĩa nguyên tử.

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN
```text
trading-agent-exness-demo/
├── app
│   ├── data
│   │   ├── __init__.py
│   │   └── quality_gate.py
│   ├── evaluation
│   │   ├── performance.py
│   │   └── run_backtest_audit.py
│   ├── journal
│   │   └── repository.py
│   ├── mt5
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── execution.py
│   │   └── market_data.py
│   ├── portfolio
│   │   └── exposure.py
│   ├── risk
│   │   ├── __init__.py
│   │   ├── kill_switch.py
│   │   └── manager.py
│   ├── strategies
│   │   ├── base.py
│   │   ├── baseline.py
│   │   └── trend_pullback.py
│   ├── __init__.py
│   ├── config.py
│   ├── daemon.py
│   ├── logging_setup.py
│   └── main.py
├── config
│   └── demo.yaml
├── research
│   ├── ARCHITECTURE.md
│   ├── BACKTEST_REPORT.md
│   ├── CANDIDATE_STRATEGIES.md
│   ├── GEMINI_INDEPENDENT_AUDIT.md
│   ├── KNOWLEDGE_BASE.md
│   ├── LIVE_DEMO_JOURNAL.md
│   ├── M0_M1_VERIFICATION_REPORT.md
│   └── STRATEGY_SPEC.md
├── tests
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_data_quality.py
│   ├── test_execution.py
│   ├── test_mt5_connection.py
│   ├── test_risk.py
│   └── test_strategy_backtest.py
├── tools
│   └── run_gemini_audit.py
├── README.md
├── requirements.txt
├── risk_state.json
└── run_state.json
```

## 3. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG (PYTEST TEST SUITE)
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\ACER\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\ACER\Documents\Codex\revenue-copilot-international-phase0
configfile: pytest.ini
plugins: anyio-4.12.1, langsmith-0.14.1
collecting ... collected 47 items

tests\test_config.py::test_load_default_demo_yaml PASSED                 [  2%]
tests\test_config.py::test_reject_demo_only_false_in_env PASSED          [  4%]
tests\test_config.py::test_reject_live_account_mode PASSED               [  6%]
tests\test_config.py::test_reject_disabled_live_account_blocker PASSED   [  8%]
tests\test_config.py::test_reject_enabled_symbols_in_m0_m1 PASSED        [ 10%]
tests\test_config.py::test_reject_enabled_symbol_not_in_allowlist PASSED [ 12%]
tests\test_config.py::test_reject_invalid_session_config PASSED          [ 14%]
tests\test_data_quality.py::test_valid_tick_and_candles_pass PASSED      [ 17%]
tests\test_data_quality.py::test_stale_tick_is_rejected PASSED           [ 19%]
tests\test_data_quality.py::test_excessive_spread_is_rejected PASSED     [ 21%]
tests\test_data_quality.py::test_missing_intra_session_candle_gap_is_rejected PASSED [ 23%]
tests\test_data_quality.py::test_stale_candle_series_is_rejected PASSED  [ 25%]
tests\test_execution.py::test_execution_adapter_blocks_all_order_operations_in_m0_m1 PASSED [ 27%]
tests\test_execution.py::test_calculate_lot_size_gold_xauusd PASSED      [ 29%]
tests\test_execution.py::test_calculate_lot_size_forex_eurusd PASSED     [ 31%]
tests\test_execution.py::test_calculate_lot_size_fails_closed_when_stop_loss_missing PASSED [ 34%]
tests\test_execution.py::test_calculate_lot_size_strictly_rounds_down PASSED [ 36%]
tests\test_execution.py::test_calculate_lot_size_rejects_order_if_min_vol_exceeds_risk_budget PASSED [ 38%]
tests\test_execution.py::test_ensure_can_execute_fails_when_trade_not_allowed PASSED [ 40%]
tests\test_execution.py::test_ensure_can_execute_fails_when_trade_expert_disabled PASSED [ 42%]
tests\test_execution.py::test_calculate_lot_size_ratchets_down_when_order_calc_profit_exceeds_budget PASSED [ 44%]
tests\test_execution.py::test_calculate_lot_size_fails_closed_when_order_calc_profit_returns_none PASSED [ 46%]
tests\test_execution.py::test_calculate_lot_size_fails_closed_when_broker_risk_exceeds_budget_after_ratchet PASSED [ 48%]
tests\test_execution.py::test_calculate_lot_size_fails_closed_when_order_calc_profit_returns_non_negative PASSED [ 51%]
tests\test_execution.py::test_calculate_lot_size_fails_closed_when_backend_missing_order_calc_profit_in_demo_auto PASSED [ 53%]
tests\test_mt5_connection.py::test_unavailable_terminal_raises_clear_error PASSED [ 55%]
tests\test_mt5_connection.py::test_real_account_trade_mode_is_rejected PASSED [ 57%]
tests\test_mt5_connection.py::test_real_server_name_is_rejected_even_if_trade_mode_demo PASSED [ 59%]
tests\test_mt5_connection.py::test_symbol_discovery_and_invalid_symbol_error PASSED [ 61%]
tests\test_mt5_connection.py::test_missing_candles_from_mt5_raises_error PASSED [ 63%]
tests\test_mt5_connection.py::test_full_diagnostic_runner_passes_with_mock_demo_terminal PASSED [ 65%]
tests\test_risk.py::test_kill_switch_cannot_be_disabled PASSED           [ 68%]
tests\test_risk.py::test_kill_switch_trips_and_blocks_operations PASSED  [ 70%]
tests\test_risk.py::test_risk_manager_healthy_under_limits PASSED        [ 72%]
tests\test_risk.py::test_risk_manager_trips_on_daily_loss_limit PASSED   [ 74%]
tests\test_risk.py::test_risk_manager_trips_on_max_drawdown PASSED       [ 76%]
tests\test_risk.py::test_kill_switch_persists_across_restart PASSED      [ 78%]
tests\test_risk.py::test_risk_manager_persists_across_restart PASSED     [ 80%]
tests\test_risk.py::test_risk_manager_trips_on_corrupted_state_file PASSED [ 82%]
tests\test_risk.py::test_risk_manager_trips_when_persist_fails PASSED    [ 85%]
tests\test_risk.py::test_kill_switch_raises_when_persist_fails PASSED    [ 87%]
tests\test_strategy_backtest.py::test_baseline_strategy_returns_flat_on_insufficient_warmup PASSED [ 89%]
tests\test_strategy_backtest.py::test_backtest_evaluator_separates_in_sample_and_out_of_sample_with_costs PASSED [ 91%]
tests\test_strategy_backtest.py::test_trend_pullback_strategy_insufficient_warmup PASSED [ 93%]
tests\test_strategy_backtest.py::test_trend_pullback_strategy_regime_filtering PASSED [ 95%]
tests\test_strategy_backtest.py::test_wilder_adx_filters_choppy_consolidation PASSED [ 97%]
tests\test_strategy_backtest.py::test_pinbar_requires_dominant_lower_wick_and_small_opposite_wick PASSED [100%]

============================= 47 passed in 0.65s ==============================
```

## 4. MÃ NGUỒN CÁC MODULE TRỌNG YẾU

### File: `config/demo.yaml`
- **GitHub Raw:** [config/demo.yaml](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/config/demo.yaml)
```yaml
platform: mt5
account_mode: demo_only
execution_mode: demo_auto

symbols:
  allowed:
    - XAGUSD
    - EURUSD
    - XAUUSD
  enabled:
    - EURUSD

timeframes:
  - H1
  - H4

data_quality:
  max_candle_age_seconds:
    H1: 7200    # 2 hours max staleness for closed H1 candle
    H4: 28800   # 8 hours max staleness for closed H4 candle
  max_tick_age_seconds: 60
  min_candle_count: 50
  max_spread_points:
    XAUUSD: 500
    XAGUSD: 400
    EURUSD: 25
    default: 100

risk:
  risk_per_trade_pct: 0.25
  max_total_open_risk_pct: 0.50
  max_daily_loss_pct: 1.0
  max_drawdown_pct: 5.0
  max_positions_per_symbol: 1

safety:
  require_stop_loss: true
  reject_stale_data: true
  reject_excessive_spread: true
  block_live_accounts: true
  kill_switch: true

session:
  enabled: true
  start_hour_utc: 7
  end_hour_utc: 16

```

### File: `app/daemon.py`
- **GitHub Raw:** [app/daemon.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/app/daemon.py)
```python
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
from app.risk.manager import RiskManager
from app.strategies.trend_pullback import TrendFollowingPullbackStrategy

STATE_FILE = AGENT_ROOT / "run_state.json"
JOURNAL_FILE = AGENT_ROOT / "research" / "LIVE_DEMO_JOURNAL.md"
KILL_SWITCH_FILE = AGENT_ROOT / "kill_switch_state.json"
RISK_STATE_FILE = AGENT_ROOT / "risk_state.json"


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
        "processed_candles": {},
    }


def save_run_state(state: dict[str, Any]) -> None:
    """Atomic write for state persistence (AUDIT-07)."""
    temp_file = STATE_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    temp_file.replace(STATE_FILE)


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
    kill_switch = KillSwitch(enabled=config.safety.kill_switch, state_file=KILL_SWITCH_FILE)
    risk_mgr = RiskManager(config=config, kill_switch=kill_switch, state_file=RISK_STATE_FILE)
    conn = MT5ConnectionManager(config=config)

    account_meta = conn.connect()
    reader = MT5MarketDataReader(connection=conn, config=config)
    gate = DataQualityGate(config=config)
    adapter = DemoExecutionAdapter(config=config, connection=conn, kill_switch=kill_switch)
    strategy = TrendFollowingPullbackStrategy()

    logger.info(
        f"Connected to MT5 Demo: #{account_meta.login} ({account_meta.server}) Balance=${account_meta.balance:.2f} "
        f"| Strategy: {strategy.strategy_id} v{strategy.version}"
    )

    state = load_run_state()
    state["status"] = "RUNNING"
    state["active"] = True
    state["account"] = asdict(account_meta)

    # Reconcile open positions from MT5 terminal upon startup (AUDIT-08)
    initial_positions = adapter.get_open_positions()
    state["open_positions"] = [
        {
            "ticket": p.ticket,
            "symbol": p.symbol,
            "type": "BUY" if p.type == 0 else "SELL",
            "volume": p.volume,
            "price_open": p.price_open,
            "sl": p.sl,
            "tp": p.tp,
            "profit": p.profit,
        }
        for p in initial_positions
    ]
    logger.info(f"Reconciled {len(initial_positions)} open positions from MT5 terminal on startup.")
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

    initial_state = load_run_state()
    last_processed_candles: dict[str, str] = dict(initial_state.get("processed_candles") or {})
    logger.info(f"Restored {len(last_processed_candles)} processed candle timestamp(s) from run_state.json across restart.")

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

            if state.get("command") == "pause":
                if state.get("status") != "PAUSED":
                    logger.info("Received 'pause' command. Pausing trade scan.")
                    state["status"] = "PAUSED"
                    state["active"] = False
                    send_alert_safe("⏸️ <b>AUTONOMOUS TRADING DAEMON ĐÃ TẠM DỪNG QUÉT (PAUSED)!</b>")
                save_run_state(state)
                time.sleep(loop_interval_sec)
                continue
            elif state.get("command") == "start" and state.get("status") == "PAUSED":
                state["status"] = "RUNNING"
                state["active"] = True
                logger.info("Resumed trading daemon from pause.")
                send_alert_safe("▶️ <b>AUTONOMOUS TRADING DAEMON ĐÃ TIẾP TỤC QUÉT TÍN HIỆU!</b>")

            # Update account info and enforce Risk Manager (AUDIT-05)
            try:
                acc_info = conn.read_account_metadata()
                state["account"] = asdict(acc_info)
                risk_state = risk_mgr.evaluate_equity(acc_info.equity)
                state["risk"] = {
                    "daily_pnl_pct": round(risk_state.daily_pnl_pct, 2),
                    "drawdown_pct": round(risk_state.drawdown_pct, 2),
                    "peak_equity": round(risk_state.peak_equity, 2),
                    "day_start_equity": round(risk_state.day_start_equity, 2),
                }
            except Exception as e:
                logger.warning(f"Could not refresh account info or evaluate risk: {e}")

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

            # Enforce Session Filter: active trading window (London + NY overlap, e.g. 07:00-16:00 UTC)
            if config.session.enabled and not (config.session.start_hour_utc <= now_utc.hour < config.session.end_hour_utc):
                logger.info(
                    f"Session Filter: Current time {now_utc.strftime('%H:%M')} UTC is outside "
                    f"active window ({config.session.start_hour_utc:02d}:00-{config.session.end_hour_utc:02d}:00 UTC). "
                    "Skipping market scan."
                )
                save_run_state(state)
                time.sleep(loop_interval_sec)
                continue

            # Scan enabled symbols (EURUSD pilot)
            for base_sym in config.symbols.enabled:
                try:
                    spec = reader.read_symbol_spec(base_sym)
                    tick = reader.read_tick(base_sym)
                    h4_candles = reader.read_candles(base_sym, "H4", count=60)
                    h1_candles = reader.read_candles(base_sym, "H1", count=60)

                    # Quality gate check on H1 candles
                    gate.evaluate(base_sym, "H1", tick, h1_candles, now_utc=now_utc)

                    # Guarantee candle bar idempotency (AUDIT-03) on closed H1 bar
                    last_bar_time = h1_candles[-1].open_time_utc.isoformat()
                    if last_processed_candles.get(base_sym) == last_bar_time:
                        continue

                    # Mark closed bar as evaluated and persist immediately to run_state.json across restarts
                    last_processed_candles[base_sym] = last_bar_time
                    state["processed_candles"] = last_processed_candles
                    save_run_state(state)

                    # Evaluate 4-tier H4/H1 trend pullback strategy
                    signal = strategy.evaluate(base_sym, h4_candles, h1_candles)
                    if signal.direction in ("BUY", "SELL"):
                        logger.info(f"Signal detected for {spec.broker_symbol}: {signal.direction} @ {signal.entry_price} ({signal.reason})")
                        # Place order
                        order_res: OrderResult = adapter.place_order(signal, spec)
                        if order_res.success:
                            trade_msg = (
                                f"📈 <b>VÀO LỆNH DEMO THÀNH CÔNG!</b>\n\n"
                                f"• Mã: <b>{order_res.symbol}</b>\n"
                                f"• Chiến thuật: <b>H4/H1 Trend-Following Pullback</b>\n"
                                f"• Chiều: <b>{order_res.direction}</b>\n"
                                f"• Khối lượng: <b>{order_res.volume} lot</b>\n"
                                f"• Giá khớp: <b>{order_res.price}</b>\n"
                                f"• Chặn lỗ (SL): <code>{order_res.stop_loss}</code>\n"
                                f"• Chốt lời (TP): <code>{order_res.take_profit}</code>\n"
                                f"• Vé lệnh: <code>#{order_res.ticket}</code>\n"
                                f"• Lý do: <i>{signal.reason}</i>"
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

```

### File: `app/mt5/execution.py`
- **GitHub Raw:** [app/mt5/execution.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/app/mt5/execution.py)
```python
"""Execution adapter for Exness MT5 Demo Trading Engine (Milestone M2 Autonomous Execution)."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any

from app.config import AppConfig
from app.mt5.connection import ACCOUNT_TRADE_MODE_DEMO, MT5ConnectionManager
from app.mt5.market_data import SymbolSpec
from app.risk.kill_switch import KillSwitch
from app.strategies.base import StrategySignal

logger = logging.getLogger("trading_agent.mt5.execution")


class ReadOnlyExecutionError(PermissionError):
    """Raised on any attempt to place, modify, or close orders during read_only mode."""


class ExecutionSafetyError(RuntimeError):
    """Raised when an execution safety rule is violated."""


@dataclass(frozen=True)
class OrderResult:
    ticket: int
    symbol: str
    direction: str
    volume: float
    price: float
    stop_loss: float
    take_profit: float
    comment: str
    retcode: int
    success: bool
    message: str


class DemoExecutionAdapter:
    """Safely executes orders on a verified MT5 DEMO terminal with strict risk sizing."""

    def __init__(
        self,
        config: AppConfig | None = None,
        connection: MT5ConnectionManager | None = None,
        kill_switch: KillSwitch | None = None,
    ) -> None:
        self._config = config
        self._connection = connection
        self._kill_switch = kill_switch

    def _ensure_can_execute(self) -> Any:
        if self._config is None or self._config.execution_mode == "read_only":
            raise ReadOnlyExecutionError(
                "SAFETY LOCK: Order placement is disabled in Milestone M0-M1 (Read-Only Connector)."
            )
        if self._connection is None or not self._connection.is_connected:
            raise ExecutionSafetyError("Cannot execute: MT5 connection is not initialized.")
        if self._kill_switch is not None:
            self._kill_switch.assert_healthy()

        account_meta = self._connection.read_account_metadata()
        if account_meta.trade_mode != ACCOUNT_TRADE_MODE_DEMO or not account_meta.is_verified_demo:
            raise ExecutionSafetyError(
                f"SAFETY LOCK: Live/real accounts are strictly blocked. Got trade_mode={account_meta.trade_mode_label}"
            )
        if not account_meta.trade_allowed:
            raise ExecutionSafetyError(
                f"SAFETY LOCK: Trade is not allowed for account #{account_meta.login} on MT5 terminal."
            )
        if not account_meta.trade_expert:
            raise ExecutionSafetyError(
                "SAFETY LOCK: Automated trading (Expert Advisors / Algo) is disabled in MT5 terminal."
            )
        return self._connection.backend

    def calculate_lot_size(
        self,
        signal: StrategySignal,
        spec: SymbolSpec,
        account_balance: float,
    ) -> float:
        """Calculate lot size based on fixed fractional risk and ATR stop distance with accurate tick value.
        
        Strictly rounds DOWN (floor) to ensure cash risk never exceeds the configured risk budget.
        Fails closed if configuration, entry price, or stop loss is missing.
        """
        import math

        if not self._config:
            raise ExecutionSafetyError("Safety violation: ExecutionAdapter has no AppConfig configured.")

        if signal.entry_price is None or signal.stop_loss is None:
            raise ExecutionSafetyError("Safety violation: Signal must have explicit entry_price and stop_loss.")

        stop_dist = abs(signal.entry_price - signal.stop_loss)
        if stop_dist <= 0:
            raise ExecutionSafetyError(f"Safety violation: Stop distance must be positive, got {stop_dist}")

        risk_pct = self._config.risk.risk_per_trade_pct
        risk_cash = account_balance * (risk_pct / 100.0)

        mt5 = self._connection.backend if self._connection else None
        min_vol = 0.01
        max_vol = 10.0
        step_vol = 0.01
        tick_size = 0.01
        tick_value = spec.contract_size * tick_size if spec.contract_size > 0 else 1.0

        if mt5:
            info = mt5.symbol_info(spec.broker_symbol)
            if info:
                min_vol = getattr(info, "volume_min", 0.01) or 0.01
                max_vol = getattr(info, "volume_max", 10.0) or 10.0
                step_vol = getattr(info, "volume_step", 0.01) or 0.01
                info_tick_size = getattr(info, "trade_tick_size", None)
                if info_tick_size and info_tick_size > 0:
                    tick_size = info_tick_size
                elif getattr(info, "digits", None):
                    tick_size = 10 ** (-info.digits)
                
                info_tick_val = getattr(info, "trade_tick_value", None)
                if info_tick_val and info_tick_val > 0:
                    tick_value = info_tick_val
                elif spec.contract_size > 0:
                    tick_value = spec.contract_size * tick_size

        if tick_size <= 0:
            tick_size = 0.01
        if tick_value <= 0:
            tick_value = 1.0

        cash_risk_per_lot = (stop_dist / tick_size) * tick_value
        if cash_risk_per_lot <= 0:
            raise ExecutionSafetyError(f"Safety violation: Cash risk per lot is non-positive ({cash_risk_per_lot})")

        raw_lots = risk_cash / cash_risk_per_lot

        # Strictly floor (round DOWN) to volume step so risk budget is never breached
        # Using round(..., 8) avoids binary floating-point representation errors (e.g. 1.0 / 0.01 == 99.99999999999999)
        decimals = max(0, -int(math.floor(math.log10(step_vol)))) if step_vol > 0 else 2
        steps = math.floor(round(raw_lots / step_vol, 8))
        lots = round(steps * step_vol, decimals)

        # Enforce minimum broker volume constraint: if min_vol risks more than risk_cash, reject order!
        if lots < min_vol:
            min_lot_cash_risk = min_vol * cash_risk_per_lot
            if min_lot_cash_risk > risk_cash:
                raise ExecutionSafetyError(
                    f"Risk limit rejected: Minimum broker volume ({min_vol}) risks ${min_lot_cash_risk:.2f}, "
                    f"which exceeds the maximum allowed risk budget of ${risk_cash:.2f}."
                )
            lots = min_vol

        # Cross-validate with MT5 internal order_calc_profit if terminal backend is available
        if mt5 and signal.entry_price and signal.stop_loss:
            if not hasattr(mt5, "order_calc_profit"):
                if self._config and self._config.execution_mode == "demo_auto":
                    raise ExecutionSafetyError("Safety violation: MT5 backend missing required order_calc_profit method in demo_auto mode.")
            else:
                mt5_type = 0 if signal.direction == "BUY" else 1
                try:
                    calc_pnl = mt5.order_calc_profit(mt5_type, spec.broker_symbol, lots, signal.entry_price, signal.stop_loss)
                except Exception as e:
                    raise ExecutionSafetyError(f"order_calc_profit check failed with exception: {e}")

                if calc_pnl is None:
                    raise ExecutionSafetyError(
                        f"order_calc_profit returned None for {spec.broker_symbol} (action={mt5_type}, lots={lots}, "
                        f"entry={signal.entry_price}, sl={signal.stop_loss}). Terminal cannot calculate monetary risk."
                    )

                if calc_pnl >= 0:
                    raise ExecutionSafetyError(
                        f"order_calc_profit returned non-negative PnL ({calc_pnl}) at Stop Loss for {spec.broker_symbol}. "
                        "Anomalous quote or inverted SL rejected."
                    )

                sim_cash_risk = abs(calc_pnl)
                while sim_cash_risk > risk_cash * 1.0001 and steps > 1:
                    steps -= 1
                    lots = round(steps * step_vol, decimals)
                    calc_pnl = mt5.order_calc_profit(mt5_type, spec.broker_symbol, lots, signal.entry_price, signal.stop_loss)
                    if calc_pnl is None:
                        raise ExecutionSafetyError("order_calc_profit returned None during lot size ratcheting.")
                    sim_cash_risk = abs(calc_pnl)

                # Final post-ratchet risk budget verification (AUDIT P0: ensure min step does not exceed budget)
                if sim_cash_risk > risk_cash * 1.0001:
                    raise ExecutionSafetyError(
                        f"Broker-calculated risk (${sim_cash_risk:.2f}) still exceeds risk budget (${risk_cash:.2f}) "
                        f"after lot reduction to minimum steps ({lots} lots). Order rejected."
                    )

        lots = min(lots, max_vol)
        return lots

    def get_open_positions(self, broker_symbol: str | None = None) -> list[Any]:
        """Fetch current open positions on MT5 terminal."""
        mt5 = self._ensure_can_execute()
        if broker_symbol:
            positions = mt5.positions_get(symbol=broker_symbol)
        else:
            positions = mt5.positions_get()
        return list(positions) if positions else []

    def place_order(
        self,
        signal: StrategySignal | None = None,
        spec: SymbolSpec | None = None,
        **kwargs: Any,
    ) -> OrderResult:
        """Execute a market order on MT5 Demo with hard stop-loss and take-profit."""
        mt5 = self._ensure_can_execute()

        if signal is None or spec is None:
            raise ReadOnlyExecutionError(
                "SAFETY LOCK: Order placement is disabled in Milestone M0-M1 (Read-Only Connector)."
            )

        if signal.direction not in ("BUY", "SELL"):
            return OrderResult(
                ticket=0,
                symbol=spec.broker_symbol,
                direction="FLAT",
                volume=0.0,
                price=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                comment="Skipped FLAT signal",
                retcode=0,
                success=False,
                message="Direction is FLAT",
            )

        # Check existing open positions
        open_pos = self.get_open_positions(spec.broker_symbol)
        max_pos = self._config.risk.max_positions_per_symbol if self._config else 1
        if len(open_pos) >= max_pos:
            logger.info(
                f"Position limit reached for {spec.broker_symbol}: open={len(open_pos)}, max={max_pos}"
            )
            return OrderResult(
                ticket=0,
                symbol=spec.broker_symbol,
                direction=signal.direction,
                volume=0.0,
                price=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                comment="Max positions limit reached",
                retcode=0,
                success=False,
                message="Position limit reached",
            )

        # Require stop loss
        if self._config and self._config.safety.require_stop_loss and not signal.stop_loss:
            raise ExecutionSafetyError("Safety violation: stop_loss is required for all orders.")

        account_meta = self._connection.read_account_metadata()
        lots = self.calculate_lot_size(signal, spec, account_meta.balance)

        tick = mt5.symbol_info_tick(spec.broker_symbol)
        if not tick:
            raise ExecutionSafetyError(f"No live tick available for {spec.broker_symbol}")

        is_buy = signal.direction == "BUY"
        order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL
        price = tick.ask if is_buy else tick.bid

        # Dynamic filling mode fallback (AUDIT-04)
        filling_mode = getattr(mt5, "ORDER_FILLING_IOC", 1)
        sym_info = mt5.symbol_info(spec.broker_symbol)
        if sym_info:
            flags = getattr(sym_info, "filling_mode", 0)
            if flags & 2:  # SYMBOL_FILLING_IOC
                filling_mode = getattr(mt5, "ORDER_FILLING_IOC", 1)
            elif flags & 1:  # SYMBOL_FILLING_FOK
                filling_mode = getattr(mt5, "ORDER_FILLING_FOK", 0)
            elif hasattr(mt5, "ORDER_FILLING_RETURN"):
                filling_mode = getattr(mt5, "ORDER_FILLING_RETURN", 2)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": spec.broker_symbol,
            "volume": lots,
            "type": order_type,
            "price": price,
            "sl": float(signal.stop_loss or 0.0),
            "tp": float(signal.take_profit or 0.0),
            "deviation": 25,
            "magic": 889100,
            "comment": "MoneyHQ_AutoTrade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }

        result = mt5.order_send(request)
        if result is None:
            err = mt5.last_error()
            raise ExecutionSafetyError(f"order_send returned None. last_error={err}")

        # Check retcode (10009 = TRADE_RETCODE_DONE, 10008 = TRADE_RETCODE_PLACED)
        success = result.retcode in (10008, 10009)
        order_res = OrderResult(
            ticket=result.order,
            symbol=spec.broker_symbol,
            direction=signal.direction,
            volume=result.volume or lots,
            price=result.price or price,
            stop_loss=signal.stop_loss or 0.0,
            take_profit=signal.take_profit or 0.0,
            comment=result.comment,
            retcode=result.retcode,
            success=success,
            message=result.comment or ("Order executed successfully" if success else "Order failed"),
        )

        logger.info(
            f"Executed order {spec.broker_symbol} {signal.direction} {lots} lots: retcode={result.retcode} ({result.comment})",
            extra={"structured_data": asdict(order_res) if hasattr(order_res, "__dataclass_fields__") else {}},
        )
        return order_res

    def modify_order(
        self,
        ticket: int,
        sl: float | None = None,
        tp: float | None = None,
    ) -> bool:
        """Modify existing position SL/TP on MT5 Demo terminal."""
        mt5 = self._ensure_can_execute()
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            logger.warning(f"Cannot modify position #{ticket}: ticket not found.")
            return False

        pos = positions[0]
        new_sl = float(sl) if sl is not None else float(getattr(pos, "sl", 0.0))
        new_tp = float(tp) if tp is not None else float(getattr(pos, "tp", 0.0))

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": pos.symbol,
            "sl": new_sl,
            "tp": new_tp,
        }
        res = mt5.order_send(request)
        success = res is not None and res.retcode in (10008, 10009)
        if success:
            logger.info(f"Modified position #{ticket}: sl={new_sl}, tp={new_tp}")
        else:
            err = res.comment if res else mt5.last_error()
            logger.warning(f"Failed to modify position #{ticket}: {err}")
        return success

    def close_position(self, ticket: int) -> bool:
        mt5 = self._ensure_can_execute()
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return False
        pos = positions[0]
        is_buy = pos.type == mt5.POSITION_TYPE_BUY
        close_type = mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY
        tick = mt5.symbol_info_tick(pos.symbol)
        if not tick:
            return False
        price = tick.bid if is_buy else tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 25,
            "magic": 889100,
            "comment": "MoneyHQ_AutoClose",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        res = mt5.order_send(request)
        return res is not None and res.retcode in (10008, 10009)

```

### File: `app/risk/manager.py`
- **GitHub Raw:** [app/risk/manager.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/app/risk/manager.py)
```python
"""Risk Manager: continuous monitoring of account equity, daily loss, and drawdown limits.

Persists state to disk to survive unexpected crashes and daemon restarts.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from app.config import AppConfig
from app.risk.kill_switch import KillSwitch

logger = logging.getLogger("trading_agent.risk.manager")


@dataclass
class RiskState:
    current_day: date
    day_start_equity: float
    peak_equity: float
    current_equity: float
    daily_pnl_pct: float
    drawdown_pct: float


class RiskManager:
    """Deterministic risk gatekeeper. Enforces hard daily loss and peak-to-trough drawdown limits with disk persistence."""

    def __init__(
        self,
        config: AppConfig,
        kill_switch: KillSwitch,
        state_file: Path | None = None,
    ) -> None:
        self.config = config
        self.kill_switch = kill_switch
        self._state_file = state_file
        self._current_day: date = datetime.now(timezone.utc).date()
        self._day_start_equity: float | None = None
        self._peak_equity: float | None = None

        # Load persisted risk metrics across restarts
        if self._state_file and self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                saved_day = date.fromisoformat(data["current_day"])
                today = datetime.now(timezone.utc).date()
                if saved_day == today:
                    self._current_day = saved_day
                    self._day_start_equity = float(data["day_start_equity"])
                    self._peak_equity = float(data["peak_equity"])
                    logger.info(
                        f"RiskManager restored today's state: start_equity={self._day_start_equity:.2f}, "
                        f"peak_equity={self._peak_equity:.2f}"
                    )
                else:
                    # New calendar day, keep peak equity but reset day start
                    self._peak_equity = float(data.get("peak_equity", 0.0)) or None
            except Exception as e:
                err_msg = f"FATAL SAFETY TRIP: Could not load RiskManager state from {self._state_file}: {e}. Failing closed."
                logger.critical(err_msg)
                self.kill_switch.trip(reason=err_msg, source="RiskManager.StateFileCorrupted")

    def _persist(self, current_equity: float) -> None:
        if not self._state_file:
            return
        try:
            payload = {
                "current_day": self._current_day.isoformat(),
                "day_start_equity": self._day_start_equity,
                "peak_equity": self._peak_equity,
                "last_equity": current_equity,
                "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            tmp = self._state_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            tmp.replace(self._state_file)
        except Exception as e:
            err_msg = f"FATAL SAFETY TRIP: Failed to persist RiskManager state to {self._state_file}: {e}. Failing closed."
            logger.critical(err_msg)
            self.kill_switch.trip(reason=err_msg, source="RiskManager.StateWriteFailed")
            self.kill_switch.assert_healthy()

    def evaluate_equity(self, current_equity: float) -> RiskState:
        """Evaluate account equity against daily loss and maximum drawdown thresholds."""
        today = datetime.now(timezone.utc).date()

        # Day rollover reset
        if today != self._current_day or self._day_start_equity is None:
            self._current_day = today
            self._day_start_equity = current_equity
            logger.info(
                f"RiskManager: Day start initialized for {today} with equity={self._day_start_equity:.2f}"
            )

        if self._peak_equity is None or current_equity > self._peak_equity:
            self._peak_equity = current_equity

        # Daily loss calculation
        daily_loss_cash = self._day_start_equity - current_equity
        daily_loss_pct = round((daily_loss_cash / self._day_start_equity) * 100.0, 4) if self._day_start_equity > 0 else 0.0

        # Drawdown calculation from peak
        drawdown_cash = self._peak_equity - current_equity
        drawdown_pct = round((drawdown_cash / self._peak_equity) * 100.0, 4) if self._peak_equity > 0 else 0.0

        state = RiskState(
            current_day=self._current_day,
            day_start_equity=self._day_start_equity,
            peak_equity=self._peak_equity,
            current_equity=current_equity,
            daily_pnl_pct=-daily_loss_pct,
            drawdown_pct=drawdown_pct,
        )

        self._persist(current_equity)

        # Enforce max daily loss
        if daily_loss_pct >= self.config.risk.max_daily_loss_pct:
            reason = (
                f"Max daily loss exceeded: current daily drop = {daily_loss_pct:.2f}% "
                f"(limit: {self.config.risk.max_daily_loss_pct:.2f}%)"
            )
            logger.critical(reason)
            self.kill_switch.trip(reason=reason, source="RiskManager.DailyLoss")
            self.kill_switch.assert_healthy()

        # Enforce max peak-to-trough drawdown
        if drawdown_pct >= self.config.risk.max_drawdown_pct:
            reason = (
                f"Max drawdown limit exceeded: current drawdown = {drawdown_pct:.2f}% "
                f"(limit: {self.config.risk.max_drawdown_pct:.2f}%)"
            )
            logger.critical(reason)
            self.kill_switch.trip(reason=reason, source="RiskManager.MaxDrawdown")
            self.kill_switch.assert_healthy()

        return state

```

### File: `app/risk/kill_switch.py`
- **GitHub Raw:** [app/risk/kill_switch.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/app/risk/kill_switch.py)
```python
"""Kill Switch state machine: halts operation when safety, connection, or risk checks fail.

Persists state to disk to prevent crash-restart bypasses.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("trading_agent.risk.kill_switch")


class KillSwitchTrippedError(RuntimeError):
    """Raised when KillSwitch fails to persist or is asserted while active."""
    pass


@dataclass(frozen=True)
class KillSwitchEvent:
    triggered_at_utc: datetime
    reason: str
    source: str


class KillSwitch:
    """Fail-closed kill switch that blocks any further operation once tripped and persists across restarts."""

    def __init__(self, enabled: bool = True, state_file: Path | None = None) -> None:
        if not enabled:
            raise ValueError("Safety violation: KillSwitch cannot be initialized as disabled.")
        self._state_file = state_file
        self._tripped = False
        self._event: KillSwitchEvent | None = None

        # Load persisted state from disk if present
        if self._state_file and self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text(encoding="utf-8"))
                if data.get("tripped"):
                    self._tripped = True
                    evt = data.get("event") or {}
                    self._event = KillSwitchEvent(
                        triggered_at_utc=datetime.fromisoformat(evt["triggered_at_utc"]),
                        reason=evt.get("reason", "Unknown persisted reason"),
                        source=evt.get("source", "persisted"),
                    )
                    logger.warning(
                        f"KillSwitch restored TRIPPED state from {self._state_file}: {self._event.reason}"
                    )
            except Exception as e:
                logger.error(f"Failed to load KillSwitch state from {self._state_file}: {e}")
                # Fail-closed: assume tripped if state file is corrupted
                self._tripped = True
                self._event = KillSwitchEvent(
                    triggered_at_utc=datetime.now(timezone.utc),
                    reason=f"State file corrupted, fail-closed: {e}",
                    source="state_file_error",
                )

    @property
    def is_tripped(self) -> bool:
        return self._tripped

    @property
    def last_event(self) -> KillSwitchEvent | None:
        return self._event

    def _persist(self) -> None:
        if not self._state_file:
            return
        try:
            state_data = {
                "tripped": self._tripped,
                "event": {
                    "triggered_at_utc": self._event.triggered_at_utc.isoformat(),
                    "reason": self._event.reason,
                    "source": self._event.source,
                }
                if self._event
                else None,
            }
            tmp = self._state_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
            tmp.replace(self._state_file)
        except Exception as e:
            err_msg = f"CRITICAL: Could not persist KillSwitch state to {self._state_file}: {e}. Failing closed."
            logger.critical(err_msg)
            raise KillSwitchTrippedError(err_msg) from e

    def trip(self, reason: str, source: str = "system") -> KillSwitchEvent:
        """Trip the kill switch, persist to disk, and record the root cause."""
        if not self._tripped:
            self._tripped = True
            self._event = KillSwitchEvent(
                triggered_at_utc=datetime.now(timezone.utc),
                reason=reason,
                source=source,
            )
            self._persist()
        assert self._event is not None
        return self._event

    def reset_state(self, reason: str, operator: str = "operator") -> None:
        """Explicit manual reset by human operator."""
        logger.warning(f"Manual KillSwitch RESET by {operator}: {reason}")
        self._tripped = False
        self._event = None
        if self._state_file and self._state_file.exists():
            try:
                self._state_file.unlink()
            except Exception as e:
                logger.error(f"Could not remove KillSwitch state file: {e}")

    def assert_healthy(self) -> None:
        """Raise KillSwitchTrippedError if the kill switch has been tripped."""
        if self._tripped and self._event is not None:
            raise KillSwitchTrippedError(
                f"KILL SWITCH ACTIVE [{self._event.source} @ {self._event.triggered_at_utc.isoformat()}]: "
                f"{self._event.reason}"
            )

```

### File: `app/mt5/connection.py`
- **GitHub Raw:** [app/mt5/connection.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/app/mt5/connection.py)
```python
"""MT5 Terminal Connection Manager and Account Metadata Reader (Read-Only)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.config import AppConfig

logger = logging.getLogger("trading_agent.mt5.connection")

# MT5 Constants
ACCOUNT_TRADE_MODE_DEMO = 0
ACCOUNT_TRADE_MODE_CONTEST = 1
ACCOUNT_TRADE_MODE_REAL = 2


class MT5ConnectionError(RuntimeError):
    """Raised when the MT5 terminal is unavailable or fails initialization."""


class LiveAccountBlockedError(PermissionError):
    """Raised when a non-demo (Real/Contest/Unverified) account is detected."""


@dataclass(frozen=True)
class AccountMetadata:
    login: int
    server: str
    trade_mode: int
    trade_mode_label: str
    currency: str
    balance: float
    equity: float
    margin: float
    margin_free: float
    margin_mode: int
    leverage: int
    trade_allowed: bool
    trade_expert: bool
    is_verified_demo: bool


class MT5ConnectionManager:
    """Manages a strictly read-only connection to a verified MT5 DEMO terminal."""

    def __init__(self, config: AppConfig, mt5_backend: Any | None = None) -> None:
        self._config = config
        if mt5_backend is None:
            try:
                import MetaTrader5 as mt5_mod
                self._mt5 = mt5_mod
            except ImportError as exc:
                raise MT5ConnectionError(
                    "MetaTrader5 Python package is not installed or unavailable on this OS."
                ) from exc
        else:
            self._mt5 = mt5_backend
        self._connected = False

    @property
    def backend(self) -> Any:
        return self._mt5

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> AccountMetadata:
        """Initialize MT5 terminal connection and enforce DEMO-only account gate."""
        env = self._config.mt5_env
        init_kwargs: dict[str, Any] = {"timeout": env.timeout_ms}
        if env.terminal_path:
            init_kwargs["path"] = env.terminal_path
        if env.login is not None:
            init_kwargs["login"] = env.login
        if env.password is not None:
            init_kwargs["password"] = env.password
        if env.server is not None:
            init_kwargs["server"] = env.server

        try:
            initialized = self._mt5.initialize(**init_kwargs)
        except Exception as exc:
            self._connected = False
            raise MT5ConnectionError(f"Failed to initialize MT5 terminal: {exc}") from exc

        if not initialized:
            err = self._safe_last_error()
            self._connected = False
            raise MT5ConnectionError(
                f"MT5 terminal unavailable or initialization failed. last_error={err}"
            )

        self._connected = True
        try:
            account_meta = self.read_account_metadata()
        except Exception:
            self.shutdown()
            raise

        logger.info(
            "Connected to verified MT5 DEMO terminal",
            extra={
                "structured_data": {
                    "login": account_meta.login,
                    "server": account_meta.server,
                    "currency": account_meta.currency,
                    "balance": account_meta.balance,
                    "equity": account_meta.equity,
                    "leverage": account_meta.leverage,
                }
            },
        )
        return account_meta

    def read_account_metadata(self) -> AccountMetadata:
        """Read account info and fail closed if the account cannot be verified as DEMO."""
        if not self._connected:
            raise MT5ConnectionError("Cannot read account info: MT5 terminal is not connected.")

        term_info = self._mt5.terminal_info()
        if term_info is None or not getattr(term_info, "connected", False):
            raise MT5ConnectionError(
                "MT5 terminal is not connected to a broker trade server."
            )

        acc = self._mt5.account_info()
        if acc is None:
            err = self._safe_last_error()
            raise MT5ConnectionError(
                f"Failed to retrieve MT5 account_info(). last_error={err}"
            )

        trade_mode = getattr(acc, "trade_mode", None)
        server = str(getattr(acc, "server", "")).strip()
        login = int(getattr(acc, "login", 0))

        if trade_mode != ACCOUNT_TRADE_MODE_DEMO:
            self.shutdown()
            raise LiveAccountBlockedError(
                f"SAFETY LOCK TRIPPED: Account {login} on server '{server}' has "
                f"trade_mode={trade_mode} (expected {ACCOUNT_TRADE_MODE_DEMO}=DEMO). "
                "Live or non-demo accounts are strictly forbidden."
            )

        server_lower = server.lower()
        if "real" in server_lower or "live" in server_lower:
            self.shutdown()
            raise LiveAccountBlockedError(
                f"SAFETY LOCK TRIPPED: Server name '{server}' contains live/real indicator "
                "despite trade_mode flag. Failing closed."
            )

        if not server or login <= 0:
            self.shutdown()
            raise LiveAccountBlockedError(
                "SAFETY LOCK TRIPPED: Account login or server name is missing/uncertain."
            )

        return AccountMetadata(
            login=login,
            server=server,
            trade_mode=trade_mode,
            trade_mode_label="DEMO",
            currency=str(getattr(acc, "currency", "USD")),
            balance=float(getattr(acc, "balance", 0.0)),
            equity=float(getattr(acc, "equity", 0.0)),
            margin=float(getattr(acc, "margin", 0.0)),
            margin_free=float(getattr(acc, "margin_free", 0.0)),
            margin_mode=int(getattr(acc, "margin_mode", 0)),
            leverage=int(getattr(acc, "leverage", 0)),
            trade_allowed=bool(getattr(acc, "trade_allowed", False)),
            trade_expert=bool(getattr(acc, "trade_expert", False)),
            is_verified_demo=True,
        )

    def shutdown(self) -> None:
        """Cleanly close the MT5 terminal connection."""
        if self._connected:
            try:
                self._mt5.shutdown()
            except Exception as exc:
                logger.warning(f"Error during MT5 shutdown: {exc}")
            finally:
                self._connected = False

    def _safe_last_error(self) -> Any:
        try:
            return self._mt5.last_error()
        except Exception:
            return "unknown"

```

### File: `app/strategies/trend_pullback.py`
- **GitHub Raw:** [app/strategies/trend_pullback.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/app/strategies/trend_pullback.py)
```python
"""H4/H1 Trend-Following Pullback Strategy (Milestone M2 Implementation).

Per STRATEGY_SPEC.md v2.0:
- Tier 1: H4 Market Regime (EMA 50 vs EMA 200, ADX 14 >= 20).
- Tier 2: H1 Setup Selection (Pullback to Value Zone between EMA 21 and EMA 50).
- Tier 3: Trigger Bar Confirmation (Rejection Pinbar or Engulfing).
- Tier 4: Structural SL with ATR buffer, Target R:R >= 1:2.0.
"""

from __future__ import annotations

import logging
from typing import Sequence

from app.mt5.market_data import CandleBar
from app.strategies.base import StrategySignal

logger = logging.getLogger("trading_agent.strategies.trend_pullback")


def compute_ema(series: list[float], period: int) -> list[float]:
    """Compute Exponential Moving Average recursively."""
    if len(series) < period:
        return [series[-1] if series else 0.0] * len(series)
    
    alpha = 2.0 / (period + 1)
    ema = [sum(series[:period]) / period]
    for price in series[period:]:
        ema.append(price * alpha + ema[-1] * (1.0 - alpha))
    
    # Pad leading values to match length
    padding = [ema[0]] * (len(series) - len(ema))
    return padding + ema


def compute_atr(candles: Sequence[CandleBar], period: int = 14) -> float:
    """Compute Average True Range for recent candles."""
    if len(candles) < 2:
        return 0.0010
    trs = []
    for i in range(1, len(candles)):
        h = candles[i].high
        l = candles[i].low
        prev_c = candles[i - 1].close
        tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        trs.append(tr)
    recent_trs = trs[-period:] if len(trs) >= period else trs
    return sum(recent_trs) / len(recent_trs) if recent_trs else 0.0010


def compute_adx(candles: Sequence[CandleBar], period: int = 14) -> float:
    """Compute Directional Movement Index (ADX) using Wilder's Smoothing (RMA).
    
    Adheres strictly to Wilder's original recursive formula to prevent rolling-window spike artifacts.
    """
    if len(candles) < period + 1:
        return 20.0  # Default neutral trend strength if warmup short

    tr_list: list[float] = []
    dm_plus_list: list[float] = []
    dm_minus_list: list[float] = []

    for i in range(1, len(candles)):
        h, l, prev_c = candles[i].high, candles[i].low, candles[i - 1].close
        prev_h, prev_l = candles[i - 1].high, candles[i - 1].low

        tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        up_move = h - prev_h
        down_move = prev_l - l

        dm_plus = up_move if up_move > down_move and up_move > 0 else 0.0
        dm_minus = down_move if down_move > up_move and down_move > 0 else 0.0

        tr_list.append(tr)
        dm_plus_list.append(dm_plus)
        dm_minus_list.append(dm_minus)

    if len(tr_list) < period:
        return 20.0

    # Wilder's Smoothing initialization (first period is simple sum)
    smooth_tr = sum(tr_list[:period])
    smooth_dmp = sum(dm_plus_list[:period])
    smooth_dmm = sum(dm_minus_list[:period])

    dx_list: list[float] = []

    def _calc_dx(tr_val: float, dmp_val: float, dmm_val: float) -> float:
        if tr_val <= 0:
            return 0.0
        di_plus = (dmp_val / tr_val) * 100.0
        di_minus = (dmm_val / tr_val) * 100.0
        denom = di_plus + di_minus
        return (abs(di_plus - di_minus) / denom * 100.0) if denom > 0 else 0.0

    dx_list.append(_calc_dx(smooth_tr, smooth_dmp, smooth_dmm))

    # Wilder's recursive smoothing: S_t = S_{t-1} - (S_{t-1} / period) + X_t
    for i in range(period, len(tr_list)):
        smooth_tr = smooth_tr - (smooth_tr / period) + tr_list[i]
        smooth_dmp = smooth_dmp - (smooth_dmp / period) + dm_plus_list[i]
        smooth_dmm = smooth_dmm - (smooth_dmm / period) + dm_minus_list[i]
        dx_list.append(_calc_dx(smooth_tr, smooth_dmp, smooth_dmm))

    if len(dx_list) < period:
        return sum(dx_list) / len(dx_list)

    # First ADX is simple average of first period DX values
    adx = sum(dx_list[:period]) / period
    for i in range(period, len(dx_list)):
        adx = (adx * (period - 1) + dx_list[i]) / period

    return adx


class TrendFollowingPullbackStrategy:
    """Quantitative implementation of H4/H1 Trend-Following Pullback."""

    strategy_id = "trend_pullback"
    version = "2.0"

    def __init__(self, adx_threshold: float = 20.0, target_rr: float = 2.0) -> None:
        self.adx_threshold = adx_threshold
        self.target_rr = target_rr

    def evaluate(
        self,
        symbol: str,
        h4_candles: Sequence[CandleBar],
        h1_candles: Sequence[CandleBar],
    ) -> StrategySignal:
        """Evaluate market regime on H4 and pullback trigger on H1."""
        if len(h4_candles) < 50 or len(h1_candles) < 50:
            return StrategySignal(
                symbol=symbol,
                timeframe="H1",
                strategy_id=self.strategy_id,
                strategy_version=self.version,
                direction="FLAT",
                reason="Insufficient warmup bars (<50 bars on H4 or H1)",
            )

        # ---------------------------------------------------------
        # TIER 1: H4 MARKET REGIME
        # ---------------------------------------------------------
        h4_closes = [c.close for c in h4_candles]
        h4_ema50 = compute_ema(h4_closes, 50)
        h4_ema200 = compute_ema(h4_closes, 200)
        h4_adx = compute_adx(h4_candles, 14)

        current_h4_c = h4_closes[-1]
        is_uptrend = (h4_ema50[-1] > h4_ema200[-1]) and (current_h4_c > h4_ema50[-1]) and (h4_adx >= self.adx_threshold)
        is_downtrend = (h4_ema50[-1] < h4_ema200[-1]) and (current_h4_c < h4_ema50[-1]) and (h4_adx >= self.adx_threshold)

        if not is_uptrend and not is_downtrend:
            return StrategySignal(
                symbol=symbol,
                timeframe="H1",
                strategy_id=self.strategy_id,
                strategy_version=self.version,
                direction="FLAT",
                reason=f"Regime Stand-Down: H4 ADX={h4_adx:.1f} (thresh={self.adx_threshold}) or EMAs tangled",
            )

        # ---------------------------------------------------------
        # TIER 2 & 3: H1 PULLBACK TO VALUE ZONE & TRIGGER CONFIRMATION
        # ---------------------------------------------------------
        h1_closes = [c.close for c in h1_candles]
        h1_ema21 = compute_ema(h1_closes, 21)
        h1_ema50 = compute_ema(h1_closes, 50)
        atr_h1 = compute_atr(h1_candles, 14)

        last_bar = h1_candles[-1]
        candle_range = last_bar.high - last_bar.low
        if candle_range <= 0:
            candle_range = 0.0001

        # UPTREND BUY SETUP
        if is_uptrend:
            # Check if pulled back into Value Zone (between EMA 21 and EMA 50)
            in_value_zone = (last_bar.low <= max(h1_ema21[-1], h1_ema50[-1])) and (last_bar.low >= min(h1_ema21[-1], h1_ema50[-1]) - atr_h1)
            
            # Stringent Rejection Pinbar:
            # 1. Lower wick >= 60% of candle range
            # 2. Lower wick >= 2x body
            # 3. Upper wick <= 25% of candle range
            body = abs(last_bar.close - last_bar.open)
            lower_wick = min(last_bar.open, last_bar.close) - last_bar.low
            upper_wick = last_bar.high - max(last_bar.open, last_bar.close)

            is_pinbar = (
                (lower_wick / candle_range >= 0.60)
                and (lower_wick >= 2.0 * body)
                and (upper_wick / candle_range <= 0.25)
            )

            # Forex-adapted Bullish Engulfing:
            # Current candle is bullish, previous candle was bearish.
            # Current body engulfs previous body AND current close breaks above previous high
            prev_bar = h1_candles[-2]
            is_engulfing = (
                (last_bar.close > last_bar.open)
                and (prev_bar.close < prev_bar.open)
                and (last_bar.close >= prev_bar.high)
                and (last_bar.open <= prev_bar.close)
            )

            if in_value_zone and (is_pinbar or is_engulfing):
                # Structural SL below recent swing low with ATR buffer
                recent_lows = [c.low for c in h1_candles[-5:]]
                swing_low = min(recent_lows)
                stop_loss = swing_low - (1.0 * atr_h1)
                entry_price = last_bar.close
                risk_dist = entry_price - stop_loss
                if risk_dist > 0:
                    take_profit = entry_price + (self.target_rr * risk_dist)
                    return StrategySignal(
                        symbol=symbol,
                        timeframe="H1",
                        strategy_id=self.strategy_id,
                        strategy_version=self.version,
                        direction="BUY",
                        entry_price=round(entry_price, 5),
                        stop_loss=round(stop_loss, 5),
                        take_profit=round(take_profit, 5),
                        reason=f"H4 Uptrend (ADX={h4_adx:.1f}) + H1 Value Pullback + Trigger ({'Pinbar' if is_pinbar else 'Engulfing'})",
                    )

        # DOWNTREND SELL SETUP
        if is_downtrend:
            # Check if pulled back up into Value Zone
            in_value_zone = (last_bar.high >= min(h1_ema21[-1], h1_ema50[-1])) and (last_bar.high <= max(h1_ema21[-1], h1_ema50[-1]) + atr_h1)

            # Stringent Bearish Rejection Pinbar:
            body = abs(last_bar.close - last_bar.open)
            upper_wick = last_bar.high - max(last_bar.open, last_bar.close)
            lower_wick = min(last_bar.open, last_bar.close) - last_bar.low

            is_pinbar = (
                (upper_wick / candle_range >= 0.60)
                and (upper_wick >= 2.0 * body)
                and (lower_wick / candle_range <= 0.25)
            )

            # Forex-adapted Bearish Engulfing:
            prev_bar = h1_candles[-2]
            is_engulfing = (
                (last_bar.close < last_bar.open)
                and (prev_bar.close > prev_bar.open)
                and (last_bar.close <= prev_bar.low)
                and (last_bar.open >= prev_bar.close)
            )

            if in_value_zone and (is_pinbar or is_engulfing):
                recent_highs = [c.high for c in h1_candles[-5:]]
                swing_high = max(recent_highs)
                stop_loss = swing_high + (1.0 * atr_h1)
                entry_price = last_bar.close
                risk_dist = stop_loss - entry_price
                if risk_dist > 0:
                    take_profit = entry_price - (self.target_rr * risk_dist)
                    return StrategySignal(
                        symbol=symbol,
                        timeframe="H1",
                        strategy_id=self.strategy_id,
                        strategy_version=self.version,
                        direction="SELL",
                        entry_price=round(entry_price, 5),
                        stop_loss=round(stop_loss, 5),
                        take_profit=round(take_profit, 5),
                        reason=f"H4 Downtrend (ADX={h4_adx:.1f}) + H1 Value Pullback + Trigger ({'Pinbar' if is_pinbar else 'Engulfing'})",
                    )

        return StrategySignal(
            symbol=symbol,
            timeframe="H1",
            strategy_id=self.strategy_id,
            strategy_version=self.version,
            direction="FLAT",
            reason="No pullback setup or trigger confirmed on H1",
        )

```

### File: `app/strategies/base.py`
- **GitHub Raw:** [app/strategies/base.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/app/strategies/base.py)
```python
"""Strategy interface definitions (Milestone M2 foundation)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

SignalDirection = Literal["BUY", "SELL", "FLAT"]


@dataclass(frozen=True)
class StrategySignal:
    symbol: str
    timeframe: str
    strategy_id: str
    strategy_version: str
    direction: SignalDirection
    entry_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    reason: str = ""


class StrategyProtocol(Protocol):
    """Deterministic strategy interface (single baseline across multiple symbols per Decision 7A)."""

    @property
    def strategy_id(self) -> str: ...

    @property
    def version(self) -> str: ...

```

### File: `app/data/quality_gate.py`
- **GitHub Raw:** [app/data/quality_gate.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/app/data/quality_gate.py)
```python
"""Data Quality Gate: detects stale ticks, missing/gap candles, invalid OHLC, and excessive spreads."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.config import AppConfig
from app.mt5.market_data import CandleBar, TickSnapshot

TIMEFRAME_SECONDS: dict[str, int] = {
    "M1": 60,
    "M5": 300,
    "M15": 900,
    "M30": 1800,
    "H1": 3600,
    "H4": 14400,
    "D1": 86400,
}


class DataQualityError(ValueError):
    """Raised when market data fails freshness, completeness, or integrity checks."""


@dataclass(frozen=True)
class DataQualityReport:
    base_symbol: str
    broker_symbol: str
    timeframe: str
    candle_count: int
    latest_candle_time_utc: datetime
    latest_tick_time_utc: datetime
    current_spread_points: int
    max_allowed_spread_points: int
    passed: bool


def is_market_closed_weekend(symbol: str, dt_utc: datetime) -> bool:
    """Check if traditional Forex/Metals market is currently in its weekend closure."""
    clean_sym = symbol.upper()
    # Crypto (BTC, ETH, etc.) is open 24/7/365
    if any(c in clean_sym for c in ("BTC", "ETH", "SOL", "XRP")):
        return False
    wd = dt_utc.weekday()
    # Friday after 22:00 UTC
    if wd == 4 and dt_utc.hour >= 22:
        return True
    # Saturday all day
    if wd == 5:
        return True
    # Sunday before 22:00 UTC
    if wd == 6 and dt_utc.hour < 22:
        return True
    return False


class DataQualityGate:
    """Enforces strict fail-closed validation on ticks and candle series."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def validate_tick(
        self,
        base_symbol: str,
        tick: TickSnapshot,
        now_utc: datetime | None = None,
    ) -> None:
        """Check tick validity, staleness, and excessive spread."""
        now = now_utc or datetime.now(timezone.utc)
        if tick.bid <= 0 or tick.ask <= 0 or tick.ask < tick.bid:
            raise DataQualityError(
                f"Invalid tick prices for {tick.symbol}: bid={tick.bid}, ask={tick.ask}"
            )

        age_sec = (now - tick.timestamp_utc).total_seconds()
        max_tick_age = self._config.data_quality.max_tick_age_seconds
        market_closed = is_market_closed_weekend(base_symbol, now)
        if self._config.safety.reject_stale_data and age_sec > max_tick_age and not market_closed:
            raise DataQualityError(
                f"Stale tick for {tick.symbol}: age={age_sec:.1f}s exceeds max_tick_age_seconds={max_tick_age}s"
            )

        max_spread = self._config.data_quality.get_max_spread(base_symbol.upper())
        if self._config.safety.reject_excessive_spread and tick.spread_points > max_spread:
            raise DataQualityError(
                f"Excessive spread for {tick.symbol}: spread_points={tick.spread_points} "
                f"exceeds max_spread_points={max_spread}"
            )

    def validate_candles(
        self,
        base_symbol: str,
        timeframe: str,
        candles: list[CandleBar],
        now_utc: datetime | None = None,
    ) -> None:
        """Check candle count, ordering, OHLC integrity, staleness, and unexpected intra-week gaps."""
        now = now_utc or datetime.now(timezone.utc)
        tf_clean = timeframe.strip().upper()
        min_count = self._config.data_quality.min_candle_count

        if not candles or len(candles) < min_count:
            actual = 0 if not candles else len(candles)
            raise DataQualityError(
                f"Insufficient candles for {base_symbol} ({tf_clean}): got {actual}, require >= {min_count}"
            )

        expected_step = TIMEFRAME_SECONDS.get(tf_clean, 900)
        prev_time: datetime | None = None

        for idx, bar in enumerate(candles):
            if bar.open <= 0 or bar.high <= 0 or bar.low <= 0 or bar.close <= 0:
                raise DataQualityError(
                    f"Non-positive OHLC price at index {idx} ({bar.open_time_utc.isoformat()}) for {bar.symbol}"
                )
            if bar.high < bar.low or bar.open > bar.high or bar.open < bar.low or bar.close > bar.high or bar.close < bar.low:
                raise DataQualityError(
                    f"Corrupted OHLC bounds at index {idx} ({bar.open_time_utc.isoformat()}) for {bar.symbol}: "
                    f"O={bar.open} H={bar.high} L={bar.low} C={bar.close}"
                )
            if prev_time is not None:
                delta = (bar.open_time_utc - prev_time).total_seconds()
                if delta <= 0:
                    raise DataQualityError(
                        f"Non-monotonic candle timestamps for {bar.symbol} at {bar.open_time_utc.isoformat()}"
                    )
                # Reject intra-session missing candles (ignore weekend closures >= 48h and scheduled daily exchange rollover breaks)
                is_weekend_break = delta >= 48 * 3600
                is_daily_rollover_break = (
                    prev_time.hour in (20, 21, 22)
                    and bar.open_time_utc.hour in (21, 22, 23)
                    and delta <= 7200
                )
                if delta > expected_step and not is_weekend_break and not is_daily_rollover_break:
                    missing_bars = int(delta // expected_step) - 1
                    raise DataQualityError(
                        f"Missing candles detected for {bar.symbol} ({tf_clean}): gap of {delta:.0f}s "
                        f"(~{missing_bars} missing bars) between {prev_time.isoformat()} and {bar.open_time_utc.isoformat()}"
                    )
            prev_time = bar.open_time_utc

        latest_bar = candles[-1]
        candle_age = (now - latest_bar.open_time_utc).total_seconds()
        max_candle_age = self._config.data_quality.get_max_candle_age(tf_clean)
        market_closed = is_market_closed_weekend(base_symbol, now)
        if self._config.safety.reject_stale_data and candle_age > max_candle_age and not market_closed:
            raise DataQualityError(
                f"Stale candle data for {latest_bar.symbol} ({tf_clean}): "
                f"latest bar {latest_bar.open_time_utc.isoformat()} is {candle_age:.0f}s old "
                f"(max allowed {max_candle_age}s)"
            )

    def evaluate(
        self,
        base_symbol: str,
        timeframe: str,
        tick: TickSnapshot,
        candles: list[CandleBar],
        now_utc: datetime | None = None,
    ) -> DataQualityReport:
        """Run full tick and candle quality checks and return a structured report."""
        self.validate_tick(base_symbol=base_symbol, tick=tick, now_utc=now_utc)
        self.validate_candles(
            base_symbol=base_symbol, timeframe=timeframe, candles=candles, now_utc=now_utc
        )
        return DataQualityReport(
            base_symbol=base_symbol.upper(),
            broker_symbol=tick.symbol,
            timeframe=timeframe.upper(),
            candle_count=len(candles),
            latest_candle_time_utc=candles[-1].open_time_utc,
            latest_tick_time_utc=tick.timestamp_utc,
            current_spread_points=tick.spread_points,
            max_allowed_spread_points=self._config.data_quality.get_max_spread(
                base_symbol.upper()
            ),
            passed=True,
        )

```

### File: `app/evaluation/performance.py`
- **GitHub Raw:** [app/evaluation/performance.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/app/evaluation/performance.py)
```python
"""Deterministic Backtest & Performance Evaluator with Spread, Commission, Swap, Slippage, and IS/OOS Split (Milestone M2)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.mt5.market_data import CandleBar
from app.strategies.baseline import BaselineMultiSymbolStrategy


@dataclass(frozen=True)
class BacktestCostModel:
    point_size: float = 0.01
    contract_size: float = 100.0
    volume_lots: float = 0.01
    spread_points_override: int | None = None
    slippage_points_per_side: int = 2
    commission_per_lot_roundtrip_usd: float = 7.0
    swap_per_lot_per_bar_usd: float = 0.0


@dataclass(frozen=True)
class SimulatedTrade:
    direction: Literal["BUY", "SELL"]
    entry_index: int
    exit_index: int
    entry_price_effective: float
    exit_price_effective: float
    gross_pnl_usd: float
    total_cost_usd: float
    net_pnl_usd: float
    exit_reason: str


@dataclass(frozen=True)
class PerformanceMetrics:
    segment: str  # FULL, IN_SAMPLE, OUT_OF_SAMPLE
    total_trades: int
    win_rate_pct: float
    gross_profit_usd: float
    gross_loss_usd: float
    net_profit_usd: float
    profit_factor: float
    expectancy_per_trade_usd: float
    max_drawdown_pct: float


@dataclass(frozen=True)
class SplitBacktestReport:
    symbol: str
    timeframe: str
    strategy_id: str
    strategy_version: str
    split_ratio: float
    in_sample: PerformanceMetrics
    out_of_sample: PerformanceMetrics


class BacktestEvaluator:
    """Reproducible, non-leaking bar-by-bar backtester with explicit transaction cost deductions."""

    def __init__(
        self,
        strategy: BaselineMultiSymbolStrategy,
        cost_model: BacktestCostModel | None = None,
        initial_equity_usd: float = 10_000.0,
    ) -> None:
        self.strategy = strategy
        self.cost_model = cost_model or BacktestCostModel()
        self.initial_equity_usd = initial_equity_usd

    def run_in_and_out_of_sample(
        self,
        candles: list[CandleBar],
        in_sample_ratio: float = 0.70,
    ) -> SplitBacktestReport:
        if not (0.2 <= in_sample_ratio <= 0.9):
            raise ValueError("in_sample_ratio must be between 0.2 and 0.9.")
        min_needed = (self.strategy.slow_ema_period + 10) * 2
        if len(candles) < min_needed:
            raise ValueError(
                f"Need at least {min_needed} candles for separate In-Sample and Out-of-Sample evaluation."
            )

        split_idx = int(len(candles) * in_sample_ratio)
        is_candles = candles[:split_idx]
        oos_candles = candles[split_idx:]

        is_trades = self.simulate_segment(is_candles)
        oos_trades = self.simulate_segment(oos_candles)

        return SplitBacktestReport(
            symbol=candles[0].symbol,
            timeframe=candles[0].timeframe,
            strategy_id=self.strategy.strategy_id,
            strategy_version=self.strategy.version,
            split_ratio=in_sample_ratio,
            in_sample=self.compute_metrics("IN_SAMPLE", is_trades),
            out_of_sample=self.compute_metrics("OUT_OF_SAMPLE", oos_trades),
        )

    def simulate_segment(self, candles: list[CandleBar]) -> list[SimulatedTrade]:
        trades: list[SimulatedTrade] = []
        warmup = max(self.strategy.slow_ema_period + 2, self.strategy.atr_period + 2)
        active_pos: dict[str, float | int | str] | None = None
        cm = self.cost_model

        for i in range(warmup, len(candles)):
            bar = candles[i]
            spread_pts = (
                cm.spread_points_override
                if cm.spread_points_override is not None
                else max(0, bar.spread)
            )
            half_spread_Plus_slip = (spread_pts * 0.5 + cm.slippage_points_per_side) * cm.point_size

            # 1. Check SL/TP on active position using current bar high/low
            if active_pos is not None:
                direction = str(active_pos["direction"])
                sl = float(active_pos["sl"])
                tp = float(active_pos["tp"])
                entry_idx = int(active_pos["entry_index"])
                entry_px = float(active_pos["entry_price"])
                exit_px: float | None = None
                exit_reason = ""

                if direction == "BUY":
                    if bar.low <= sl:
                        exit_px = sl - cm.slippage_points_per_side * cm.point_size
                        exit_reason = "STOP_LOSS"
                    elif bar.high >= tp:
                        exit_px = tp - cm.slippage_points_per_side * cm.point_size
                        exit_reason = "TAKE_PROFIT"
                else:
                    if bar.high >= sl:
                        exit_px = sl + cm.slippage_points_per_side * cm.point_size
                        exit_reason = "STOP_LOSS"
                    elif bar.low <= tp:
                        exit_px = tp + cm.slippage_points_per_side * cm.point_size
                        exit_reason = "TAKE_PROFIT"

                if exit_px is not None:
                    trades.append(
                        self._close_trade(
                            direction=direction,  # type: ignore[arg-type]
                            entry_index=entry_idx,
                            exit_index=i,
                            entry_price_effective=entry_px,
                            exit_price_effective=exit_px,
                            exit_reason=exit_reason,
                        )
                    )
                    active_pos = None

            # 2. If flat at the start of bar i, evaluate signal on closed bars up to i-1 and execute at bar i open
            elif active_pos is None:
                sig = self.strategy.generate_signal(candles[:i])
                if sig.direction in {"BUY", "SELL"} and sig.stop_loss is not None and sig.take_profit is not None:
                    raw_open = bar.open
                    price_diff = raw_open - ( sig.entry_price or raw_open )
                    if sig.direction == "BUY":
                        eff_entry = raw_open + half_spread_Plus_slip
                    else:
                        eff_entry = raw_open - half_spread_Plus_slip
                    active_pos = {
                        "direction": sig.direction,
                        "entry_index": i,
                        "entry_price": eff_entry,
                        "sl": sig.stop_loss + price_diff,
                        "tp": sig.take_profit + price_diff,
                    }

        return trades

    def _close_trade(
        self,
        direction: Literal["BUY", "SELL"],
        entry_index: int,
        exit_index: int,
        entry_price_effective: float,
        exit_price_effective: float,
        exit_reason: str,
    ) -> SimulatedTrade:
        cm = self.cost_model
        bars_held = max(1, exit_index - entry_index)
        price_move = (
            (exit_price_effective - entry_price_effective)
            if direction == "BUY"
            else (entry_price_effective - exit_price_effective)
        )
        gross_pnl = price_move * cm.contract_size * cm.volume_lots
        commission = cm.commission_per_lot_roundtrip_usd * cm.volume_lots
        swap_cost = cm.swap_per_lot_per_bar_usd * cm.volume_lots * bars_held
        total_cost = round(commission + swap_cost, 4)
        net_pnl = round(gross_pnl - total_cost, 4)

        return SimulatedTrade(
            direction=direction,
            entry_index=entry_index,
            exit_index=exit_index,
            entry_price_effective=round(entry_price_effective, 5),
            exit_price_effective=round(exit_price_effective, 5),
            gross_pnl_usd=round(gross_pnl, 4),
            total_cost_usd=total_cost,
            net_pnl_usd=net_pnl,
            exit_reason=exit_reason,
        )

    def compute_metrics(self, segment: str, trades: list[SimulatedTrade]) -> PerformanceMetrics:
        if not trades:
            return PerformanceMetrics(
                segment=segment,
                total_trades=0,
                win_rate_pct=0.0,
                gross_profit_usd=0.0,
                gross_loss_usd=0.0,
                net_profit_usd=0.0,
                profit_factor=0.0,
                expectancy_per_trade_usd=0.0,
                max_drawdown_pct=0.0,
            )

        wins = [t.net_pnl_usd for t in trades if t.net_pnl_usd > 0]
        losses = [abs(t.net_pnl_usd) for t in trades if t.net_pnl_usd <= 0]
        gross_profit = round(sum(wins), 2)
        gross_loss = round(sum(losses), 2)
        net_profit = round(sum(t.net_pnl_usd for t in trades), 2)
        win_rate = round((len(wins) / len(trades)) * 100.0, 2)
        pf = round(gross_profit / gross_loss, 3) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)
        expectancy = round(net_profit / len(trades), 2)

        equity = self.initial_equity_usd
        peak = equity
        max_dd_pct = 0.0
        for t in trades:
            equity += t.net_pnl_usd
            if equity > peak:
                peak = equity
            dd_pct = ((peak - equity) / peak) * 100.0 if peak > 0 else 0.0
            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct

        return PerformanceMetrics(
            segment=segment,
            total_trades=len(trades),
            win_rate_pct=win_rate,
            gross_profit_usd=gross_profit,
            gross_loss_usd=gross_loss,
            net_profit_usd=net_profit,
            profit_factor=pf,
            expectancy_per_trade_usd=expectancy,
            max_drawdown_pct=round(max_dd_pct, 2),
        )

```

### File: `tests/test_execution.py`
- **GitHub Raw:** [tests/test_execution.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/tests/test_execution.py)
```python
"""Unit tests verifying that order execution is hard-disabled in Milestone M0-M1."""

from __future__ import annotations

import pytest

from app.config import RiskConfig
from app.mt5.execution import DemoExecutionAdapter, ReadOnlyExecutionError
from app.mt5.market_data import SymbolSpec
from app.strategies.base import StrategySignal


class DummyAppConfig:
    def __init__(self, risk_pct: float = 0.25) -> None:
        self.execution_mode = "demo_auto"
        self.risk = RiskConfig(
            risk_per_trade_pct=risk_pct,
            max_total_open_risk_pct=0.50,
            max_daily_loss_pct=1.0,
            max_drawdown_pct=5.0,
            max_positions_per_symbol=1,
        )


def test_execution_adapter_blocks_all_order_operations_in_m0_m1() -> None:
    adapter = DemoExecutionAdapter()
    with pytest.raises(ReadOnlyExecutionError, match="disabled in Milestone M0-M1"):
        adapter.place_order(symbol="EURUSDm", volume=0.01)

    with pytest.raises(ReadOnlyExecutionError, match="disabled in Milestone M0-M1"):
        adapter.modify_order(ticket=12345, sl=1.0700)

    with pytest.raises(ReadOnlyExecutionError, match="disabled in Milestone M0-M1"):
        adapter.close_position(ticket=12345)


def test_calculate_lot_size_gold_xauusd() -> None:
    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25))
    # Balance: $100,000 -> 0.25% risk = $250 cash risk
    signal = StrategySignal(
        symbol="XAUUSD",
        timeframe="M15",
        strategy_id="baseline",
        strategy_version="1.0",
        direction="BUY",
        entry_price=2700.0,
        stop_loss=2690.0,  # $10 stop distance
        take_profit=2720.0,
        reason="Test Gold",
    )
    # Gold contract size: 100 oz. 100 oz * $10 stop dist = $1,000 risk per lot.
    # $250 / $1000 = 0.25 lots!
    spec = SymbolSpec(
        base_symbol="XAUUSD",
        broker_symbol="XAUUSDm",
        description="Gold vs US Dollar",
        currency_base="XAU",
        currency_profit="USD",
        currency_margin="USD",
        digits=2,
        point=0.01,
        tick_size=0.01,
        tick_value=1.0,
        contract_size=100.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=15,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    lots = adapter.calculate_lot_size(signal, spec, account_balance=100000.0)
    assert lots == 0.25


def test_calculate_lot_size_forex_eurusd() -> None:
    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25))
    # Balance: $100,000 -> 0.25% risk = $250 cash risk
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="M15",
        strategy_id="baseline",
        strategy_version="1.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07750,  # 25 pips = 0.00250 dist
        take_profit=1.08500,
        reason="Test EUR",
    )
    # EURUSD contract size: 100,000 EUR. 100,000 * 0.00250 = $250 risk per lot.
    # $250 / $250 = 1.00 lots!
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="Euro vs US Dollar",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    lots = adapter.calculate_lot_size(signal, spec, account_balance=100000.0)
    assert lots == 1.00


def test_calculate_lot_size_fails_closed_when_stop_loss_missing() -> None:
    from app.mt5.execution import ExecutionSafetyError

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25))
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=None,  # Missing!
        take_profit=1.08500,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    with pytest.raises(ExecutionSafetyError, match="explicit entry_price and stop_loss"):
        adapter.calculate_lot_size(signal, spec, account_balance=100000.0)


def test_calculate_lot_size_strictly_rounds_down() -> None:
    # Set risk budget such that raw_lots is 0.259
    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.259))
    signal = StrategySignal(
        symbol="XAUUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=2700.0,
        stop_loss=2690.0,  # $10 stop dist
        take_profit=2720.0,
    )
    spec = SymbolSpec(
        base_symbol="XAUUSD",
        broker_symbol="XAUUSDm",
        description="Gold",
        currency_base="XAU",
        currency_profit="USD",
        currency_margin="USD",
        digits=2,
        point=0.01,
        tick_size=0.01,
        tick_value=1.0,
        contract_size=100.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=15,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    # Balance: 100k -> 0.259% risk = $259. Cash risk per lot = $1,000. Raw lots = 0.259.
    # Round down (floor) must yield 0.25, NOT 0.26!
    lots = adapter.calculate_lot_size(signal, spec, account_balance=100000.0)
    assert lots == 0.25


def test_calculate_lot_size_rejects_order_if_min_vol_exceeds_risk_budget() -> None:
    from app.mt5.execution import ExecutionSafetyError

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25))
    # Balance $1,000 -> 0.25% risk = $2.50 max budget
    # Stop distance = 100 pips on EURUSD -> 0.01 lot risks $10.00
    # $10.00 > $2.50 budget -> MUST REJECT, NOT inflate!
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07000,  # 100 pips dist
        take_profit=1.10000,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    with pytest.raises(ExecutionSafetyError, match="Risk limit rejected"):
        adapter.calculate_lot_size(signal, spec, account_balance=1000.0)


def test_ensure_can_execute_fails_when_trade_not_allowed() -> None:
    from app.mt5.connection import AccountMetadata
    from app.mt5.execution import ExecutionSafetyError

    class MockConn:
        is_connected = True
        backend = object()

        def read_account_metadata(self) -> AccountMetadata:
            return AccountMetadata(
                login=464160066,
                server="Exness-MT5Trial17",
                trade_mode=0,
                trade_mode_label="DEMO",
                currency="USD",
                balance=100000.0,
                equity=100000.0,
                margin=0.0,
                margin_free=100000.0,
                margin_mode=2,
                leverage=500,
                trade_allowed=False,  # Blocked!
                trade_expert=True,
                is_verified_demo=True,
            )

    adapter = DemoExecutionAdapter(config=DummyAppConfig(), connection=MockConn())
    with pytest.raises(ExecutionSafetyError, match="Trade is not allowed"):
        adapter._ensure_can_execute()


def test_ensure_can_execute_fails_when_trade_expert_disabled() -> None:
    from app.mt5.connection import AccountMetadata
    from app.mt5.execution import ExecutionSafetyError

    class MockConn:
        is_connected = True
        backend = object()

        def read_account_metadata(self) -> AccountMetadata:
            return AccountMetadata(
                login=464160066,
                server="Exness-MT5Trial17",
                trade_mode=0,
                trade_mode_label="DEMO",
                currency="USD",
                balance=100000.0,
                equity=100000.0,
                margin=0.0,
                margin_free=100000.0,
                margin_mode=2,
                leverage=500,
                trade_allowed=True,
                trade_expert=False,  # Expert Advisors / Algo trading disabled!
                is_verified_demo=True,
            )

    adapter = DemoExecutionAdapter(config=DummyAppConfig(), connection=MockConn())
    with pytest.raises(ExecutionSafetyError, match="Automated trading"):
        adapter._ensure_can_execute()


def test_calculate_lot_size_ratchets_down_when_order_calc_profit_exceeds_budget() -> None:
    class MockMT5BackendWithProfitCalc:
        def symbol_info(self, symbol: str):
            from types import SimpleNamespace
            return SimpleNamespace(
                volume_min=0.01,
                volume_max=10.0,
                volume_step=0.01,
                trade_tick_size=0.00001,
                trade_tick_value=1.0,
                digits=5,
            )

        def order_calc_profit(self, action: int, symbol: str, volume: float, price_open: float, price_close: float) -> float:
            # Simulate a scenario where broker pricing causes $270 loss for 1.00 lot instead of $250
            return -270.0 * (volume / 1.00)

    class MockConn:
        is_connected = True
        backend = MockMT5BackendWithProfitCalc()

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25), connection=MockConn())
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07750,
        take_profit=1.08500,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    # Risk budget is $250. 1.00 lot would lose $270.
    # The ratchet loop will decrement lots step by step until volume loss <= $250 (i.e. 0.92 lot = -$248.40)
    lots = adapter.calculate_lot_size(signal, spec, account_balance=100000.0)
    assert lots < 1.00
    assert lots == 0.92


def test_calculate_lot_size_fails_closed_when_order_calc_profit_returns_none() -> None:
    from app.mt5.execution import ExecutionSafetyError

    class MockMT5BackendNoneProfit:
        def symbol_info(self, symbol: str):
            from types import SimpleNamespace
            return SimpleNamespace(
                volume_min=0.01,
                volume_max=10.0,
                volume_step=0.01,
                trade_tick_size=0.00001,
                trade_tick_value=1.0,
                digits=5,
            )

        def order_calc_profit(self, action: int, symbol: str, volume: float, price_open: float, price_close: float) -> float | None:
            return None  # Terminal desynced or calculation failed

    class MockConn:
        is_connected = True
        backend = MockMT5BackendNoneProfit()

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25), connection=MockConn())
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07750,
        take_profit=1.08500,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    with pytest.raises(ExecutionSafetyError, match="order_calc_profit returned None"):
        adapter.calculate_lot_size(signal, spec, account_balance=100000.0)


def test_calculate_lot_size_fails_closed_when_broker_risk_exceeds_budget_after_ratchet() -> None:
    from app.mt5.execution import ExecutionSafetyError

    class MockMT5BackendPersistentHighRisk:
        def symbol_info(self, symbol: str):
            from types import SimpleNamespace
            return SimpleNamespace(
                volume_min=0.01,
                volume_max=10.0,
                volume_step=0.01,
                trade_tick_size=0.00001,
                trade_tick_value=1.0,
                digits=5,
            )

        def order_calc_profit(self, action: int, symbol: str, volume: float, price_open: float, price_close: float) -> float:
            # Even at 0.01 lot, simulated loss is $300 > $250 risk budget
            return -300.0

    class MockConn:
        is_connected = True
        backend = MockMT5BackendPersistentHighRisk()

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25), connection=MockConn())
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07750,
        take_profit=1.08500,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    with pytest.raises(ExecutionSafetyError, match="still exceeds risk budget"):
        adapter.calculate_lot_size(signal, spec, account_balance=100000.0)


def test_calculate_lot_size_fails_closed_when_order_calc_profit_returns_non_negative() -> None:
    from app.mt5.execution import ExecutionSafetyError

    class MockMT5BackendPositiveProfitAtSL:
        def symbol_info(self, symbol: str):
            from types import SimpleNamespace
            return SimpleNamespace(
                volume_min=0.01,
                volume_max=10.0,
                volume_step=0.01,
                trade_tick_size=0.00001,
                trade_tick_value=1.0,
                digits=5,
            )

        def order_calc_profit(self, action: int, symbol: str, volume: float, price_open: float, price_close: float) -> float:
            return 25.0  # Anomalous positive profit at Stop Loss!

    class MockConn:
        is_connected = True
        backend = MockMT5BackendPositiveProfitAtSL()

    adapter = DemoExecutionAdapter(config=DummyAppConfig(risk_pct=0.25), connection=MockConn())
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07750,
        take_profit=1.08500,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    with pytest.raises(ExecutionSafetyError, match="non-negative PnL"):
        adapter.calculate_lot_size(signal, spec, account_balance=100000.0)


def test_calculate_lot_size_fails_closed_when_backend_missing_order_calc_profit_in_demo_auto() -> None:
    from app.mt5.execution import ExecutionSafetyError

    class MockMT5BackendWithoutCalc:
        def symbol_info(self, symbol: str):
            from types import SimpleNamespace
            return SimpleNamespace(
                volume_min=0.01,
                volume_max=10.0,
                volume_step=0.01,
                trade_tick_size=0.00001,
                trade_tick_value=1.0,
                digits=5,
            )

    class MockConn:
        is_connected = True
        backend = MockMT5BackendWithoutCalc()

    cfg = DummyAppConfig(risk_pct=0.25)
    cfg.execution_mode = "demo_auto"
    adapter = DemoExecutionAdapter(config=cfg, connection=MockConn())
    signal = StrategySignal(
        symbol="EURUSD",
        timeframe="H1",
        strategy_id="trend_pullback",
        strategy_version="2.0",
        direction="BUY",
        entry_price=1.08000,
        stop_loss=1.07750,
        take_profit=1.08500,
    )
    spec = SymbolSpec(
        base_symbol="EURUSD",
        broker_symbol="EURUSDm",
        description="EURUSD",
        currency_base="EUR",
        currency_profit="USD",
        currency_margin="USD",
        digits=5,
        point=0.00001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        volume_min=0.01,
        volume_max=10.0,
        volume_step=0.01,
        stops_level=0,
        spread_points=10,
        spread_float=True,
        trade_mode=4,
        visible=True,
    )
    with pytest.raises(ExecutionSafetyError, match="missing required order_calc_profit"):
        adapter.calculate_lot_size(signal, spec, account_balance=100000.0)

```

### File: `tests/test_risk.py`
- **GitHub Raw:** [tests/test_risk.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/tests/test_risk.py)
```python
"""Unit tests for KillSwitch and Risk safety locks."""

from __future__ import annotations

import pytest

from app.config import RiskConfig
from app.risk.kill_switch import KillSwitch
from app.risk.manager import RiskManager


def test_kill_switch_cannot_be_disabled() -> None:
    with pytest.raises(ValueError, match="cannot be initialized as disabled"):
        KillSwitch(enabled=False)


def test_kill_switch_trips_and_blocks_operations() -> None:
    ks = KillSwitch(enabled=True)
    assert ks.is_tripped is False
    ks.assert_healthy()

    event = ks.trip(reason="Stale M15 candle on XAUUSDm", source="DataQualityGate")
    assert ks.is_tripped is True
    assert event.source == "DataQualityGate"

    with pytest.raises(RuntimeError, match="KILL SWITCH ACTIVE"):
        ks.assert_healthy()


class DummyConfig:
    def __init__(self, daily_loss_pct: float = 1.0, drawdown_pct: float = 5.0) -> None:
        self.risk = RiskConfig(
            risk_per_trade_pct=0.25,
            max_total_open_risk_pct=0.50,
            max_daily_loss_pct=daily_loss_pct,
            max_drawdown_pct=drawdown_pct,
            max_positions_per_symbol=1,
        )


def test_risk_manager_healthy_under_limits() -> None:
    cfg = DummyConfig(daily_loss_pct=1.0, drawdown_pct=5.0)
    ks = KillSwitch(enabled=True)
    rm = RiskManager(config=cfg, kill_switch=ks)

    state = rm.evaluate_equity(100000.0)
    assert state.daily_pnl_pct == 0.0
    assert state.drawdown_pct == 0.0
    assert not ks.is_tripped

    state = rm.evaluate_equity(99500.0)  # -0.5% daily drop
    assert state.daily_pnl_pct == -0.5
    assert not ks.is_tripped


def test_risk_manager_trips_on_daily_loss_limit() -> None:
    cfg = DummyConfig(daily_loss_pct=1.0, drawdown_pct=5.0)
    ks = KillSwitch(enabled=True)
    rm = RiskManager(config=cfg, kill_switch=ks)

    rm.evaluate_equity(100000.0)  # Day start = 100k
    with pytest.raises(RuntimeError, match="Max daily loss exceeded"):
        rm.evaluate_equity(98900.0)  # -1.1% daily drop -> trips!

    assert ks.is_tripped
    assert "DailyLoss" in ks.last_event.source


def test_risk_manager_trips_on_max_drawdown() -> None:
    cfg = DummyConfig(daily_loss_pct=10.0, drawdown_pct=5.0)
    ks = KillSwitch(enabled=True)
    rm = RiskManager(config=cfg, kill_switch=ks)

    rm.evaluate_equity(100000.0)
    rm.evaluate_equity(110000.0)  # Peak = 110k
    with pytest.raises(RuntimeError, match="Max drawdown limit exceeded"):
        rm.evaluate_equity(104000.0)  # Drop from 110k to 104k = 5.45% drawdown -> trips!

    assert ks.is_tripped
    assert "MaxDrawdown" in ks.last_event.source


def test_kill_switch_persists_across_restart(tmp_path) -> None:
    ks_file = tmp_path / "kill_switch_state.json"
    ks1 = KillSwitch(enabled=True, state_file=ks_file)
    assert not ks1.is_tripped
    ks1.trip(reason="Excessive spread spike", source="DataQualityGate")
    assert ks1.is_tripped

    # Simulate process restart
    ks2 = KillSwitch(enabled=True, state_file=ks_file)
    assert ks2.is_tripped
    with pytest.raises(RuntimeError, match="KILL SWITCH ACTIVE"):
        ks2.assert_healthy()

    # Operator manual reset
    ks2.reset_state(reason="Market stabilized", operator="admin")
    assert not ks2.is_tripped
    ks2.assert_healthy()


def test_risk_manager_persists_across_restart(tmp_path) -> None:
    rm_file = tmp_path / "risk_state.json"
    cfg = DummyConfig(daily_loss_pct=1.0, drawdown_pct=5.0)
    ks = KillSwitch(enabled=True)

    rm1 = RiskManager(config=cfg, kill_switch=ks, state_file=rm_file)
    rm1.evaluate_equity(100000.0)  # Day start = 100k, peak = 100k
    rm1.evaluate_equity(99500.0)

    # Simulate process restart
    rm2 = RiskManager(config=cfg, kill_switch=ks, state_file=rm_file)
    assert rm2._day_start_equity == 100000.0
    assert rm2._peak_equity == 100000.0
    state = rm2.evaluate_equity(99300.0)
    assert state.day_start_equity == 100000.0
    assert state.daily_pnl_pct == -0.7


def test_risk_manager_trips_on_corrupted_state_file(tmp_path) -> None:
    rm_file = tmp_path / "corrupted_risk_state.json"
    rm_file.write_text("{invalid json: malformed...", encoding="utf-8")
    cfg = DummyConfig(daily_loss_pct=1.0, drawdown_pct=5.0)
    ks = KillSwitch(enabled=True)

    rm = RiskManager(config=cfg, kill_switch=ks, state_file=rm_file)
    assert ks.is_tripped is True
    with pytest.raises(Exception, match="KILL SWITCH ACTIVE"):
        ks.assert_healthy()


def test_risk_manager_trips_when_persist_fails(tmp_path) -> None:
    from app.risk.kill_switch import KillSwitchTrippedError

    # Point state file to a path inside a non-existent unwritable directory
    unwritable_file = tmp_path / "non_existent_subdir" / "cannot_create" / "risk_state.json"
    cfg = DummyConfig(daily_loss_pct=1.0, drawdown_pct=5.0)
    ks = KillSwitch(enabled=True)

    rm = RiskManager(config=cfg, kill_switch=ks, state_file=unwritable_file)
    with pytest.raises(KillSwitchTrippedError, match="KILL SWITCH ACTIVE"):
        rm.evaluate_equity(100000.0)
    assert ks.is_tripped is True


def test_kill_switch_raises_when_persist_fails(tmp_path) -> None:
    from app.risk.kill_switch import KillSwitchTrippedError

    unwritable_file = tmp_path / "non_existent_subdir" / "cannot_create" / "kill_switch.json"
    ks = KillSwitch(enabled=True, state_file=unwritable_file)
    with pytest.raises(KillSwitchTrippedError, match="Could not persist KillSwitch state"):
        ks.trip("Testing persist failure", source="test")
    assert ks.is_tripped is True

```

### File: `tests/test_strategy_backtest.py`
- **GitHub Raw:** [tests/test_strategy_backtest.py](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/tests/test_strategy_backtest.py)
```python
"""Unit tests for Milestone M2: BaselineMultiSymbolStrategy and BacktestEvaluator (IS/OOS + Cost Model)."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from app.evaluation.performance import BacktestCostModel, BacktestEvaluator
from app.mt5.market_data import CandleBar
from app.strategies.baseline import BaselineMultiSymbolStrategy
from app.strategies.trend_pullback import TrendFollowingPullbackStrategy


def _synthetic_wave_candles(count: int = 300, symbol: str = "XAUUSDm") -> list[CandleBar]:
    bars: list[CandleBar] = []
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    for i in range(count):
        # Smooth sine wave + slight trend to trigger both bullish and bearish EMA crossovers
        base = 2600.0 + 35.0 * math.sin(i / 9.0) + i * 0.05
        bars.append(
            CandleBar(
                symbol=symbol,
                timeframe="M15",
                open_time_utc=start + timedelta(minutes=15 * i),
                open=round(base - 1.0, 2),
                high=round(base + 6.0, 2),
                low=round(base - 6.0, 2),
                close=round(base + 1.0, 2),
                tick_volume=200,
                spread=20,
                real_volume=0,
            )
        )
    return bars


def test_baseline_strategy_returns_flat_on_insufficient_warmup() -> None:
    strat = BaselineMultiSymbolStrategy()
    candles = _synthetic_wave_candles(count=20)
    sig = strat.generate_signal(candles)
    assert sig.direction == "FLAT"
    assert "Insufficient warmup" in sig.reason


def test_backtest_evaluator_separates_in_sample_and_out_of_sample_with_costs() -> None:
    strat = BaselineMultiSymbolStrategy(fast_ema_period=10, slow_ema_period=25, atr_period=10)
    cost_model = BacktestCostModel(
        point_size=0.01,
        contract_size=100.0,
        volume_lots=0.01,
        slippage_points_per_side=2,
        commission_per_lot_roundtrip_usd=7.0,
        swap_per_lot_per_bar_usd=0.05,
    )
    evaluator = BacktestEvaluator(strategy=strat, cost_model=cost_model, initial_equity_usd=10_000.0)
    candles = _synthetic_wave_candles(count=320)
    report = evaluator.run_in_and_out_of_sample(candles, in_sample_ratio=0.70)

    assert report.symbol == "XAUUSDm"
    assert report.in_sample.segment == "IN_SAMPLE"
    assert report.out_of_sample.segment == "OUT_OF_SAMPLE"
    assert report.in_sample.total_trades > 0
    assert report.out_of_sample.total_trades > 0


def test_trend_pullback_strategy_insufficient_warmup() -> None:
    strat = TrendFollowingPullbackStrategy()
    h4 = _synthetic_wave_candles(count=20, symbol="EURUSDm")
    h1 = _synthetic_wave_candles(count=20, symbol="EURUSDm")
    sig = strat.evaluate("EURUSD", h4, h1)
    assert sig.direction == "FLAT"
    assert "Insufficient warmup" in sig.reason


def test_trend_pullback_strategy_regime_filtering() -> None:
    strat = TrendFollowingPullbackStrategy(adx_threshold=20.0)
    h4 = _synthetic_wave_candles(count=100, symbol="EURUSDm")
    h1 = _synthetic_wave_candles(count=100, symbol="EURUSDm")
    sig = strat.evaluate("EURUSD", h4, h1)
    assert sig.symbol == "EURUSD"
    assert sig.timeframe == "H1"
    assert sig.direction in ("BUY", "SELL", "FLAT")


def test_wilder_adx_filters_choppy_consolidation() -> None:
    from app.strategies.trend_pullback import compute_adx

    # Oscillating chop with no net movement
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    chop_candles: list[CandleBar] = []
    for i in range(80):
        val = 1.0800 + 0.0010 * math.sin(i * 1.5)
        chop_candles.append(
            CandleBar(
                symbol="EURUSDm",
                timeframe="H4",
                open_time_utc=start + timedelta(hours=4 * i),
                open=round(val, 5),
                high=round(val + 0.0008, 5),
                low=round(val - 0.0008, 5),
                close=round(val + 0.0001, 5),
                tick_volume=100,
                spread=15,
                real_volume=0,
            )
        )
    adx_chop = compute_adx(chop_candles, 14)
    assert adx_chop < 18.0, f"Expected chop ADX < 18.0, got {adx_chop}"

    # Clear monotonic trending market
    trend_candles: list[CandleBar] = []
    for i in range(80):
        val = 1.0800 + 0.0005 * i
        trend_candles.append(
            CandleBar(
                symbol="EURUSDm",
                timeframe="H4",
                open_time_utc=start + timedelta(hours=4 * i),
                open=round(val - 0.0002, 5),
                high=round(val + 0.0005, 5),
                low=round(val - 0.0003, 5),
                close=round(val + 0.0003, 5),
                tick_volume=100,
                spread=15,
                real_volume=0,
            )
        )
    adx_trend = compute_adx(trend_candles, 14)
    assert adx_trend > 40.0, f"Expected trend ADX > 40.0, got {adx_trend}"


def test_pinbar_requires_dominant_lower_wick_and_small_opposite_wick() -> None:
    strat = TrendFollowingPullbackStrategy(adx_threshold=15.0)

    # Construct candles where H4 is in strong uptrend and H1 pulls back to EMA 21
    start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    h4 = [
        CandleBar(
            symbol="EURUSDm",
            timeframe="H4",
            open_time_utc=start + timedelta(hours=4 * i),
            open=round(1.0500 + i * 0.0008, 5),
            high=round(1.0510 + i * 0.0008, 5),
            low=round(1.0490 + i * 0.0008, 5),
            close=round(1.0508 + i * 0.0008, 5),
            tick_volume=100,
            spread=15,
            real_volume=0,
        )
        for i in range(80)
    ]

    # Non-pinbar: equal wicks and large body
    h1_bad = [
        CandleBar(
            symbol="EURUSDm",
            timeframe="H1",
            open_time_utc=start + timedelta(hours=i),
            open=round(1.1000 + i * 0.0002, 5),
            high=round(1.1010 + i * 0.0002, 5),
            low=round(1.0990 + i * 0.0002, 5),
            close=round(1.1008 + i * 0.0002, 5),
            tick_volume=100,
            spread=15,
            real_volume=0,
        )
        for i in range(80)
    ]
    sig_bad = strat.evaluate("EURUSD", h4, h1_bad)
    # Shouldn't trigger a buy because no pinbar or engulfing at value zone
    assert sig_bad.direction == "FLAT"

```

### File: `research/STRATEGY_SPEC.md`
- **GitHub Raw:** [research/STRATEGY_SPEC.md](https://raw.githubusercontent.com/MaiLeac/revenue-copilot-international-phase0/main/trading-agent-exness-demo/research/STRATEGY_SPEC.md)
```markdown
# Single Strategy Specification: H4/H1 Trend-Following Pullback Engine
**Document Version:** 2.0 (Institutional Focus Pilot)  
**Target Instrument:** `EURUSD` (Primary Pilot — Most liquid, lowest spread, zero slippage footprint)  
**Execution Environment:** Exness MT5 Demo (`#464160066`, Server: `Exness-MT5Trial17`)  
**Design Philosophy:** "Cá nhỏ bơi theo dấu chân Cá Voi" — Giảm tần số giao dịch, loại bỏ cuộc đua tốc độ, ưu tiên bảo toàn vốn, biến khả năng đứng ngoài thành lợi thế cấu trúc.

---

## 1. Triết Lý & Vị Thế Cạnh Tranh Của "Cá Nhỏ"

### 1.1. Từ Bỏ Cuộc Chơi Của Quỹ Lớn
* **Không Scalping / HFT:** Không cạnh tranh tốc độ mili-giây, không ăn chênh lệch giá vài giây trên khung M1/M5.
* **Không News Sniping:** Không đặt cược giật giá 2 đầu vào đúng giây công bố tin tức đỏ.
* **Không Indicator Bloat:** Loại bỏ hoàn toàn hệ thống 27 chỉ báo phức tạp. Một chỉ báo chỉ được tồn tại nếu có giả thuyết kinh tế/toán học rõ ràng.

### 1.2. Khai Thác 3 Lợi Thế Cấu Trúc Độc Quyền
1. **Thanh khoản tức thời (Liquidity Agility):** Vào/thoát toàn bộ vị thế chỉ trong 0.1 giây mà không làm trượt giá thị trường.
2. **Quyền đứng ngoài (No Mandate Pressure):** Không chịu áp lực giải ngân hàng ngày hay báo cáo tháng; chỉ giao dịch khi xác suất nghiêng hẳn về phía mình.
3. **Bơi theo dòng tiền lớn:** Để các quỹ lớn tranh chấp và thiết lập xu hướng trên H4/D1, ta chỉ đóng vai trò "bắn tỉa du kích" tại các nhịp hồi có giá trị.

---

## 2. Kiến Trúc Chiến Thuật 4 Tầng (The 4-Tier Engine)

```
[TẦNG 1: MARKET REGIME (H4)] ──► Trend Rõ Ràng?
            │
            ├── KHÔNG (Chop / Sideway / Nhiễu) ──► ĐỨNG NGOÀI (Cash is King)
            └── CÓ (Uptrend hoặc Downtrend)
                     │
                     ▼
[TẦNG 2: SETUP SELECTION (H1)] ──► Nhịp Hồi Về Value Zone + Nến Xác Nhận Tiếp Diễn?
            │
            ├── KHÔNG ──► ĐỨNG NGOÀI (Không đuổi giá)
            └── CÓ
                     │
                     ▼
[TẦNG 3: RISK & SIZING GATE] ──► Rủi ro <= 0.25%? SL theo cấu trúc? Spread hợp lệ?
            │
            ├── VI PHẠM ──► HỦY LỆNH (Không nâng rủi ro để cố vào lệnh)
            └── ĐẠT CHUẨN
                     │
                     ▼
[TẦNG 4: TRADE MANAGEMENT] ──► Giữ theo luận điểm, Breakeven tại 1R, Cắt khi vô hiệu
```

---

### Tầng 1: Nhận Diện Trạng Thái Thị Trường (H4 Market Regime)

* **Khung thời gian:** `H4` (4 Giờ).
* **Mục đích:** Xác định xem thị trường có đang trong xu hướng mạnh hay đang đi ngang/nhiễu.
* **Quy tắc định lượng:**
  * **Uptrend (Xu hướng Tăng):**
    1. Cấu trúc đỉnh/đáy: Tạo Higher High (HH) và Higher Low (HL) rõ ràng trên H4.
    2. Đường trung bình động: $\text{EMA}(50) > \text{EMA}(200)$, giá nằm trên cả 2 đường EMA.
    3. Độ mạnh xu hướng: $\text{ADX}(14) \ge 20$ và $\text{DI}^+ > \text{DI}^-$.
  * **Downtrend (Xu hướng Giảm):**
    1. Cấu trúc đỉnh/đáy: Tạo Lower High (LH) và Lower Low (LL) rõ ràng trên H4.
    2. Đường trung bình động: $\text{EMA}(50) < \text{EMA}(200)$, giá nằm dưới cả 2 đường EMA.
    3. Độ mạnh xu hướng: $\text{ADX}(14) \ge 20$ và $\text{DI}^- > \text{DI}^+$.
  * **Regime Nhiễu / Đi Ngang (Sideway / Chop):**
    * Khi $\text{ADX}(14) < 20$ HOẶC $\text{EMA}(50)$ cắt xoắn liên tục qua $\text{EMA}(200)$ trong vòng 20 nến gần nhất.
    * **HÀNH ĐỘNG BẮT BUỘC: ĐỨNG NGOÀI 100%. Không tìm kiếm bất kỳ tín hiệu nào.**

---

### Tầng 2: Chọn Lọc Tín Hiệu (H1 Setup Selection)

* **Khung thời gian:** `H1` (1 Giờ).
* **Mục đích:** Tìm điểm vào lệnh có biên an toàn cao khi giá hồi về vùng giá trị (Value Zone), tuyệt đối không mua đuổi tại đỉnh hay bán đuổi tại đáy.
* **Quy tắc vào lệnh Mua (BUY Setup):**
  1. H4 Regime xác nhận **Uptrend**.
  2. Giá H1 hồi về **Vùng Giá Trị (Value Zone)**:
     - Nằm giữa $\text{EMA}(21)$ và $\text{EMA}(50)$ trên H1, HOẶC chạm vùng hỗ trợ đỉnh cũ đã phá vỡ (Resistance turned Support).
  3. **Tín hiệu kích hoạt (Trigger Bar):**
     - Xuất hiện nến từ chối giảm (Bullish Rejection Pinbar có bóng nến dưới dài tối thiểu $60\%$ thân nến) HOẶC nến nhấn chìm tăng (Bullish Engulfing).
     - Giá đóng cửa của nến Trigger phải nằm trên $\text{EMA}(21)$ H1.
* **Quy tắc vào lệnh Bán (SELL Setup):**
  1. H4 Regime xác nhận **Downtrend**.
  2. Giá H1 hồi lên **Vùng Giá Trị (Value Zone)**:
     - Nằm giữa $\text{EMA}(21)$ và $\text{EMA}(50)$ trên H1, HOẶC chạm vùng kháng cự đáy cũ đã phá vỡ (Support turned Resistance).
  3. **Tín hiệu kích hoạt (Trigger Bar):**
     - Xuất hiện nến từ chối tăng (Bearish Rejection Pinbar có bóng nến trên dài tối thiểu $60\%$ thân nến) HOẶC nến nhấn chìm giảm (Bearish Engulfing).
     - Giá đóng cửa của nến Trigger phải nằm dưới $\text{EMA}(21)$ H1.

---

### Tầng 3: Quản Lý Vốn & Kiểm Soát Rủi Ro (Risk & Sizing Gate)

* **Mức rủi ro tối đa mỗi lệnh:** Cố định **$0.25\%$** vốn chủ sở hữu (`Equity`).
* **Tổng rủi ro danh mục mở:** Tối đa **$0.50\%$** (tối đa 1–2 vị thế cùng lúc).
* **Xác định điểm Cắt Lỗ (Stop-Loss - SL) theo cấu trúc:**
  - Lệnh BUY: Đặt SL dưới đáy nến Trigger hoặc dưới đáy sóng hồi H1 gần nhất $- 1.0 \times \text{ATR}(14, \text{H1})$.
  - Lệnh SELL: Đặt SL trên đỉnh nến Trigger hoặc trên đỉnh sóng hồi H1 gần nhất $+ 1.0 \times \text{ATR}(14, \text{H1})$.
* **Tính toán Lot Size chuẩn xác:**
  $$\text{Cash Risk} = \text{Equity} \times 0.0025$$
  $$\text{Stop Distance} = |\text{Entry Price} - \text{Stop Loss}|$$
  $$\text{Cash Risk Per Lot} = \frac{\text{Stop Distance}}{\text{Trade Tick Size}} \times \text{Trade Tick Value}$$
  $$\text{Lots} = \text{Quantize}\left(\frac{\text{Cash Risk}}{\text{Cash Risk Per Lot}}, \text{Volume Step}\right)$$
* **Luật Bảo Vệ Tuyệt Đối:**
  * Nếu $\text{Lots} < \text{Volume Min}$ (0.01) mà mức rủi ro thực tế vượt quá $0.25\%$ vốn $\rightarrow$ **BỎ LỆNH**. Tuyệt đối không được gượng ép làm tròn lên để vào lệnh.
  * Kiểm tra chênh lệch giá (`Spread`): Nếu $\text{Spread} > 1.5 \times \text{Spread Trung Bình}$ (vượt quá 25 points đối với EURUSD) $\rightarrow$ **BỎ LỆNH**.

---

### Tầng 4: Quản Lý Lệnh & Thoát Vị Thế (Trade Management)

* **Tỷ lệ Lợi Nhuận / Rủi Ro (Target R:R):**
  - Mục tiêu tối thiểu: **$R:R = 1:2.0$** (kỳ vọng lợi nhuận dương $EV$).
  - Take Profit (TP) đặt tại vùng cấu trúc cản đối diện (Recent H4 Swing High/Low) hoặc bằng $\text{Entry} + 2.0 \times |\text{Entry} - \text{SL}|$.
* **Quy tắc Dời Chặn Lỗ (Breakeven & Trailing):**
  - Khi giá di chuyển có lãi đạt **$+1.0 R$**: Dời SL về điểm hòa vốn (`Entry Price + Commission/Spread Buffer`). Bảo toàn $100\%$ rủi ro còn lại của lệnh.
  - Khi giá hình thành các đỉnh/đáy mới trên H1 theo xu hướng: Dời SL theo sau các đáy sóng hồi (HL) mới hình thành.
* **Quy tắc Thoát Lệnh Chủ Động (Thesis Invalidation Exit):**
  - Nếu xuất hiện nến H4 đóng cửa hoàn toàn phá vỡ $\text{EMA}(50)$ H4 theo chiều ngược lại $\rightarrow$ Luận điểm xu hướng đã bị bẻ gãy. Đóng lệnh thị trường ngay lập tức, không đợi giá chạm SL ban đầu.
* **Cấm Tuyệt Đối:**
  - Không bao giờ nới rộng SL khi giá tiến sát SL.
  - Không nhồi thêm vị thế bình quân giá giảm (Martingale / Averaging Down).

---

## 3. Điều Kiện Đứng Ngoài Thị Trường (Stand-Down Rules)

Hệ thống xem việc **"Không vào lệnh"** là một vị thế phòng thủ chủ động:

1. **Khung Giờ Giao Dịch (Session Filter):**
   - Chỉ quét và kích hoạt vào lệnh từ **07:00 UTC đến 16:00 UTC** (giai đoạn trùng lặp sôi động nhất của Phiên London và Phiên New York).
   - Đứng ngoài hoàn toàn trong Phiên Á (thanh khoản mỏng, dễ bị quét râu giả tạo) và phiên giao dịch chuyển giao ngày (Rollover 21:00 - 23:00 UTC).
2. **Bộ Lọc Lịch Kinh Tế Đỏ (High-Impact News Freeze):**
   - Đứng ngoài trước 30 phút và sau 30 phút của các tin tức đặc biệt: Non-Farm Payrolls (NFP), CPI Mỹ, Họp lãi suất FOMC / FED, ECB Rate Decision.
3. **Bộ Ngắt Mạch Tự Động (Risk Kill-Switch Tripping):**
   - Sụt giảm vốn trong ngày (`Daily Loss`) chạm ngưỡng **$1.0\%$** $\rightarrow$ Dừng mở lệnh mới trong 24 giờ.
   - Sụt giảm từ đỉnh (`Peak Drawdown`) chạm ngưỡng **$3.0\%$** $\rightarrow$ Dừng toàn bộ hệ thống, khóa giao dịch và yêu cầu người vận hành rà soát nguyên nhân.

---

## 4. Tiêu Chí Loại Bỏ Chiến Lược (Strategy Decommissioning Criteria)

Một chiến lược sẽ bị **LẬP TỨC KHAI TỬ HOẶC VIẾT LẠI TỪ ĐẦU** nếu vi phạm bất kỳ tiêu chí nào sau đây trong quá trình thử nghiệm:

| Tiêu Chí Đánh Giá | Ngưỡng Cho Phép | Hành Động Khi Vi Phạm |
| :--- | :--- | :--- |
| **Kỳ Vọng Toán Học (EV Out-of-Sample)** | $EV > 0$ sau khi trừ đủ Spread, Commission và Slippage | Loại bỏ ngay lập tức nếu $EV \le 0$ trên tập dữ liệu ngoài mẫu. |
| **Số Lượng Giao Dịch Thử Nghiệm** | Tối thiểu $\ge 50$ giao dịch trong Backtest nghiêm ngặt | Không phê duyệt bất kỳ báo cáo nào có dưới 50 lệnh (tránh bẫy ăn may ngẫu nhiên). |
| **Chuỗi Thua Liên Tiếp Tối Đa** | $\le 7$ lệnh liên tiếp | Nếu chạm 8 lệnh thua liên tiếp $\rightarrow$ Dừng hệ thống để rà soát Market Regime. |
| **Mức Sụt Giảm Tài Khoản (Max DD)** | $\le 5.0\%$ vốn | Khóa bot, hủy chiến lược. |
| **Độ Khớp Giữa Backtest và Forward Test** | Sai lệch Winrate hoặc Slippage $\le 20\%$ | Nếu Demo Forward Test thua lỗ trong khi Backtest lãi $\rightarrow$ Bị Overfitting / rò rỉ dữ liệu, hủy bỏ kết quả. |

---

## 5. Kế Hoạch Triển Khai Thực Tế

1. **Bước 1 (Đã hoàn tất):** Nền móng thực thi an toàn, quản trị vốn `RiskManager`, chống trùng nến, ghi file nguyên tử và xác thực Demo MT5.
2. **Bước 2 (Hiện tại):** Đóng băng việc mở rộng đa mã. Khóa tập trung vào duy nhất cặp `EURUSD` theo bản đặc tả `H4/H1 Trend-Following Pullback Engine`.
3. **Bước 3:** Lập trình module tính toán Market Regime H4 và Trigger H1 trong [`app/strategies/trend_pullback.py`](../app/strategies/trend_pullback.py).
4. **Bước 4:** Thực hiện kiểm thử quá khứ (Backtest) nghiêm ngặt trên ít nhất 1 năm nến MT5 thật, chia tách 70% In-Sample và 30% Out-of-Sample có tính trượt giá.
5. **Bước 5:** Trình nộp diffs và kết quả backtest sang **Gemini Independent Reviewer** để nhận phản biện độc lập trước khi mở cho daemon chạy Demo dài hạn.

```