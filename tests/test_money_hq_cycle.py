import json
from datetime import datetime, timezone

from tools.money_hq_cycle import run_cycle
from tools.money_hq_dashboard import compute_money_hq_metrics


def _ledgers(root):
    finance = root / "finance"
    finance.mkdir()
    (finance / "CASH_LEDGER.csv").write_text(
        "status,currency,net_usable_cash,proof_reference_redacted,refunds,owner_hours\n"
        "L4_COLLECTED_CASH,VND,100000,,0,0\n"
        "L4_COLLECTED_CASH,VND,200000,receipt-1,0,0\n", encoding="utf-8")
    (finance / "COST_LEDGER.csv").write_text(
        "amount,currency,purpose,owner_approved\n10000,VND,hosting,yes\n", encoding="utf-8")
    (finance / "AI_USAGE_AND_COST_LOG.csv").write_text(
        "incremental_cost_vnd\n2000\n", encoding="utf-8")


def test_finance_uses_proof_and_correct_ai_cost_column(tmp_path):
    _ledgers(tmp_path)
    metric = compute_money_hq_metrics(
        tmp_path / "finance/CASH_LEDGER.csv",
        tmp_path / "finance/COST_LEDGER.csv",
        tmp_path / "finance/AI_USAGE_AND_COST_LOG.csv")
    assert metric.realized_revenue_l4_vnd == 200000
    assert metric.incremental_tool_api_costs_vnd == 2000


def test_cycle_creates_one_local_draft_and_does_not_claim_sale(tmp_path):
    _ledgers(tmp_path)
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    now = datetime(2026, 11, 6, tzinfo=timezone.utc)
    signal = {
        "signal_id": "hn:1", "source_url": "https://news.ycombinator.com/item?id=1",
        "checked_at": now.isoformat(), "title": "Need help with CSV", "excerpt": "I have a budget",
        "opportunity_status": "buyer_intent_to_verify",
    }
    (runtime / "signals.jsonl").write_text(json.dumps(signal) + "\n", encoding="utf-8")
    first = run_cycle(tmp_path, runtime, now)
    second = run_cycle(tmp_path, runtime, now)
    assert first["action"] == "offer_draft_created"
    assert second["action"] == "none"
    assert first["cash_collected_l4_vnd"] == 200000
    draft = json.loads((runtime / "offer_draft_latest.json").read_text(encoding="utf-8"))
    assert draft["status"] == "LOCAL_DRAFT_ONLY_NOT_A_CUSTOMER"
