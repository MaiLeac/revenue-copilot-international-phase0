# Exness Candidate Trading Strategies Specification (R&D)

**System:** Money HQ Quantitative Strategy Lab  
**Evaluation Criteria:** Out-of-sample Expectancy, Realistic Friction Deductions, Max Drawdown < 3%  
**Mandate:** Zero Martingale, Strict Predefined Stop-Loss, No Curve-Fitting

---

## Candidate 1: EURUSD Volatility-Filtered Donchian Trend Follower

### 1. Market Hypothesis
EURUSD exhibits persistent multi-day trending behaviors during periods of diverging central bank interest rate expectations (ECB vs. Federal Reserve), punctuated by false intraday breakouts during European/Asian session transitions.

### 2. Strategy Rules
- **Timeframe:** H1 Primary, H4 Bias Filter.
- **Indicators:**
  - 20-period Donchian Channel High/Low on H1.
  - 50-period EMA on H4 (Trend direction filter).
  - 14-period ATR (Average True Range).
- **Entry Rules:**
  - *Long:* H4 Close > H4 EMA(50) AND H1 Close breaks above the 20-period Donchian High.
  - *Short:* H4 Close < H4 EMA(50) AND H1 Close breaks below the 20-period Donchian Low.
- **Stop-Loss Logic:** Predefined at $1.5 \times \text{ATR}(14)$ from entry price.
- **Take-Profit / Exit:** Trailing stop behind the opposite 10-period Donchian band (trend exhaustion) or $3.0 \times \text{ATR}(14)$ reward target (1:2 minimum Risk-Reward ratio).
- **Position Sizing:** Exactly $0.25\%$ equity risk per trade based on $1.5 \times \text{ATR}$ stop distance.

### 3. Cost & Friction Assumptions
- Fixed spread deduction: 12 points (1.2 pips).
- Round-turn commission: $7.00 per lot.
- Slippage model: 5 points on entry and stop-loss execution.

### 4. Failure Conditions & Invalidation
- High whipsaw regime: When ATR(14) drops below 20th percentile (low volatility consolidation), all new entries are frozen.
- Multiple consecutive breakout failures (> 3 consecutive losses) automatically trip the cool-off timer for 48 hours.

---

## Candidate 2: XAUUSD (Gold) Asian Liquidity Sweep & Mean Reversion

### 1. Market Hypothesis
Spot Gold (XAUUSD) consistently establishes high and low liquidity pools during the Asian Session (00:00–07:00 UTC). Institutional market participants in the London open (07:00–09:00 UTC) frequently probe and sweep these extremes before rotating back toward the daily volume equilibrium.

### 2. Strategy Rules
- **Timeframe:** M15 Execution, Daily Opening Range Benchmark.
- **Setup:**
  - Identify Asian Session High ($H_{\text{asia}}$) and Asian Session Low ($L_{\text{asia}}$).
- **Entry Rules:**
  - *Short:* London open candle pierces above $H_{\text{asia}}$ by 15–40 cents but closes back below $H_{\text{asia}}$ (bearish rejection pin-bar).
  - *Long:* London open candle pierces below $L_{\text{asia}}$ by 15–40 cents but closes back above $L_{\text{asia}}$ (bullish rejection pin-bar).
- **Stop-Loss Logic:** 10 cents beyond the extreme of the sweep candle (hard stop mandatory upon order placement).
- **Take-Profit:** Asian session mid-point ($[H_{\text{asia}} + L_{\text{asia}}] / 2$).
- **Position Sizing:** Strict $0.25\%$ equity risk.

### 3. Cost & Friction Assumptions
- Spread: 25 points ($0.25).
- Commission: $7.00 per standard lot round-turn.
- Slippage allowance: 10 points ($0.10).

### 4. Failure Conditions & Invalidation
- High-impact macroeconomic news releases (CPI, Non-Farm Payrolls, FOMC meetings) completely invalidate mean-reversion. Trading is hard-locked 60 minutes before and 60 minutes after high-impact events.

---

## Candidate 3: XAGUSD (Silver) Multi-Timeframe Momentum Expansion

### 1. Market Hypothesis
Silver is a high-beta sister asset to Gold with significant industrial demand components. Momentum moves in Silver tend to run further and more aggressively once institutional volume confirms a breakout.

### 2. Strategy Rules
- **Timeframe:** H1 Execution.
- **Indicators:** Bollinger Bands (20, 2.0 std dev) and Volume-Weighted Moving Average (VWMA 20).
- **Entry Rules:**
  - Band squeeze condition: Bandwidth $< \text{historical 10th percentile}$ for at least 12 bars.
  - Breakout confirmation: First candle closing completely outside the upper (long) or lower (short) Bollinger band with volume $> 1.5 \times$ 20-bar average.
- **Stop-Loss Logic:** Placed at the 20-period VWMA.
- **Take-Profit:** Parabolic exit; trail stop along VWMA(20) until closed.

### 3. Comparative Summary Table

| Metric / Parameter | Candidate 1 (EURUSD Trend) | Candidate 2 (XAUUSD Sweep) | Candidate 3 (XAGUSD Momentum) |
| :--- | :--- | :--- | :--- |
| **Market Regime** | Trending | Mean-Reverting | Volatility Expansion |
| **Expected Win Rate** | 38% – 45% | 55% – 62% | 40% – 48% |
| **Payoff Ratio (R:R)** | 1 : 2.5 | 1 : 1.3 | 1 : 2.8 |
| **Trade Frequency** | 8 – 14 trades / month | 12 – 18 trades / month | 4 – 8 trades / month |
| **Friction Sensitivity** | Moderate | High (tight targets) | Low |
| **Max Drawdown Target** | $< 2.5\%$ | $< 2.0\%$ | $< 3.0\%$ |
| **Recommended Order** | Primary Baseline | Secondary Validator | Research / Incubator |
