"""Unit tests auditing the SOL-USDT spot backtest artifact (TRD-02) for reproducibility and OOS honesty."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def test_sol_backtest_offline_reproducibility_and_oos_negative_edge_check() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "experiments" / "sol-backtest" / "sol_backtest_reviewed.py"
    spec = importlib.util.spec_from_file_location("sol_backtest_reviewed", script_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    payload = mod.run_sol_evaluation(offline=True)
    cov = payload["coverage"]
    res = payload["results"]

    assert cov["requested_rows"] == 2096
    assert cov["warmup_rows_before_2021"] == 92
    # Both Buy & Hold and EMA50/200 are negative in Out-of-Sample (2025 onward) -> no deployable edge
    assert res["buy_hold_oos"]["total_return"] < 0
    assert res["ema50_ema200_oos"]["total_return"] < 0
