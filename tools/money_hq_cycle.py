"""Zero-API Money HQ handoff: scout -> finance/risk gate -> local offer draft.

Runs after Public Demand Scout. This never contacts a prospect, spends money,
starts MT5, or counts a public discussion as a sale. Runtime files are ignored
by Git. The only automatic execution is a bounded, reversible local draft for
one new candidate with explicit buyer language.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from tools.money_hq_dashboard import compute_money_hq_metrics
from tools.risk_review import review_finance, review_mt5, review_site

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "operations" / "public_demand_scout"


def _recent_candidates(path: Path, now: datetime) -> list[dict]:
    if not path.is_file():
        return []
    candidates: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            checked = datetime.fromisoformat(row["checked_at"].replace("Z", "+00:00"))
        except (ValueError, KeyError, TypeError):
            continue
        if (row.get("opportunity_status") == "buyer_intent_to_verify"
                and checked.tzinfo is not None
                and now - timedelta(days=7) <= checked.astimezone(timezone.utc) <= now
                and row.get("source_url")
                and row.get("signal_id")):
            candidates[row["signal_id"]] = row
    return sorted(candidates.values(), key=lambda row: row["checked_at"], reverse=True)


def run_cycle(root: Path = ROOT, runtime: Path = RUNTIME, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    finance = review_finance(root)
    mt5 = review_mt5(root, now)
    site = review_site(root)
    metrics = compute_money_hq_metrics(
        root / "finance/CASH_LEDGER.csv",
        root / "finance/COST_LEDGER.csv",
        root / "finance/AI_USAGE_AND_COST_LOG.csv",
    )
    issues = finance + mt5 + site
    prior_path = runtime / "executed_candidates.json"
    try:
        done = set(json.loads(prior_path.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        done = set()
    candidates = _recent_candidates(runtime / "signals.jsonl", now)
    target = next((row for row in candidates if row["signal_id"] not in done), None)
    action = "none"
    if target:
        # Generate a reviewable offer draft; original context, payer and channel
        # still need verification before any external action.
        runtime.mkdir(parents=True, exist_ok=True)
        draft = {
            "signal_id": target["signal_id"],
            "source_url": target["source_url"],
            "source_checked_at": target["checked_at"],
            "problem_claim": target["title"],
            "excerpt": target["excerpt"],
            "offer_hypothesis": "Provide one small, measurable data-quality or workflow fix using a synthetic sample first.",
            "verification_required": [
                "Read the original post and confirm current need and actual buyer.",
                "Check existing alternatives and why they fail for this case.",
                "Confirm a permitted contact channel and payment conditions before outreach.",
            ],
            "status": "LOCAL_DRAFT_ONLY_NOT_A_CUSTOMER",
            "created_at": now.isoformat(),
        }
        draft_path = runtime / "offer_draft_latest.json"
        draft_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        done.add(target["signal_id"])
        prior_path.write_text(json.dumps(sorted(done), ensure_ascii=False) + "\n", encoding="utf-8")
        action = "offer_draft_created"
    result = {
        "checked_at": now.isoformat(),
        "cash_collected_l4_vnd": metrics.realized_revenue_l4_vnd,
        "recorded_incremental_cost_vnd": metrics.variable_costs_vnd + metrics.incremental_tool_api_costs_vnd,
        "buyer_candidates_last_7d": len(candidates),
        "action": action,
        "risk_codes": [item["code"] for item in issues],
        "mt5_recent_heartbeat_and_guard": not bool(mt5),
        "next_gate": "Xác minh người mua và bối cảnh; duyệt cách liên hệ trước khi gửi" if target else "Chưa có tín hiệu mua mới; cải thiện đề nghị hiện có hoặc chất lượng nguồn",
    }
    runtime.mkdir(parents=True, exist_ok=True)
    (runtime / "cycle_latest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(run_cycle(), ensure_ascii=False))
