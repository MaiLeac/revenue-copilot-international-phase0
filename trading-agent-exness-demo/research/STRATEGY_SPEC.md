# Strategy & Multi-Symbol Specification (Locked Pre-M2)

## 1. Multi-Symbol Design Decision (Option A Locked)
Per architectural decision **7A**:
- **Single Baseline Strategy Across Whitelisted Symbols**: One deterministic baseline strategy (`BaselineMultiSymbolStrategy`) will be evaluated uniformly across the allowlist (`XAGUSD`, `EURUSD`, `XAUUSD`) on `M15` and `H1`.
- **Rationale**: Prevents hypothesis explosion and overfitting, simplifies attribution when performance degrades, and tests multi-symbol portfolio/risk plumbing before introducing per-symbol specialization.

## 2. MVP Allowlist & Activation Gate
- **Allowed Symbols (`symbols.allowed`)**: `XAGUSD`, `EURUSD`, `XAUUSD` (auto-discovered against broker suffix conventions such as `XAUUSDm`, `EURUSDm`, `XAGUSDm`).
- **Enabled Symbols (`symbols.enabled`)**: `[]` (Empty in M0-M1; symbols are only enabled one by one after passing Gates G1-G4).

## 3. Initial Risk Envelope (For M2-M3 Testing)
- `risk_per_trade_pct`: `0.25%`
- `max_total_open_risk_pct`: `0.50%` (portfolio-wide across correlated symbols)
- `max_daily_loss_pct`: `1.0%`
- `max_drawdown_pct`: `5.0%`
- `max_positions_per_symbol`: `1`
