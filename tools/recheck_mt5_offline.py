"""Recheck MT5 strategy against tracked bar caches, without opening a terminal or sending orders."""
from __future__ import annotations

import csv
import hashlib
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.quant_backtest_multisymbol import CACHE_DIR, PORTFOLIO_SPECS, CandleBar, PortfolioBacktester

OUT = ROOT / "trading-agent-exness-demo" / "research" / "offline_recheck"


def main() -> None:
    logging.disable(logging.WARNING)
    inputs = {}
    basket = {}
    for symbol in PORTFOLIO_SPECS:
        pair = []
        for timeframe in ("H1", "H4"):
            path = CACHE_DIR / f"{symbol}_{timeframe}.json"
            raw = path.read_bytes()
            rows = json.loads(raw)
            for row in rows:
                row["open_time_utc"] = datetime.fromisoformat(row["open_time_utc"])
            pair.append([CandleBar(**row) for row in rows])
            inputs[f"{symbol}_{timeframe}"] = {"path": str(path.relative_to(ROOT)), "bars": len(rows), "sha256": hashlib.sha256(raw).hexdigest()}
        basket[symbol] = tuple(pair)
    tester = PortfolioBacktester()
    stats = tester.run(basket)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stats.json").write_text(json.dumps({"inputs": inputs, "assumptions": "Historical simulation using cached broker bars; fixed spread/slippage/swap; no verified historical news calendar; no real fills.", "stats": stats}, ensure_ascii=False, indent=2), encoding="utf-8")
    trades = [asdict(trade) for trade in tester.closed_trades]
    with (OUT / "trades.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(trades[0]) if trades else list(asdict(tester.open_trades[0])) if tester.open_trades else [])
        if writer.fieldnames:
            writer.writeheader()
            writer.writerows(trades)
    print(json.dumps({"net_profit": stats["net_profit"], "return_pct": stats["return_pct"], "trades": stats["total_trades"], "profit_factor": stats["profit_factor"], "output": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
