from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("MetaTrader5")
from tools.quant_backtest_multisymbol import CandleBar, PortfolioBacktester
from app.strategies.base import StrategySignal


def bar(symbol, when, timeframe):
    return CandleBar(symbol, timeframe, when, 1.0, 1.1, 0.9, 1.0, 1, 1, 0)


def test_strategy_only_sees_closed_bars():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    h1 = [bar("EURUSD", start + timedelta(hours=i), "H1") for i in range(900)]
    h4 = [bar("EURUSD", start + timedelta(hours=4*i), "H4") for i in range(225)]
    seen = []

    class Probe:
        def evaluate(self, symbol, h4_candles, h1_candles):
            seen.append((tester.equity_curve[-1][0], h4_candles[-1].open_time_utc, h1_candles[-1].open_time_utc))
            return StrategySignal(symbol=symbol, timeframe="H1", strategy_id="probe", strategy_version="1", direction="FLAT", reason="test")

    tester = PortfolioBacktester()
    tester.strategy = Probe()
    tester.run({"EURUSD": (h1, h4)})
    assert seen
    for current_time, h4_open, h1_open in seen:
        # At every eligible H1 open, neither the H1 nor H4 forming bar is passed.
        assert h1_open + timedelta(hours=1) <= current_time
        assert h4_open + timedelta(hours=4) <= current_time
