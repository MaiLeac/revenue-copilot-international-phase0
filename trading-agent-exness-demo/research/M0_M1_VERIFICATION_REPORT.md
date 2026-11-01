# Milestone M0 & M1 Verification Report

**Date:** 2026-11-01  
**Project:** `trading-agent-exness-demo`  
**Scope:** M0 (Project Foundation) + M1 (MT5 Read-Only Connector & Data Quality Gate)

---

## 1. Local Environment Inspection Results

| Check | Status / Value | Notes |
|---|---|---|
| **OS** | Windows 11 64-bit (`AMD64`) | Required native environment for MetaTrader5 IPC bridge |
| **Python Version** | `Python 3.12.10` (MSC v.1943 64-bit) | Verified 64-bit interpreter |
| **MetaTrader5 Package** | `MetaTrader5 5.0.6231` (MetaQuotes Ltd.) | Installed and verified importable |
| **PyYAML / Pydantic / Pytest** | Installed (`pytest 9.2.0`) | All config & unit test dependencies present |
| **Local MT5 Terminal Binary** | **Not yet installed on disk** (`terminal64.exe` not found in `C:\Program Files`) | Requires user to install Exness MT5 Terminal and log into an `Exness-MT5Trial` demo account |

---

## 2. What Was Implemented & Verified (Automated Tests: 20/20 Passed)

1. **Configuration & Fail-Closed Validation (`tests/test_config.py`)**:
   - Verified loading of `config/demo.yaml`.
   - Verified rejection when `DEMO_ONLY != true` in environment.
   - Verified rejection when `account_mode != demo_only` or `safety.block_live_accounts != true`.
   - Verified rejection if `symbols.enabled` is non-empty during M0-M1 or contains symbols outside `symbols.allowed`.
2. **MT5 Connection & Demo Account Gate (`tests/test_mt5_connection.py`)**:
   - Verified clear error (`MT5ConnectionError`) when MT5 terminal is unavailable.
   - Verified hard rejection (`LiveAccountBlockedError`) + automatic `shutdown()` when `account_info().trade_mode != ACCOUNT_TRADE_MODE_DEMO (0)`.
   - Verified secondary defense: hard rejection if server name contains `real` or `live` even if `trade_mode == 0`.
   - Verified broker symbol discovery (`XAUUSD` -> `XAUUSDm`, `EURUSD` -> `EURUSDm`, `XAGUSD` -> `XAGUSDm`) and contract specification validation.
3. **Data Quality Gate (`tests/test_data_quality.py`)**:
   - Verified detection and rejection of stale ticks (`age > max_tick_age_seconds`).
   - Verified detection and rejection of excessive spread (`spread_points > max_spread_points`).
   - Verified detection and rejection of missing intra-session candles (timestamp gap > timeframe step) and stale candle series.
4. **Read-Only Execution Lock & Kill Switch (`tests/test_execution.py`, `tests/test_risk.py`)**:
   - Verified `DemoExecutionAdapter` raises `ReadOnlyExecutionError` on `place_order`, `modify_order`, and `close_position`.
   - Verified `KillSwitch` cannot be disabled and halts operations once tripped.

---

## 3. What Remains Unverified (Requires Live Exness Demo Terminal)

- Live IPC handshake with a running Exness MT5 `terminal64.exe` instance on this machine.
- Confirming exact suffix naming (`m`, `z`, or raw) on the user's specific `Exness-MT5Trial` server.
- Confirming real-time session hours and live tick stream latency during market open.
