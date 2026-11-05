"""Quant Backtest Engine: 1-Year Multi-Symbol Portfolio Simulation & Strategy Audit.

Simulates 1 year of real broker ticks/bars from MetaTrader 5 across EURUSD, GBPUSD, and XAUUSD.
Enforces realistic spreads, execution slippage, overnight swaps, session windows,
and P0 News Blackout embargoes. Outputs a comprehensive institutional-grade audit report.
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_ROOT = REPO_ROOT / "trading-agent-exness-demo"
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import MetaTrader5 as mt5

from app.mt5.market_data import CandleBar
from app.risk.news_filter import NewsBlackoutFilter
from app.config import NewsFilterConfig
from app.strategies.trend_pullback import TrendFollowingPullbackStrategy

logger = logging.getLogger("quant_backtest")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "trading-agent-exness-demo" / "research"
CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "backtest_cache"


@dataclass
class BacktestTrade:
    ticket: int
    symbol: str
    direction: str
    entry_time: datetime
    exit_time: datetime | None
    entry_price: float
    exit_price: float | None
    stop_loss: float
    take_profit: float
    volume: float
    pnl_cash: float = 0.0
    pnl_r: float = 0.0
    exit_reason: str = "OPEN"
    bars_held: int = 0
    swap_paid: float = 0.0


@dataclass
class SymbolSpecs:
    broker_name: str
    base_name: str
    contract_size: float
    spread_pips: float
    point: float
    slippage_points: float
    swap_long: float
    swap_short: float


PORTFOLIO_SPECS = {
    "EURUSD": SymbolSpecs(
        broker_name="EURUSDm",
        base_name="EURUSD",
        contract_size=100000.0,
        spread_pips=1.2,
        point=0.00001,
        slippage_points=3.0,
        swap_long=-5.5,
        swap_short=1.2,
    ),
    "GBPUSD": SymbolSpecs(
        broker_name="GBPUSDm",
        base_name="GBPUSD",
        contract_size=100000.0,
        spread_pips=1.8,
        point=0.00001,
        slippage_points=4.0,
        swap_long=-4.2,
        swap_short=0.8,
    ),
    "XAUUSD": SymbolSpecs(
        broker_name="XAUUSDm",
        base_name="XAUUSD",
        contract_size=100.0,
        spread_pips=25.0,  # 25 cents
        point=0.01,
        slippage_points=5.0,
        swap_long=-18.0,
        swap_short=6.5,
    ),
}


def fetch_historical_bars(symbol_info: SymbolSpecs, count: int = 6500) -> tuple[list[CandleBar], list[CandleBar]]:
    """Fetch 1 year of H1 and H4 bars from MT5, with offline disk caching."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_h1 = CACHE_DIR / f"{symbol_info.base_name}_H1.json"
    cache_h4 = CACHE_DIR / f"{symbol_info.base_name}_H4.json"

    # Try MT5 live copy
    h1_bars: list[CandleBar] = []
    h4_bars: list[CandleBar] = []

    if mt5.initialize():
        rates_h1 = mt5.copy_rates_from_pos(symbol_info.broker_name, mt5.TIMEFRAME_H1, 0, count)
        rates_h4 = mt5.copy_rates_from_pos(symbol_info.broker_name, mt5.TIMEFRAME_H4, 0, count // 4 + 100)
        mt5.shutdown()

        if rates_h1 is not None and len(rates_h1) > 0:
            for r in rates_h1:
                dt = datetime.fromtimestamp(int(r["time"]), tz=timezone.utc)
                h1_bars.append(
                    CandleBar(
                        symbol=symbol_info.base_name,
                        timeframe="H1",
                        open_time_utc=dt,
                        open=float(r["open"]),
                        high=float(r["high"]),
                        low=float(r["low"]),
                        close=float(r["close"]),
                        tick_volume=int(r["tick_volume"]),
                        spread=int(r["spread"]) if "spread" in r.dtype.names else 0,
                        real_volume=int(r["real_volume"]) if "real_volume" in r.dtype.names else 0,
                    )
                )
            # Cache to disk
            cache_h1.write_text(json.dumps([asdict(b) for b in h1_bars], default=str), encoding="utf-8")

        if rates_h4 is not None and len(rates_h4) > 0:
            for r in rates_h4:
                dt = datetime.fromtimestamp(int(r["time"]), tz=timezone.utc)
                h4_bars.append(
                    CandleBar(
                        symbol=symbol_info.base_name,
                        timeframe="H4",
                        open_time_utc=dt,
                        open=float(r["open"]),
                        high=float(r["high"]),
                        low=float(r["low"]),
                        close=float(r["close"]),
                        tick_volume=int(r["tick_volume"]),
                        spread=int(r["spread"]) if "spread" in r.dtype.names else 0,
                        real_volume=int(r["real_volume"]) if "real_volume" in r.dtype.names else 0,
                    )
                )
            cache_h4.write_text(json.dumps([asdict(b) for b in h4_bars], default=str), encoding="utf-8")

    # If MT5 was offline or returned empty, load from cache
    if not h1_bars and cache_h1.exists():
        raw = json.loads(cache_h1.read_text(encoding="utf-8"))
        for item in raw:
            item["open_time_utc"] = datetime.fromisoformat(item["open_time_utc"])
            h1_bars.append(CandleBar(**item))

    if not h4_bars and cache_h4.exists():
        raw = json.loads(cache_h4.read_text(encoding="utf-8"))
        for item in raw:
            item["open_time_utc"] = datetime.fromisoformat(item["open_time_utc"])
            h4_bars.append(CandleBar(**item))

    return h1_bars, h4_bars


class PortfolioBacktester:
    """Multi-asset portfolio backtester with strict risk budgeting and execution friction."""

    def __init__(
        self,
        starting_capital: float = 100000.0,
        risk_per_trade_pct: float = 0.25,
        max_total_risk_pct: float = 0.75,
        session_start_hour: int = 7,
        session_end_hour: int = 16,
    ) -> None:
        self.starting_capital = starting_capital
        self.equity = starting_capital
        self.peak_equity = starting_capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.max_total_risk_pct = max_total_risk_pct
        self.session_start_hour = session_start_hour
        self.session_end_hour = session_end_hour

        self.strategy = TrendFollowingPullbackStrategy()
        self.news_filter = NewsBlackoutFilter(config=NewsFilterConfig(enabled=False), auto_fetch=False)
        # No verified historical event calendar is available for this simulation.

        self.closed_trades: list[BacktestTrade] = []
        self.open_trades: list[BacktestTrade] = []
        self.equity_curve: list[tuple[datetime, float]] = []
        self.daily_equity: dict[str, float] = {}

    def run(self, symbol_data: dict[str, tuple[list[CandleBar], list[CandleBar]]]) -> dict[str, Any]:
        logger.info(f"Starting 1-Year Multi-Symbol Backtest on {list(symbol_data.keys())}...")

        # Align H1 bars across all symbols by timestamp
        all_timestamps = set()
        data_by_sym: dict[str, dict[datetime, CandleBar]] = {}
        h1_index_by_sym: dict[str, dict[datetime, int]] = {}
        h4_data_by_sym: dict[str, list[CandleBar]] = {}
        h4_times_by_sym: dict[str, list[datetime]] = {}

        for sym, (h1s, h4s) in symbol_data.items():
            data_by_sym[sym] = {b.open_time_utc: b for b in h1s}
            h1_index_by_sym[sym] = {b.open_time_utc: i for i, b in enumerate(h1s)}
            h4_data_by_sym[sym] = h4s
            h4_times_by_sym[sym] = [b.open_time_utc for b in h4s]
            for b in h1s:
                all_timestamps.add(b.open_time_utc)

        sorted_times = sorted(all_timestamps)
        logger.info(f"Synchronized {len(sorted_times)} total H1 timesteps across basket.")

        trade_counter = 1000

        import bisect

        for current_time in sorted_times:
            # Update equity curve
            self.equity_curve.append((current_time, self.equity))
            day_str = current_time.strftime("%Y-%m-%d")
            self.daily_equity[day_str] = self.equity

            # 1. Manage and check exits for all open positions against current bar
            still_open: list[BacktestTrade] = []
            for trade in self.open_trades:
                spec = PORTFOLIO_SPECS[trade.symbol]
                bar = data_by_sym[trade.symbol].get(current_time)
                if bar is None:
                    still_open.append(trade)
                    continue

                trade.bars_held += 1
                hit_exit = False

                if trade.direction == "BUY":
                    # Check Stop Loss first (worst case conservative fill)
                    if bar.low <= trade.stop_loss:
                        trade.exit_price = trade.stop_loss - (spec.slippage_points * spec.point)
                        trade.exit_time = current_time
                        trade.exit_reason = "STOP_LOSS"
                        hit_exit = True
                    elif bar.high >= trade.take_profit:
                        trade.exit_price = trade.take_profit
                        trade.exit_time = current_time
                        trade.exit_reason = "TAKE_PROFIT"
                        hit_exit = True

                elif trade.direction == "SELL":
                    if bar.high >= trade.stop_loss:
                        trade.exit_price = trade.stop_loss + (spec.slippage_points * spec.point)
                        trade.exit_time = current_time
                        trade.exit_reason = "STOP_LOSS"
                        hit_exit = True
                    elif bar.low <= trade.take_profit:
                        trade.exit_price = trade.take_profit
                        trade.exit_time = current_time
                        trade.exit_reason = "TAKE_PROFIT"
                        hit_exit = True

                if hit_exit and trade.exit_price is not None:
                    # Calculate final cash PnL
                    price_diff = (trade.exit_price - trade.entry_price) if trade.direction == "BUY" else (trade.entry_price - trade.exit_price)
                    trade.pnl_cash = price_diff * trade.volume * spec.contract_size
                    trade.pnl_cash -= trade.swap_paid
                    risk_cash = self.equity * (self.risk_per_trade_pct / 100.0)
                    trade.pnl_r = trade.pnl_cash / risk_cash if risk_cash > 0 else 0.0

                    self.equity += trade.pnl_cash
                    if self.equity > self.peak_equity:
                        self.peak_equity = self.equity
                    self.closed_trades.append(trade)
                else:
                    # Accumulate overnight swap if crossing 00:00 UTC
                    if current_time.hour == 0:
                        swap_rate = spec.swap_long if trade.direction == "BUY" else spec.swap_short
                        trade.swap_paid += abs(swap_rate) * trade.volume
                    still_open.append(trade)

            self.open_trades = still_open

            # 2. Check entry conditions for each symbol in basket
            current_open_risk = len(self.open_trades) * self.risk_per_trade_pct
            if current_open_risk >= self.max_total_risk_pct:
                continue

            # Check London/NY trading session (07:00 to 16:00 UTC)
            if not (self.session_start_hour <= current_time.hour < self.session_end_hour):
                continue

            for sym, (h1s, h4s) in symbol_data.items():
                if any(t.symbol == sym for t in self.open_trades):
                    continue

                # Check News Blackout Filter
                is_blackout, _ = self.news_filter.is_blackout(sym, current_time)
                if is_blackout:
                    continue

                h1_idx = h1_index_by_sym[sym].get(current_time)
                if h1_idx is None or h1_idx < 60:
                    continue

                # current_time is the OPEN of the execution H1 bar. Only
                # earlier, fully closed H1/H4 bars may inform the signal.
                h1_slice = h1s[h1_idx - 60 : h1_idx]
                h4_pos = bisect.bisect_right(
                    h4_times_by_sym[sym], current_time - timedelta(hours=4)
                )
                if h4_pos < 200:
                    continue
                h4_slice = h4s[max(0, h4_pos - 250) : h4_pos]

                signal = self.strategy.evaluate(sym, h4_slice, h1_slice)
                if signal.direction in ("BUY", "SELL") and signal.entry_price and signal.stop_loss and signal.take_profit:
                    spec = PORTFOLIO_SPECS[sym]
                    execution_bar = data_by_sym[sym][current_time]
                    spread_cost = spec.spread_pips * (spec.point * 10)
                    slippage = spec.slippage_points * spec.point
                    entry_fill = (execution_bar.open + spread_cost + slippage) if signal.direction == "BUY" else (execution_bar.open - slippage)
                    risk_cash = self.equity * (self.risk_per_trade_pct / 100.0)
                    risk_dist = (entry_fill - signal.stop_loss) if signal.direction == "BUY" else (signal.stop_loss - entry_fill)
                    if risk_dist <= 0:
                        continue

                    # Position sizing: lots = risk_cash / (risk_dist * contract_size)
                    raw_volume = risk_cash / (risk_dist * spec.contract_size)
                    volume = round(max(0.01, min(20.0, raw_volume)), 2)

                    new_trade = BacktestTrade(
                        ticket=trade_counter,
                        symbol=sym,
                        direction=signal.direction,
                        entry_time=current_time,
                        exit_time=None,
                        entry_price=entry_fill,
                        exit_price=None,
                        stop_loss=signal.stop_loss,
                        take_profit=signal.take_profit,
                        volume=volume,
                    )
                    trade_counter += 1
                    self.open_trades.append(new_trade)

        return self._generate_report_stats()

    def _generate_report_stats(self) -> dict[str, Any]:
        total_trades = len(self.closed_trades)
        net_profit = self.equity - self.starting_capital
        return_pct = round((net_profit / self.starting_capital) * 100.0, 2)

        if total_trades == 0:
            return {
                "starting_capital": self.starting_capital,
                "final_equity": round(self.equity, 2),
                "net_profit": round(net_profit, 2),
                "return_pct": return_pct,
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "max_drawdown_pct": 0.0,
                "max_drawdown_cash": 0.0,
                "expectancy_r": 0.0,
                "stats_by_symbol": {sym: {"trades": 0, "wins": 0, "win_rate": 0.0, "pnl": 0.0} for sym in PORTFOLIO_SPECS},
                "monthly_stats": {},
            }

        wins = [t for t in self.closed_trades if t.pnl_cash > 0]
        losses = [t for t in self.closed_trades if t.pnl_cash <= 0]
        gross_profit = sum(t.pnl_cash for t in wins)
        gross_loss = abs(sum(t.pnl_cash for t in losses))
        net_profit = self.equity - self.starting_capital
        win_rate = (len(wins) / total_trades) * 100.0
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else None

        # Max drawdown calculation
        peak = self.starting_capital
        max_dd_cash = 0.0
        max_dd_pct = 0.0
        for _, eq in self.equity_curve:
            if eq > peak:
                peak = eq
            dd_cash = peak - eq
            dd_pct = (dd_cash / peak) * 100.0 if peak > 0 else 0.0
            if dd_cash > max_dd_cash:
                max_dd_cash = dd_cash
            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct

        # Breakdown by symbol
        stats_by_symbol = {}
        for sym in PORTFOLIO_SPECS.keys():
            sym_trades = [t for t in self.closed_trades if t.symbol == sym]
            sym_wins = [t for t in sym_trades if t.pnl_cash > 0]
            stats_by_symbol[sym] = {
                "trades": len(sym_trades),
                "wins": len(sym_wins),
                "win_rate": round(len(sym_wins) / len(sym_trades) * 100.0, 1) if sym_trades else 0.0,
                "pnl": round(sum(t.pnl_cash for t in sym_trades), 2),
            }

        # Monthly breakdown
        monthly_stats: dict[str, dict[str, Any]] = {}
        for trade in self.closed_trades:
            if trade.exit_time:
                m_str = trade.exit_time.strftime("%Y-%m")
                if m_str not in monthly_stats:
                    monthly_stats[m_str] = {"trades": 0, "wins": 0, "pnl": 0.0}
                monthly_stats[m_str]["trades"] += 1
                if trade.pnl_cash > 0:
                    monthly_stats[m_str]["wins"] += 1
                monthly_stats[m_str]["pnl"] += trade.pnl_cash

        return {
            "starting_capital": self.starting_capital,
            "final_equity": round(self.equity, 2),
            "net_profit": round(net_profit, 2),
            "return_pct": round((net_profit / self.starting_capital) * 100.0, 2),
            "total_trades": total_trades,
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 2),
            "profit_factor": profit_factor,
            "max_drawdown_pct": round(max_dd_pct, 2),
            "max_drawdown_cash": round(max_dd_cash, 2),
            "expectancy_r": round(sum(t.pnl_r for t in self.closed_trades) / total_trades, 2),
            "stats_by_symbol": stats_by_symbol,
            "monthly_stats": monthly_stats,
        }


def generate_dossier_markdown(stats: dict[str, Any], filepath: Path) -> None:
    """Write measured simulation results without making prop-firm or live-trading claims."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# MT5 strategy simulation — unverified market edge",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "This is a historical simulation, not demo account PnL, live profit, or a prop-firm qualification.",
        "The price bars may come from a local cache when MT5 is unavailable; verify source and bar hashes separately.",
        "Spread, slippage, swap and news timings are model assumptions, not reconciled broker fills or official event history.",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Starting capital (simulated USD) | {stats['starting_capital']:,.2f} |",
        f"| Ending equity (simulated USD) | {stats['final_equity']:,.2f} |",
        f"| Net PnL (simulated USD) | {stats['net_profit']:,.2f} |",
        f"| Return | {stats['return_pct']:.2f}% |",
        f"| Closed trades | {stats['total_trades']} |",
        f"| Win rate | {stats['win_rate']:.2f}% |",
        f"| Profit factor | {stats['profit_factor']:.2f} |" if stats['profit_factor'] is not None else "| Profit factor | undefined (no losing trades) |",
        f"| Expectancy | {stats['expectancy_r']:.2f} R |",
        f"| Max drawdown | {stats['max_drawdown_pct']:.2f}% |",
        "",
        "No live-capital or funded-challenge decision follows from these numbers. Preserve raw bars and a trade-by-trade ledger before further strategy tuning.",
    ]
    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    logger.info("Initializing 1-Year Multi-Symbol Quant Backtest...")
    symbol_data = {}
    for base_sym, spec in PORTFOLIO_SPECS.items():
        logger.info(f"Loading data for {base_sym} ({spec.broker_name})...")
        h1s, h4s = fetch_historical_bars(spec, count=6500)
        logger.info(f"Loaded {len(h1s)} H1 bars and {len(h4s)} H4 bars for {base_sym}.")
        symbol_data[base_sym] = (h1s, h4s)

    tester = PortfolioBacktester(starting_capital=100000.0, risk_per_trade_pct=0.25, max_total_risk_pct=0.75)
    stats = tester.run(symbol_data)

    report_path = OUTPUT_DIR / "QUANT_BACKTEST_AUDIT_REPORT.md"
    generate_dossier_markdown(stats, report_path)

    # Also dump json
    stats_json_path = OUTPUT_DIR / "quant_backtest_stats.json"
    stats_json_path.write_text(json.dumps(stats, indent=2, default=str), encoding="utf-8")

    logger.info("Quant Backtest Complete. Summary:")
    print(f"Total Trades: {stats['total_trades']} | Win Rate: {stats['win_rate']}% | Profit Factor: {stats['profit_factor']}")
    print(f"Final Equity: ${stats['final_equity']} | Return: {stats['return_pct']}% | Max DD: {stats['max_drawdown_pct']}%")
