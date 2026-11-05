"""Flag stale current-status claims before an agent reports or republishes them.

This is a read-only consistency check, not a substitute for bank or service checks.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
CURRENT = [
    "README.md",
    "AGENTS.md",
    "AI_MANDATE_CONSTITUTION.md",
    "OPERATING_SYSTEM.md",
    "PROJECT_STATE.md",
    "agents/AI_ROUTING_POLICY.md",
    "agents/COST_OPTIMIZATION_POLICY.md",
    "portfolio/OPPORTUNITY_REGISTER.md",
    "portfolio/WINK_ECOSYSTEM_CHARTER.md",
    "operations/ATTENTION_PANEL.md",
    "operations/DAILY_BRIEF.md",
    "operations/OWNER_ACTIONS.md",
    "finance/MONEY_HQ_DASHBOARD.md",
]
FALSE_CURRENT_CLAIMS = re.compile(
    r"mua sách tặng trà|live 100%|100% ready|zero traffic|"
    r"vietqr.{0,25}(?:24/7|tự động|active)|"
    r"(?:199|299|389)[.,]000\s*(?:đ|vnd)",
    re.IGNORECASE,
)
LOCAL_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def main() -> int:
    errors: list[str] = []
    for relative in CURRENT:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing current document: {relative}")
            continue
        body = path.read_text(encoding="utf-8-sig")
        # Negated warnings such as "do not claim zero traffic" are allowed.
        for line_no, line in enumerate(body.splitlines(), 1):
            if FALSE_CURRENT_CLAIMS.search(line) and not any(
                word in line.lower()
                for word in ("không", "chưa", "đừng", "do not", "not ", "từng", "historical")
            ):
                errors.append(f"stale commercial claim: {relative}:{line_no}")
        for target in LOCAL_LINK.findall(body):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            dest = (path.parent / target.split("#", 1)[0]).resolve()
            if not dest.exists():
                errors.append(f"broken link: {relative} -> {target}")

    cash = ROOT / "finance/CASH_LEDGER.csv"
    with cash.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if any((row.get("status") or "").upper() == "L4_COLLECTED_CASH" for row in rows):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig").lower()
        if "chưa ghi nhận tiền thu" in readme:
            errors.append("README still says no cash was recorded after an L4 ledger row")

    products = json.loads((ROOT / "experiments/exp03-duong-nhan-ai-mvp/products.json").read_text(encoding="utf-8"))
    if any(p.get("status") == "available" for p in products["products"]):
        readme = (ROOT / "README.md").read_text(encoding="utf-8-sig").lower()
        if any(phrase in readme for phrase in ("chưa mở bán", "chưa có giá", "web bản thảo hiện mới là bản giới thiệu")):
            errors.append("README describes a draft/no sale while catalog has an available product")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(CURRENT)} current documents, links, ledger/catalog state")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
