"""Money HQ — Separate Project Financial Dashboard & Accounting Guardrails.

Tracks strictly verified Money HQ operating performance (L4 realized cash, incremental costs,
runway, and owner hours).
Enforces the hard separation rule: Family investment assets are NEVER co-mingled.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

BUDGET_CAP_VND = 0
SHADOW_WAGE_VND_PER_HR = 50_000


@dataclass(frozen=True)
class MoneyHQMetrics:
    """Core financial metrics snapshot for the Money HQ dashboard."""

    starting_budget_cap_vnd: int
    realized_revenue_l4_vnd: int
    pending_payouts_l3_count: int
    pending_payouts_l3_note: str
    refunds_or_rejected_vnd: int
    variable_costs_vnd: int
    incremental_tool_api_costs_vnd: int
    net_realized_profit_vnd: int
    cash_runway_remaining_vnd: int
    cash_runway_pct: float
    owner_hours_logged: float
    realized_profit_per_owner_hour_vnd: int
    budget_breach_alert: bool
    status_banner: str


def _safe_int(val: str | None) -> int:
    if not val:
        return 0
    cleaned = str(val).replace(",", "").strip()
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def _safe_float(val: str | None) -> float:
    if not val:
        return 0.0
    cleaned = str(val).replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def compute_money_hq_metrics(
    cash_ledger_csv: str | Path,
    cost_ledger_csv: str | Path,
    ai_cost_log_csv: str | Path | None = None,
    budget_cap_vnd: int = BUDGET_CAP_VND,
    baseline_owner_hours: float = 0.0,
) -> MoneyHQMetrics:
    """Compute verified business metrics from CASH_LEDGER.csv and COST_LEDGER.csv."""
    cash_path = Path(cash_ledger_csv)
    cost_path = Path(cost_ledger_csv)

    realized_l4_vnd = 0
    refunds_vnd = 0
    ledger_owner_hours = 0.0

    if cash_path.exists():
        with cash_path.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                status = (row.get("status") or "").strip().upper()
                if status == "L4_COLLECTED_CASH":
                    realized_l4_vnd += _safe_int(row.get("net_usable_cash"))
                refunds_vnd += _safe_int(row.get("refunds"))
                ledger_owner_hours += _safe_float(row.get("owner_hours"))

    variable_costs_vnd = 0
    incremental_api_costs_vnd = 0

    if cost_path.exists():
        with cost_path.open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                amt = _safe_int(row.get("amount"))
                purpose = (row.get("purpose") or "").lower()
                if "api" in purpose or "tool" in purpose or "software" in purpose:
                    incremental_api_costs_vnd += amt
                else:
                    variable_costs_vnd += amt

    if ai_cost_log_csv and Path(ai_cost_log_csv).exists():
        with Path(ai_cost_log_csv).open("r", encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                incremental_api_costs_vnd += _safe_int(row.get("cost_vnd"))

    total_incremental_cost = variable_costs_vnd + incremental_api_costs_vnd
    net_realized_profit = realized_l4_vnd - total_incremental_cost
    runway_remaining = budget_cap_vnd - total_incremental_cost
    runway_pct = round((runway_remaining / budget_cap_vnd) * 100.0, 1) if budget_cap_vnd > 0 else 0.0

    total_owner_hours = round(max(baseline_owner_hours, ledger_owner_hours), 2)
    profit_per_hour = (
        int(round(net_realized_profit / total_owner_hours))
        if total_owner_hours > 0
        else 0
    )

    budget_breach = runway_remaining < 0 or total_incremental_cost > budget_cap_vnd
    if budget_breach:
        banner = "CRITICAL ALERT: EXPERIMENTAL BUDGET CAP EXCEEDED — HALT SPENDING"
    elif realized_l4_vnd == 0:
        banner = "NO L4 CASH RECORDED IN LEDGER"
    else:
        banner = "REVENUE GENERATING (L4 Verified Cash Collected)"

    return MoneyHQMetrics(
        starting_budget_cap_vnd=budget_cap_vnd,
        realized_revenue_l4_vnd=realized_l4_vnd,
        pending_payouts_l3_count=0,
        pending_payouts_l3_note="L3 payouts are not reconciled by these ledgers",
        refunds_or_rejected_vnd=refunds_vnd,
        variable_costs_vnd=variable_costs_vnd,
        incremental_tool_api_costs_vnd=incremental_api_costs_vnd,
        net_realized_profit_vnd=net_realized_profit,
        cash_runway_remaining_vnd=runway_remaining,
        cash_runway_pct=runway_pct,
        owner_hours_logged=total_owner_hours,
        realized_profit_per_owner_hour_vnd=profit_per_hour,
        budget_breach_alert=budget_breach,
        status_banner=banner,
    )


def build_sheet_grid(metrics: MoneyHQMetrics) -> list[list[str]]:
    """Export ledger numbers and current commercial gates without invented live status."""
    return [
        ["MONEY HQ — FINANCIAL SNAPSHOT", "", "", "", "", ""],
        ["State", metrics.status_banner, "Source", "CASH_LEDGER.csv / COST_LEDGER.csv", "Scope", "Recorded rows only"],
        ["", "", "", "", "", ""],
        ["Metric", "Value (VND)", "Evidence", "Calculation", "Unknown", "Next check"],
        ["Currently authorized incremental spend", f"{metrics.starting_budget_cap_vnd:,}", "Configured cap", "Do not infer permission from historical 500,000 VND ceiling", "Future approval", "Before any spend"],
        ["L4 net cash recorded", f"{metrics.realized_revenue_l4_vnd:,}", "Cash ledger", "Only status L4_COLLECTED_CASH", "External accounts not independently checked", "Reconcile receipt"],
        ["Refunds recorded", f"{metrics.refunds_or_rejected_vnd:,}", "Cash ledger", "Sum refund fields", "External refunds unknown", "Reconcile receipt"],
        ["Variable costs recorded", f"{metrics.variable_costs_vnd:,}", "Cost ledger", "Non-tool incremental costs", "Unrecorded costs unknown", "Reconcile receipt"],
        ["Tool/API costs recorded", f"{metrics.incremental_tool_api_costs_vnd:,}", "Cost + AI usage logs", "Recorded incremental charges", "Subscription allocation unknown", "Reconcile bills"],
        ["Recorded cash after incremental costs", f"{metrics.net_realized_profit_vnd:,}", "Derived", "L4 net cash - recorded costs", "Not net profit; owner time/fixed costs excluded", "Log hours"],
        ["Authorized cap less recorded costs", f"{metrics.cash_runway_remaining_vnd:,}", "Derived", "Configured cap - recorded costs", "Not a cash balance", "Require approval before spend"],
        ["Owner hours in ledger", str(metrics.owner_hours_logged), "Cash ledger only", "Logged hours", "Other owner work not captured", "Log actual time"],
        ["", "", "", "", "", ""],
        ["Commercial gate", "Status", "Evidence", "Blocker", "Priority", "Rule"],
        ["Bản Thảo book", "Draft", "products.json", "No finished deliverable", "1", "No sale or physical goods"],
        ["Bản Thảo checkout", "Closed", "checkout.html", "No verified order/payment/delivery path", "2", "Do not claim automated confirmation"],
        ["Buyer response", "Unknown", "No measurement in ledgers", "No verified acquisition test", "3", "Do not claim zero traffic"],
        ["CatalogueQA", "Prototype", "Synthetic sample", "Paid demand unverified", "Backup", "No fake customer claims"],
        ["MT5", "Demo", "run_state.json label", "No real trading evidence", "Separate", "Never count demo P&L as L4"],
        ["", "", "", "", "", ""],
        ["Decision", "Fix the closest buyer-path blocker", "Measure response and cash", "Change direction on failure", "Use resources by task", "Avoid idle report loops"],
    ]


def export_dashboard_artifacts(
    repo_root: str | Path,
) -> tuple[Path, Path, MoneyHQMetrics]:
    """Compute metrics and write MONEY_HQ_DASHBOARD.csv and MONEY_HQ_DASHBOARD.md."""
    root = Path(repo_root)
    metrics = compute_money_hq_metrics(
        cash_ledger_csv=root / "finance" / "CASH_LEDGER.csv",
        cost_ledger_csv=root / "finance" / "COST_LEDGER.csv",
        ai_cost_log_csv=root / "finance" / "AI_USAGE_AND_COST_LOG.csv",
    )
    grid = build_sheet_grid(metrics)

    csv_path = root / "finance" / "MONEY_HQ_DASHBOARD.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerows(grid)

    md_path = root / "finance" / "MONEY_HQ_DASHBOARD.md"
    md_lines = [
        "# Money HQ — financial snapshot from repository ledgers",
        "",
        "This report is generated from recorded ledger rows. It does not inspect bank accounts, live ports, customers, or actual owner time outside the ledger. See [PROJECT_STATE.md](../PROJECT_STATE.md).",
        "",
        f"- L4 net cash recorded: **{metrics.realized_revenue_l4_vnd:,} VND**.",
        f"- Incremental costs recorded: **{metrics.variable_costs_vnd + metrics.incremental_tool_api_costs_vnd:,} VND**.",
        f"- Cash after recorded incremental costs: **{metrics.net_realized_profit_vnd:,} VND**. This is not net profit; owner time and fixed costs are excluded.",
        f"- Currently authorized incremental spend in this calculation: **{metrics.starting_budget_cap_vnd:,} VND**. Historical 500,000 VND ceiling is not automatic spending permission.",
        f"- Owner hours appearing in cash ledger: **{metrics.owner_hours_logged}**; other work may be unlogged.",
        "- Traffic, buyer interest, order confirmation and paid delivery: **unknown** from these ledgers.",
        "- Bản Thảo book: **draft**; checkout **closed**. MT5: **demo only**.",
        "",
        "Next useful action: remove a verified blocker on the product → buyer → payment → delivery path, then record the observed result.",
    ]
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return csv_path, md_path, metrics


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    csv_out, md_out, m = export_dashboard_artifacts(repo_root)
    print(
        f"Exported {csv_out.name} & {md_out.name} | "
        f"L4={m.realized_revenue_l4_vnd:,} VND | "
        f"CashAfterRecordedCosts={m.net_realized_profit_vnd:,} VND"
    )
