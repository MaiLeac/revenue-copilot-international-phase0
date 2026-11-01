# Exness MT5 Demo Trading Agent (Milestone M0 & M1 — Read-Only Connector)

Deterministic, safety-first Python trading infrastructure for **Exness MetaTrader 5 (DEMO ONLY)**.

> **Milestone M0–M1 Safety Status:**
> - **Strictly Read-Only**: No order placement, modification, or position closing exists in this milestone (`DemoExecutionAdapter` raises `ReadOnlyExecutionError`).
> - **Hard Demo Lock**: Connections to any MT5 account with `trade_mode != ACCOUNT_TRADE_MODE_DEMO (0)` or server names containing `real`/`live` are immediately terminated (`LiveAccountBlockedError`).
> - **No Autonomous LLM Execution**: LLMs are never granted order execution permissions.

---

## 1. Project Structure

```text
trading-agent-exness-demo/
├── app/
│   ├── main.py                 # CLI entry point & M0-M1 diagnostic runner
│   ├── config.py               # YAML + .env loader with fail-closed validation
│   ├── logging_setup.py        # Structured JSON logger with automatic secret redaction
│   ├── mt5/
│   │   ├── connection.py       # MT5 connection manager & DEMO-only account verifier
│   │   ├── market_data.py      # Broker symbol discovery, contract specs, ticks & candles
│   │   └── execution.py        # Hard-locked read-only stub for M0-M1
│   ├── data/
│   │   └── quality_gate.py     # Checks stale ticks, missing candles, OHLC integrity & spread
│   ├── strategies/
│   │   ├── base.py             # Strategy protocol (M2 foundation)
│   │   └── baseline.py         # Baseline multi-symbol strategy stub (Decision 7A)
│   ├── risk/
│   │   ├── manager.py          # Deterministic risk manager stub (M3)
│   │   └── kill_switch.py      # Circuit breaker state machine
│   ├── portfolio/
│   │   └── exposure.py         # Portfolio exposure stub (M3)
│   ├── journal/
│   │   └── repository.py       # Trade journal stub (M4)
│   └── evaluation/
│       └── performance.py      # Evaluator stub (M4)
├── config/
│   └── demo.yaml               # Whitelist, timeframes, data quality & safety configuration
├── tests/
│   ├── test_config.py
│   ├── test_mt5_connection.py
│   ├── test_data_quality.py
│   ├── test_risk.py
│   └── test_execution.py
├── research/
│   ├── ARCHITECTURE.md
│   ├── STRATEGY_SPEC.md
│   └── M0_M1_VERIFICATION_REPORT.md
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 2. Local Setup Instructions (Windows 64-bit)

### Step 1: Install Python Dependencies
```powershell
cd trading-agent-exness-demo
python -m pip install -r requirements.txt
```

### Step 2: Run Offline Automated Test Suite (No MT5 Terminal Required)
```powershell
python -m pytest tests -v
```

### Step 3: Validate Configuration Only
```powershell
python -m app.main --validate-config-only
```

### Step 4: Connect to Exness MT5 Demo Terminal
1. Install **MetaTrader 5 EXNESS** on Windows and log into an **Exness Demo (`Exness-MT5Trial...`)** account.
2. Copy `.env.example` to `.env` and fill in your Demo login, password, server, and `MT5_TERMINAL_PATH`:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Run the M0-M1 read-only diagnostic connector:
   ```powershell
   python -m app.main --config config/demo.yaml
   ```
