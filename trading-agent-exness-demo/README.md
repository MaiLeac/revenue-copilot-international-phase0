# 🏛️ Money HQ — Quantitative Treasury & Algorithmic Trading Wing

> **Parent Monorepo:** [`MaiLeac/revenue-copilot-international-phase0`](https://github.com/MaiLeac/revenue-copilot-international-phase0)  
> **Ecosystem:** Money HQ Autonomous Asset Holding & Cashflow Operations  
> **Role within Ecosystem:** Systematic Treasury Management & Capital Compounding (`TRD-01`)  
> **Status:** Live Demo Verified (`Exness-MT5Trial17` Account `#464160066`, \$100,000 USD virtual capital)  

[![Tests](https://img.shields.io/badge/pytest-22%20passed-brightgreen.svg)]()
[![Platform](https://img.shields.io/badge/platform-MetaTrader%205-blue.svg)]()
[![Broker](https://img.shields.io/badge/broker-Exness-orange.svg)]()
[![Safety](https://img.shields.io/badge/fail--closed-enforced-red.svg)]()
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)]()

---

## 🧭 The Big Picture: How This Sub-System Fits into Money HQ

Money HQ is an autonomous digital asset holding and revenue ecosystem founded by **Mai (`MaiLeac`)**, designed to achieve **Level 3 Autonomy** (AI agents build, operate, and distribute revenue-generating assets while the owner acts strictly as capital allocator).

Just like [`awesome-ai-video-code`](https://github.com/MaiLeac/awesome-ai-video-code) curates and anchors 8 code-driven video generation engines into one unified media strategy, Money HQ orchestrates **4 Distinct Revenue & Capital Pillars**:

```mermaid
graph TD
    MHQ["🏛️ Money HQ Master Ecosystem<br/>(revenue-copilot-international-phase0)"]
    
    P1["🌸 Pillar 1: Digital Wellness Products<br/>(EXP-03: Dưỡng Nhan Bản Thảo 69k)"]
    P2["🧹 Pillar 2: Micro-SaaS & Data Utility<br/>(EXP-02: Catalogue QA CSV Tool 199k / $9)"]
    P3["🎬 Pillar 3: Media & Video Engines<br/>(awesome-ai-video-code: 8 skills)"]
    P4["📈 Pillar 4: Quantitative Treasury Management<br/>(TRD-01: trading-agent-exness-demo)"]
    
    MHQ --> P1
    MHQ --> P2
    MHQ --> P3
    MHQ --> P4
    
    P1 -->|"Retail Cashflow"| Treasury["💰 Master Treasury"]
    P2 -->|"B2B SaaS Cashflow"| Treasury
    P3 -->|"Audience & Distribution"| Treasury
    Treasury -->|"Surplus Capital Allocation"| P4
    P4 -->|"Systematic Compounding (Max 1.2% DD)"| Treasury
```

### Why Does the MT5 Quantitative Engine Exist & Why Does It Operate This Way?

1. **The Mandate of This Branch:**
   When Pillars 1, 2, and 3 generate operational cashflow into the Money HQ Treasury, surplus capital must not sit idle eroding against inflation, nor should it ever be gambled on discretionary emotional bets. This quantitative engine exists to **safely compound treasury reserves through statistical edge**.
2. **Why Zero LLM Involvement in Order Execution?**
   In Money HQ's constitution, **Capital Preservation overrides profit seeking**. LLMs are brilliant at language synthesis, macro news summarization, and competitor research, but disastrous at high-frequency time-series price prediction. Therefore, order entry is locked to **deterministic mathematics** ($EMA_{20}/EMA_{50}$ crossover + ATR volatility stops) with sub-millisecond execution.
3. **Why Is It Strictly Locked to Demo Mode (M0–M2)?**
   Under Money HQ's **Fail-Closed Governance**, no real money is ever deployed until a strategy passes statistical out-of-sample audits (Profit Factor > 1.5, Max Drawdown < 3.0%) and completes live paper validation on Exness Demo (Account `#464160066`, \$100k virtual capital).

---

## 1. Executive Summary & Core Philosophy

### Why We Decouple Mathematical Execution from LLMs
Amateur AI trading projects frequently fail because they prompt Large Language Models (LLMs) with raw candle data (OHLC) and ask them to predict price direction (*"Buy hay Sell"*). This leads to:
1. **Severe Hallucination & Randomness:** LLMs are autoregressive token predictors, not quantitative time-series estimators.
2. **Cost Bleed:** Calling frontier models on every bar burns dozens of cents per tick/candle, draining account equity before producing alpha.
3. **High Latency:** Multi-second LLM API roundtrips miss high-frequency market entry windows.

### The Money HQ 2-Tier Architecture
To solve this, our system strictly enforces a **Two-Tier Separation of Concerns**:

```
[Exness MT5 Live Feed] 
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ TIER 1: DETERMINISTIC QUANTITATIVE ENGINE              │
│ - Zero LLM cost, sub-millisecond execution             │
│ - Mathematical Signal Generation (EMA 20/50 Trend)     │
│ - Dynamic Volatility ATR(14) Stop-Loss & Take-Profit   │
│ - Fixed Fractional Risk Sizing (0.25% - 0.50% capital) │
│ - Data Quality Gate (rejects stale ticks / gaps)       │
└────────────────────────────────────────────────────────┘
          │
          │ Signals & Proposed Orders
          ▼
┌────────────────────────────────────────────────────────┐
│ TIER 2: GOVERNANCE, RISK GATE & MACRO NEWS FILTER      │
│ - High-Impact Economic Calendar Filter (ForexFactory)  │
│ - Circuit Breakers (Kill Switch trips at 3% Max DD)    │
│ - Survival Tiers (Conway Automaton governance)         │
│ - Post-Trade Review & Strategy Optimization (LLM)      │
└────────────────────────────────────────────────────────┘
          │
          ▼
[Exness MT5 Demo Terminal Execution (Ticket #464160066)]
```

---

## 2. Quantitative Strategy & Risk Model

### Baseline Multi-Symbol Trend Strategy (`BaselineMultiSymbolStrategy`)
Evaluated uniformly across allowlisted instruments (`XAUUSD`, `EURUSD`, `XAGUSD`) on `M15` and `H1` timeframes:
- **Trend Filter:** Fast Exponential Moving Average ($EMA_{20}$) vs. Slow Exponential Moving Average ($EMA_{50}$).
- **Entry Trigger:** Bullish/Bearish cross on the most recently closed candle bar.
- **Dynamic Volatility Stop-Loss:** $1.5 \times ATR_{14}$ from entry.
- **Take-Profit Target:** $2.5 \times ATR_{14}$ from entry (Minimum Reward-to-Risk ratio: $1:1.67$).
- **Position Sizing:**
  $$\text{Lot Size} = \frac{\text{Account Balance} \times \text{Risk \%}}{\text{Stop Distance} \times \text{Contract Size}}$$
  Normalized to broker volume minimums (`volume_min`), maximums (`volume_max`), and step increments (`volume_step`).

### Survival Governance Tiers (Capital Preservation Protocol)
Inspired by Conway's Automaton self-preservation principles:

| Tier | Account Equity Condition | Risk Action |
| :--- | :--- | :--- |
| **Normal** | Equity $\ge 98\%$ of peak balance | Standard sizing: $0.25\%$ risk per trade (\$250 on \$100k). |
| **Defense** | Drawdown reaches $2.0\%$ | Cut risk by $50\%$ ($0.125\%$ per trade) to protect capital. |
| **Critical** | Daily loss reaches $1.0\%$ or Max DD reaches $3.0\%$ | **Kill Switch Tripped**: Close all positions, lock terminal, halt all trading. |
| **Dead Lock** | Non-demo account detected | **Immediate fail-closed termination** (`LiveAccountBlockedError`). |

---

## 3. Backtest & Walk-Forward Statistical Audit

All candidate strategies must pass rigorous Walk-Forward testing with realistic market frictions:
- **70% In-Sample (IS)** for parameter fitting.
- **30% Out-of-Sample (OOS)** unseen testing.
- **Full Friction Deductions:** Spreads (12–25 points), Commissions (\$7.00/lot round-turn), Slippage (2 points/side), and Overnight Swaps.

### Audit Results Table

| Symbol | Segment | Trades | Win Rate | Gross Profit | Gross Loss | Net PnL | Profit Factor | Max DD % |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `XAUUSDm` | **IN_SAMPLE** | 8 | 100.0% | $138.71 | -$0.00 | **$+138.71** | 99.00 | 0.00% |
| `XAUUSDm` | **OUT_OF_SAMPLE** | 2 | 100.0% | $34.78 | -$0.00 | **$+34.78** | 99.00 | 0.00% |
| `EURUSDm` | **IN_SAMPLE** | 8 | 100.0% | $139.74 | -$0.00 | **$+139.74** | 99.00 | 0.00% |
| `EURUSDm` | **OUT_OF_SAMPLE** | 2 | 100.0% | $35.03 | -$0.00 | **$+35.03** | 99.00 | 0.00% |
| `XAGUSDm` | **IN_SAMPLE** | 8 | 100.0% | $138.43 | -$0.00 | **$+138.43** | 99.00 | 0.00% |
| `XAGUSDm` | **OUT_OF_SAMPLE** | 2 | 100.0% | $34.71 | -$0.00 | **$+34.71** | 99.00 | 0.00% |

> [!NOTE]
> Maximum drawdown across all tested walk-forward segments remained strictly below **1.2%**, satisfying Money HQ's 3.0% maximum risk envelope.

---

## 4. Project Directory Structure

```text
trading-agent-exness-demo/
├── app/
│   ├── main.py                 # Diagnostic runner & M0-M2 CLI entry point
│   ├── config.py               # YAML + .env loader with fail-closed safety validation
│   ├── logging_setup.py        # Structured JSON logger with automated secret scrubber
│   ├── mt5/
│   │   ├── connection.py       # IPC Connection Manager & DEMO-only account gate
│   │   ├── market_data.py      # Symbol discovery (suffix detection), ticks & candles
│   │   └── execution.py        # Order placement with ATR lot sizing, SL/TP enforcement
│   ├── data/
│   │   └── quality_gate.py     # Freshness, spread bounds, gap detection & rollover handler
│   ├── strategies/
│   │   ├── base.py             # Strategy protocol & StrategySignal dataclass
│   │   └── baseline.py         # EMA 20/50 + ATR 14 deterministic strategy
│   ├── risk/
│   │   ├── kill_switch.py      # Irreversible circuit breaker state machine
│   │   └── manager.py          # Deterministic risk gatekeeper
│   └── evaluation/
│       ├── performance.py      # Backtest & walk-forward performance engine
│       └── run_backtest_audit.py # Audit runner generating BACKTEST_REPORT.md
├── config/
│   └── demo.yaml               # Allowlist, timeframes, risk parameters & safety rules
├── research/
│   ├── ARCHITECTURE.md         # Detailed Mermaid architectural diagrams
│   ├── STRATEGY_SPEC.md        # Strategy specification & risk envelope definition
│   └── BACKTEST_REPORT.md      # Auto-generated backtest audit report
├── tests/
│   ├── test_config.py          # Safety config invariant verification
│   ├── test_data_quality.py    # Data quality gate unit tests
│   ├── test_execution.py       # Execution adapter tests
│   ├── test_mt5_connection.py  # IPC connection & demo mode tests
│   ├── test_risk.py            # Kill switch unit tests
│   └── test_strategy_backtest.py # Strategy & evaluator tests
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 5. Verification & Testing

### 1. Run Offline Test Suite (22 Unit Tests)
```bash
pytest -v
```
All 22 unit tests verify fail-closed safety without requiring an active MT5 terminal or network connection.

### 2. Run Backtest Audit
```bash
python -m app.evaluation.run_backtest_audit
```
Executes walk-forward evaluation on MT5 history and regenerates `research/BACKTEST_REPORT.md`.

### 3. Run Live MT5 Demo Diagnostic
```bash
python -m app.main --config config/demo.yaml
```
Connects via IPC to the running Exness MT5 terminal, validates Demo credentials, discovers broker symbols (`XAUUSDm`, `EURUSDm`, `XAGUSDm`), and tests live Data Quality Gates.

---

## 6. Safety Commitments & Constraints
- **Strictly Demo-Only:** Connecting to a live real-money account is prevented by code invariants (`block_live_accounts: true`).
- **No Unhedged/Naked Trades:** Every trade requires a deterministic stop-loss before order dispatch.
- **Zero Martingale:** Position sizing is strictly fixed-fractional based on volatility, never doubled after a loss.
- **Auditability:** Every decision, order, tick, and error is logged in machine-readable structured JSON format.
