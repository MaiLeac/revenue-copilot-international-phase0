"""Unit tests for the Money HQ Separate Financial Dashboard (tools/money_hq_dashboard.py)."""

from __future__ import annotations

from pathlib import Path

from tools.money_hq_dashboard import (
    BUDGET_CAP_VND,
    build_sheet_grid,
    compute_money_hq_metrics,
    export_dashboard_artifacts,
)


def test_compute_money_hq_metrics_defaults_to_zero_l4_and_full_runway(tmp_path: Path) -> None:
    cash_csv = tmp_path / "CASH_LEDGER.csv"
    cost_csv = tmp_path / "COST_LEDGER.csv"
    cash_csv.write_text(
        "date,stream,gross_received,currency,platform_payment_fees,fx_costs,refunds,net_usable_cash,proof_reference_redacted,owner_hours,status,notes\n",
        encoding="utf-8",
    )
    cost_csv.write_text(
        "date,item,amount,currency,recurring,owner_approved,purpose,proof_reference_redacted,notes\n",
        encoding="utf-8",
    )
    metrics = compute_money_hq_metrics(cash_csv, cost_csv)
    assert metrics.starting_budget_cap_vnd == BUDGET_CAP_VND
    assert metrics.realized_revenue_l4_vnd == 0
    assert metrics.pending_payouts_l3_count == 0
    assert metrics.incremental_tool_api_costs_vnd == 0
    assert metrics.net_realized_profit_vnd == 0
    assert metrics.cash_runway_remaining_vnd == 0
    assert metrics.budget_breach_alert is False


def test_compute_money_hq_metrics_detects_l4_revenue_and_incremental_cost(tmp_path: Path) -> None:
    cash_csv = tmp_path / "CASH_LEDGER.csv"
    cost_csv = tmp_path / "COST_LEDGER.csv"
    cash_csv.write_text(
        "date,stream,gross_received,currency,platform_payment_fees,fx_costs,refunds,net_usable_cash,proof_reference_redacted,owner_hours,status,notes\n"
        "2026-11-15,uTest:Cycle562706,650000,VND,20000,10000,0,620000,UTEST_RCPT_1,4.0,L4_COLLECTED_CASH,Settled\n",
        encoding="utf-8",
    )
    cost_csv.write_text(
        "date,item,amount,currency,recurring,owner_approved,purpose,proof_reference_redacted,notes\n"
        "2026-11-10,API token test,50000,VND,no,yes,tool api test,RCPT_COST_1,One-off\n",
        encoding="utf-8",
    )
    metrics = compute_money_hq_metrics(cash_csv, cost_csv, budget_cap_vnd=500_000)
    assert metrics.realized_revenue_l4_vnd == 620_000
    assert metrics.incremental_tool_api_costs_vnd == 50_000
    assert metrics.net_realized_profit_vnd == 570_000
    assert metrics.cash_runway_remaining_vnd == 450_000
    assert metrics.owner_hours_logged == 4.0
    assert metrics.realized_profit_per_owner_hour_vnd == 142_500
    grid = build_sheet_grid(metrics)
    assert len(grid) >= 20


def test_export_dashboard_artifacts_writes_csv_and_md() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    csv_path, md_path, metrics = export_dashboard_artifacts(repo_root)
    assert csv_path.exists()
    assert md_path.exists()
    assert metrics.realized_revenue_l4_vnd == 0
    assert metrics.cash_runway_remaining_vnd == 0
