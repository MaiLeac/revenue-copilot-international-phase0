---
name: trading-operator
description: "Inspect and control the autonomous MT5 trading bot (TRD-01 Exness Demo). DO NOT install MetaTrader5 or run daemon.py inside Docker; communicate exclusively via tools/trading_ctl.py or run_state.json."
---

# Autonomous MT5 Trading Operator Skill (TRD-01 Exness Demo)

Use this skill whenever the owner asks about trading, bot status, starting/stopping trading, or checking profit/loss (e.g., "Bắt đầu trade đi", "Trạng thái bot", "Lời lỗ bao nhiêu", "Dừng trade", "Bật bot").

## Critical Architecture Rule
1. **Never attempt to install `MetaTrader5` via pip inside Docker/Linux.** The official MetaTrader 5 Python library is a Windows-only C-API extension that requires the native Windows MT5 Terminal (`terminal64.exe`). It cannot run in Linux/Docker.
2. **The MT5 daemon already runs on the Windows host.** It runs autonomously in the background, connects to Exness Demo (`#464160066`), and monitors `EURUSD` using the Trend-Following Pullback strategy (H4/H1).
3. **Control and monitor via `tools/trading_ctl.py` (0 token cost, 0 dependencies):**
   - Always execute `python tools/trading_ctl.py <command>` to inspect or control the bot.
   - It reads and updates `trading-agent-exness-demo/run_state.json` safely.

## Standard Execution Commands (inside `/a0/usr/projects/money-hq` or repo root)

### 1. When owner asks "Bắt đầu trade đi", "Bật bot", "Start trading":
```bash
python tools/trading_ctl.py start
```
*Action:* Output the exact result returned by `trading_ctl.py` to the owner in Telegram. Confirm that the command is active in `run_state.json` and the Windows daemon is actively scanning the market.

### 2. When owner asks "Trạng thái bot", "Tình hình sao rồi", "Status", "Có lệnh nào không":
```bash
python tools/trading_ctl.py status
```
*Action:* Return the formatted status (Daemon status, heartbeat freshness, Account #464160066, Balance, Equity, Daily PnL %, Drawdown %, Open positions, Active Strategy).

### 3. When owner asks "Tạm dừng trade", "Pause":
```bash
python tools/trading_ctl.py pause
```

### 4. When owner asks "Dừng hẳn bot", "Stop trading", "Tắt bot":
```bash
python tools/trading_ctl.py stop
```

### 5. When owner asks for recent trading history or logs:
```bash
python tools/trading_ctl.py journal
```

## Security & Risk Guardrails
- **DEMO ONLY:** The bot operates strictly on Exness Demo (`#464160066`, server `Exness-MT5Trial17`). Real money accounts are blocked by policy.
- **Fixed Risk:** Every trade risks exactly 0.25% of balance with mandatory hard Stop Loss.
- **Never report Demo trading profit as business cashflow (L4).**
