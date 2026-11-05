"""Read-only, zero-API review of Money HQ's highest-impact local risks.

Prints a compact JSON result. Never prints secret values or ledger notes.
Exit 2 means an actionable high-risk finding; 0 means no such finding.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNED_SUFFIXES = {".md", ".txt", ".py", ".js", ".cjs", ".ts", ".tsx", ".html", ".json", ".yaml", ".yml", ".env"}
SECRET_RULES = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b"),
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b"),
    "google_api_key": re.compile(r"\bAIza[A-Za-z0-9_-]{35}\b"),
}


def finding(code: str, severity: str, status: str, evidence: str, action: str) -> dict[str, str]:
    return dict(code=code, severity=severity, status=status, evidence=evidence, action=action)


def rows(path: Path) -> list[dict[str, str]] | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def money(raw: str | None) -> Decimal | None:
    try:
        value = Decimal((raw or "").strip())
        return value if value.is_finite() else None
    except InvalidOperation:
        return None


def review_finance(root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    cash = rows(root / "finance/CASH_LEDGER.csv")
    costs = rows(root / "finance/COST_LEDGER.csv")
    ai = rows(root / "finance/AI_USAGE_AND_COST_LOG.csv")
    if cash is None or costs is None or ai is None:
        return [finding("LEDGER_MISSING", "high", "unverified", "finance/*.csv", "Restore all three finance ledgers before relying on revenue or cost claims.")]
    verified_cash_vnd = Decimal(0)
    for i, row in enumerate(cash, start=2):
        amount = money(row.get("net_usable_cash"))
        if amount is None:
            issues.append(finding("CASH_INVALID", "high", "open", f"finance/CASH_LEDGER.csv:{i}", "Correct the numeric net cash entry."))
        elif (row.get("status", "").strip().upper() == "L4_COLLECTED_CASH"
              and row.get("currency", "").upper() == "VND"
              and row.get("proof_reference_redacted", "").strip()):
            verified_cash_vnd += amount
    ai_cost_vnd = Decimal(0)
    for i, row in enumerate(ai, start=2):
        amount = money(row.get("incremental_cost_vnd"))
        if amount is None or amount < 0:
            issues.append(finding("AI_COST_INVALID", "high", "open", f"finance/AI_USAGE_AND_COST_LOG.csv:{i}", "Correct the incremental cost entry."))
        else:
            ai_cost_vnd += amount
    for i, row in enumerate(costs, start=2):
        amount = money(row.get("amount"))
        if amount is None or amount < 0:
            issues.append(finding("COST_INVALID", "high", "open", f"finance/COST_LEDGER.csv:{i}", "Correct the cost entry."))
        elif amount > 0 and row.get("owner_approved", "").strip().lower() not in {"yes", "true", "approved", "có", "da duyet", "đã duyệt"}:
            issues.append(finding("COST_UNAPPROVED", "critical", "open", f"finance/COST_LEDGER.csv:{i}", "Stop further spend; obtain and record owner approval."))
    if ai_cost_vnd > verified_cash_vnd:
        issues.append(finding("AI_COST_EXCEEDS_PROVEN_CASH", "high", "open", "finance/AI_USAGE_AND_COST_LOG.csv", "Stop incremental AI spend and reconcile revenue proof and costs."))
    if not cash:
        issues.append(finding("NO_RECORDED_CASH", "info", "unverified", "finance/CASH_LEDGER.csv", "Do not describe demos, backtests or agent logs as collected revenue."))
    return issues


def review_mt5(root: Path, now: datetime | None = None) -> list[dict[str, str]]:
    config = root / "trading-agent-exness-demo/config/demo.yaml"
    source = root / "trading-agent-exness-demo/app/mt5/execution.py"
    if not config.is_file() or not source.is_file():
        return [finding("MT5_GUARD_MISSING", "critical", "unverified", "trading-agent-exness-demo", "Keep MT5 disconnected until demo-only guards are reviewed.")]
    cfg = config.read_text(encoding="utf-8")
    code = source.read_text(encoding="utf-8")
    if not re.search(r"(?m)^account_mode:\s*demo_only\s*$", cfg) or "ACCOUNT_TRADE_MODE_DEMO" not in code:
        return [finding("MT5_DEMO_GUARD_CHANGED", "critical", "open", "trading-agent-exness-demo", "Stop MT5 execution and inspect account mode and order guard.")]
    state_file = root / "trading-agent-exness-demo/run_state.json"
    if not state_file.is_file():
        return [finding("MT5_RUNTIME_UNVERIFIED", "info", "unverified", "trading-agent-exness-demo/run_state.json", "Check the demo daemon before claiming that it is scanning markets.")]
    try:
        state = json.loads(state_file.read_text(encoding="utf-8"))
        if state.get("status") != "RUNNING":
            return [finding("MT5_DEMO_INACTIVE", "info", "verified", "trading-agent-exness-demo/run_state.json", "Inspect the demo daemon; do not claim market scanning from a saved state file.")]
        heartbeat = datetime.fromisoformat(state["last_heartbeat_utc"].replace("Z", "+00:00"))
        if heartbeat.tzinfo is None:
            raise ValueError("heartbeat lacks timezone")
        age = (now or datetime.now(timezone.utc)) - heartbeat.astimezone(timezone.utc)
    except (OSError, ValueError, KeyError, TypeError):
        return [finding("MT5_HEARTBEAT_INVALID", "high", "open", "trading-agent-exness-demo/run_state.json", "Do not claim the demo bot is running; inspect the daemon and state writer.")]
    if age > timedelta(minutes=5) or age < -timedelta(minutes=1):
        return [finding("MT5_HEARTBEAT_STALE", "high", "open", "trading-agent-exness-demo/run_state.json", "Do not claim the demo bot is running; inspect the process and restart only after demo guards are verified.")]
    return []


def review_site(root: Path) -> list[dict[str, str]]:
    path = root / "experiments/exp03-duong-nhan-ai-mvp/products.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError):
        return [finding("PRODUCTS_INVALID", "high", "open", str(path.relative_to(root)), "Fix the product file before showing a checkout.")]
    text = json.dumps(data, ensure_ascii=False).lower()
    if '"status": "draft"' in text:
        return [finding("PRODUCT_DRAFT", "info", "verified", str(path.relative_to(root)), "Keep payment closed until the digital product is deliverable.")]
    return []


def review_tracked_secrets(root: Path, git_executable: str = "git") -> list[dict[str, str]]:
    try:
        result = subprocess.run([git_executable, "ls-files", "-z"], cwd=root, check=True, capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return [finding("TRACKED_FILES_UNKNOWN", "high", "unverified", ".git", "Run the tracked-file secret review manually before publishing.")]
    issues = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8", errors="replace")
        path = root / relative
        if path.suffix.lower() not in SCANNED_SUFFIXES or not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for rule, pattern in SECRET_RULES.items():
            if pattern.search(content):
                issues.append(finding("TRACKED_SECRET_" + rule.upper(), "critical", "possible", relative, "Remove the secret from the working tree, rotate it, and inspect Git history before push."))
    return issues


def review(root: Path, git_executable: str = "git") -> dict[str, object]:
    issues = review_finance(root) + review_mt5(root) + review_site(root) + review_tracked_secrets(root, git_executable)
    return {"checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "repo": str(root), "risk_findings": issues, "high_or_critical": sum(i["severity"] in {"high", "critical"} for i in issues), "limits": ["Static checks cannot prove legal compliance, absence of secrets in Git history, real account separation, or cash receipt.", "VND cash comparison uses only entries with a proof reference; foreign-currency entries need independent FX reconciliation."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--git", default="git", help="Path to Git executable if the scheduler has no Git on PATH.")
    parser.add_argument("--output", type=Path, help="Write the report to a local file for the next operator run.")
    args = parser.parse_args()
    report = review(args.repo.resolve(), args.git)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        destination = args.output.resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(rendered + "\n", encoding="utf-8")
        temporary.replace(destination)
    print(rendered)
    return 2 if report["high_or_critical"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
