import tempfile
import unittest
from pathlib import Path

from tools.risk_review import review_finance, review_mt5


class RiskReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "finance").mkdir()
        (self.root / "finance/CASH_LEDGER.csv").write_text(
            "net_usable_cash,currency,proof_reference_redacted\n", encoding="utf-8"
        )
        (self.root / "finance/COST_LEDGER.csv").write_text(
            "amount,currency,owner_approved\n", encoding="utf-8"
        )
        (self.root / "finance/AI_USAGE_AND_COST_LOG.csv").write_text(
            "incremental_cost_vnd\n", encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_cost_without_approval_and_cash_is_flagged(self):
        (self.root / "finance/COST_LEDGER.csv").write_text(
            "amount,currency,owner_approved\n10000,VND,no\n", encoding="utf-8"
        )
        (self.root / "finance/AI_USAGE_AND_COST_LOG.csv").write_text(
            "incremental_cost_vnd\n10000\n", encoding="utf-8"
        )
        codes = {item["code"] for item in review_finance(self.root)}
        self.assertIn("COST_UNAPPROVED", codes)
        self.assertIn("AI_COST_EXCEEDS_PROVEN_CASH", codes)

    def test_unproven_cash_does_not_cover_ai_spend(self):
        (self.root / "finance/CASH_LEDGER.csv").write_text(
            "net_usable_cash,currency,proof_reference_redacted\n100000,VND,\n", encoding="utf-8"
        )
        (self.root / "finance/AI_USAGE_AND_COST_LOG.csv").write_text(
            "incremental_cost_vnd\n1000\n", encoding="utf-8"
        )
        codes = {item["code"] for item in review_finance(self.root)}
        self.assertIn("AI_COST_EXCEEDS_PROVEN_CASH", codes)

    def test_missing_mt5_guards_fail_closed(self):
        issues = review_mt5(self.root)
        self.assertEqual(issues[0]["code"], "MT5_GUARD_MISSING")


if __name__ == "__main__":
    unittest.main()
