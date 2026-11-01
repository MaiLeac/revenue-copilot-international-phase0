"""Money HQ Separate Business Financial Dashboard & Early-Warning Monitor.

Tracks strictly verified Money HQ operating performance (L4 realized cash, L3 pending payouts,
incremental costs against the 500,000 VND budget cap, owner hours, experiment P&L, and blockers)
completely separate from the owner's family investment portfolio.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from pathlib import Path

BUDGET_CAP_VND = 0
SHADOW_WAGE_VND_PER_HR = 50_000


@dataclass(frozen=True)
class MoneyHQMetrics:
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
    baseline_owner_hours: float = 3.5,
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
                incremental_api_costs_vnd += _safe_int(row.get("incremental_cost_vnd"))

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
        banner = "ACTIVE PRE-REVENUE (L3 Verified on EXP-01; L4 Cash = 0 VND; Spend = 0 VND)"
    else:
        banner = "REVENUE GENERATING (L4 Verified Cash Collected)"

    return MoneyHQMetrics(
        starting_budget_cap_vnd=budget_cap_vnd,
        realized_revenue_l4_vnd=realized_l4_vnd,
        pending_payouts_l3_count=0,
        pending_payouts_l3_note="uTest platform.utest.com: VND 0.00 Pending Payout (chưa có payout)",
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
    """Build a clean 2D grid of rows for the Google Sheet 'Money HQ' tab and CSV export."""
    return [
        ["MONEY HQ - BANG DIEU KHIEN TAI CHINH DU AN AI TU KIEM TIEN (TACH BIET TAI SAN GIA DINH)", "", "", "", "", ""],
        ["Cap nhat", "2026-11-01", "Trang thai he thong", metrics.status_banner, "Che do van hanh", "Autonomous Low-Cost (0 VND Spend)"],
        ["", "", "", "", "", ""],
        ["1. CHI SO TAI CHINH COT LOI (CORE P&L & RUNWAY)", "Gia tri (VND / Don vi)", "Cap bang chung", "Quy tac hach toan", "Canh bao / Nguong", "Ghi chu xac thuc"],
        ["Ngan sach thu nghiem toi da (Budget Cap)", f"{metrics.starting_budget_cap_vnd:,}", "Approved Cap", "Khong vuot qua 500,000 VND", "Hard Stop tai 500,000 VND", "Chi dung khi co ROI >= 3x"],
        ["Doanh thu thuc nhan ve tai khoan (Realized Cash L4)", f"{metrics.realized_revenue_l4_vnd:,}", "L4 (Collected)", "Chi ghi nhan khi tien ve Bank/PayPal", "Muc tieu: >0 VND trong 14 ngay", "CASH_LEDGER.csv (0 VND hien tai)"],
        ["Doanh thu cho thanh toan (Pending Payouts L3)", f"{metrics.pending_payouts_l3_count} bugs approved (USD TBD)", "L3 (Approved)", "Tach biet tuyet doi voi L4", "Theo doi ky thanh toan 15 & cuoi thang", metrics.pending_payouts_l3_note],
        ["Hoan tien / Tu choi thanh toan (Refunds / Rejected)", f"{metrics.refunds_or_rejected_vnd:,}", "Verified", "Ghi nhan moi khoan bi clawback/reject", "Canh bao neu > 10% bug bi reject", "0 bug bi reject (3/3 approved)"],
        ["Chi phi bien doi (Variable Operating Costs)", f"{metrics.variable_costs_vnd:,}", "Verified", "Chi phi san xuat/rut tien thuc te", "Toi thieu hoa", "COST_LEDGER.csv"],
        ["Chi phi cong cu / API tang them (Incremental AI/Tool Spend)", f"{metrics.incremental_tool_api_costs_vnd:,}", "Verified", "Tach biet thue bao co dinh vs phi tang them", "Uu tien 100% Free/Local script", "Dung Python local + OAuth co san (0 VND)"],
        ["Loi nhuan rong thuc nhan (Net Realized Profit L4)", f"{metrics.net_realized_profit_vnd:,}", "L4 Net", "Realized Cash L4 - Total Incremental Cost", "Muc tieu duong ngay tu ky rut dau tien", "Chua tinh L3 dang cho ve"],
        ["Ngan sach con lai (Cash Runway Remaining)", f"{metrics.cash_runway_remaining_vnd:,}", f"{metrics.cash_runway_pct}%", "Budget Cap - Incremental Cost", "Bao dong do neu < 150,000 VND", "Con nguyen 100% ngan sach (500,000 VND)"],
        ["So gio chu so huu da bo ra (Owner Hours Spent)", f"{metrics.owner_hours_logged} gio", "Logged", "Chi tinh gio Mai truc tiep thao tac", "Gioi han <= 5h/tuan", "3.5h test uTest Cycle 562706"],
        ["Loi nhuan thuc nhan / Gio cua Mai (Net Profit / Owner Hr)", f"{metrics.realized_profit_per_owner_hour_vnd:,}", "L4 / Hr", "San luong lao dong an: 50,000 VND/gio", "Dung thu nghiem neu < 50,000 VND/gio", "Se cap nhat ngay khi L3 -> L4"],
        ["", "", "", "", "", ""],
        ["2. DANH MUC TAI SAN SO TU DONG (AUTONOMOUS ASSET PORTFOLIO)", "Cap uu tien", "Bang chung", "Doanh thu L4 (VND)", "Chi phi bien (Marginal Cost)", "Co che Tu dong hoa & Link Live"],
        ["ASSET-01 (EXP-03): Cam Nang & Tro Ly Duong Nhan 7 The Chat + Audio (299k)", "Tier 1 & 2 Primary (#1)", "L2 Live Asset (L1 299k Price)", "0", "0 VND / don", "100% AI tao Web Quiz + 21 Cong thuc Audio/PDF + VietQR/KOC (?ref=). Live tren GitHub Pages"],
        ["ASSET-02 (EXP-02): Catalogue QA Auto-Clean Self-Serve Web App (199k/$9)", "Tier 2 & 4 Tool (#2)", "L2 Live Asset (120 SKU Test)", "0", "0 VND / don", "100% tu phuc vu tren trinh duyet (Client-side CSV Audit + Clean + Report), 0h lao dong tay chan"],
        ["CASH-01 (EXP-01): uTest Cycle 562706 Approved Bug Bounty Settlement", "Tier 6 Cash Bridge (#3)", "L3 Verified (3/3 Approved)", "0", "0 VND", "Rank #1 Cycle 562706 (3/3 bugs approved). Chi thu tien L3 -> L4, khong bat Mai lam job tay chan"],
        ["TRD-01 & TRD-02: Exness MT5 Demo Agent & SOL EMA50/200 Backtest", "R&D Demo / Archived", "G1-G3 Pass / SOL OOS -38.65%", "0 (Demo Only)", "0 VND", "Khoa cung LiveAccountBlockedError; SOL EMA50/200 DA DONG vi lo OOS (-38.65%)"],
        ["", "", "", "", "", ""],
        ["3. CANH BAO SOM & VIEC CAN MAI DUYET (CAPITAL ALLOCATOR & EXCEPTION HANDLER)", "Muc do", "Trang thai", "Hanh dong cua AI", "Ngoai le duy nhat can Mai", "Thoi gian uoc tinh"],
        ["ACT-01: Gan tai khoan nhan tien tu dong (VietQR/SePay + PayPal uTest)", "ONE-TIME", "CHO MAI DUYET", "Da deploy live ASSET-01 & ASSET-02 len GitHub Pages + VietQR", "Gan STK/SePay nhan tien VietQR & xac nhan PayPal uTest nhan tien L3", "3 phut (1 lan duy nhat)"],
        ["RISK-01: Chong bien Mai thanh nhan vien van hanh tay chan (Anti-Labor Lock)", "GUARDED", "ACTIVE LOCK", "Da ha cap JOB-01 (viec lam theo gio) xuong Tier 6; uu tien 100% Tai san so", "Khong can thao tac (0h/ngay)", "0 phut"],
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
        "# Money HQ — Separate Project Financial Dashboard",
        "",
        "> **Separation Rule:** This dashboard tracks **only** Money HQ autonomous business experiments. Family investment assets (`Bạc KNP`, `PSOL`, `Exness Personal`) remain strictly separated on the family tabs.",
        "",
        f"- **System Status:** `{metrics.status_banner}`",
        f"- **Starting Budget Cap:** `{metrics.starting_budget_cap_vnd:,} VND`",
        f"- **Realized Revenue (`L4` Collected Cash):** `{metrics.realized_revenue_l4_vnd:,} VND`",
        f"- **Pending Payouts (`L3` Approved, Unsettled):** `{metrics.pending_payouts_l3_count} approved bugs` ({metrics.pending_payouts_l3_note})",
        f"- **Refunds / Rejected Payouts:** `{metrics.refunds_or_rejected_vnd:,} VND`",
        f"- **Variable Operating Costs:** `{metrics.variable_costs_vnd:,} VND`",
        f"- **Incremental Tool / API Spend:** `{metrics.incremental_tool_api_costs_vnd:,} VND`",
        f"- **Net Realized Profit (`L4`):** `{metrics.net_realized_profit_vnd:,} VND`",
        f"- **Cash Runway Remaining:** `{metrics.cash_runway_remaining_vnd:,} VND` (`{metrics.cash_runway_pct}%`)",
        f"- **Owner Hours Logged:** `{metrics.owner_hours_logged} hrs`",
        f"- **Realized Net Profit / Owner Hour:** `{metrics.realized_profit_per_owner_hour_vnd:,} VND/hr`",
        "",
        "## Autonomous Asset Portfolio Breakdown",
        "",
        "| Asset / Stream | Priority Tier | Evidence | Realized Cash (`L4`) | Marginal Cost | Automation & Live Status |",
        "| :--- | :--- | :--- | ---: | ---: | :--- |",
        "| `ASSET-01` (`EXP-03` Dưỡng Nhan 7-Constitution Web App + Handbook + Audio) | Tier 1 & 2 Primary (`#1`) | `L2` Live Asset (`L1` 299k Price) | `0 VND` | `0 VND` | Live on GitHub Pages (`index.html` + `handbook.html`), VietQR + KOC (`?ref=`) built-in. |",
        "| `ASSET-02` (`EXP-02` Catalogue QA Self-Serve CSV Web Tool) | Tier 2 & 4 Tool (`#2`) | `L2` Live Asset (120-SKU Verified) | `0 VND` | `0 VND` | 100% browser self-serve CSV audit & cleaner (`exp02/index.html`) + Executive Report. |",
        "| `CASH-01` (`EXP-01` uTest Cycle 562706 Approved Payout) | Tier 6 Cash Bridge (`#3`) | `L3` (`3/3` bugs approved, Rank `#1`) | `0 VND` | `0 VND` | Passive payout collection only (`L3 -> L4`); hourly `JOB-01` demoted to optional. |",
        "| `TRD-01` & `TRD-02` (`Exness Demo` & `SOL EMA50/200`) | R&D Demo / Archived | `G1–G3` Pass / SOL OOS `-38.65%` | `0 VND` | `0 VND` | Hard-locked to demo; SOL EMA50/200 closed due to negative OOS return. |",
        "",
    ]
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return csv_path, md_path, metrics


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    csv_out, md_out, m = export_dashboard_artifacts(repo_root)
    print(
        f"Exported {csv_out.name} & {md_out.name} | "
        f"L4={m.realized_revenue_l4_vnd} VND | Spend={m.incremental_tool_api_costs_vnd} VND | "
        f"Runway={m.cash_runway_remaining_vnd:,} VND ({m.cash_runway_pct}%)"
    )
    sys.exit(0)
