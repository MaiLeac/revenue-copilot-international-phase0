"""Gemini Independent Reviewer for MT5 Demo Trading Engine.

Performs read-only adversarial audits using Google Gemini Free Tier API.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import urllib.request
from pathlib import Path

# Force IPv4 resolution to prevent dual-stack IPv6 hangs on Windows
_orig_getaddrinfo = socket.getaddrinfo


def _getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)


socket.getaddrinfo = _getaddrinfo_ipv4_only


def get_gemini_key() -> str:
    # Read strictly from environment or local .env file (never hardcode in repo)
    key = os.environ.get("GEMINI_API_KEY")
    if key and (key.startswith("AQ.") or key.startswith("AIza")):
        return key

    # Check local .env in user root if present
    env_file = Path.home() / "agent-zero" / "agent-zero" / "usr" / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    raise ValueError("GEMINI_API_KEY environment variable is required to run independent audit.")


def read_repo_files(repo_root: Path) -> dict[str, str]:
    target_files = [
        "app/mt5/execution.py",
        "app/mt5/connection.py",
        "app/risk/kill_switch.py",
        "app/data/quality_gate.py",
        "app/daemon.py",
        "app/strategies/baseline.py",
        "config/demo.yaml",
        "tests/test_execution.py",
        "tests/test_risk.py",
    ]
    bundle = {}
    for rel_path in target_files:
        full_path = repo_root / rel_path
        if full_path.exists():
            bundle[rel_path] = full_path.read_text(encoding="utf-8")
    return bundle


def run_gemini_audit(repo_root: Path, prompt_mode: str = "first_pass", extra_context: str = "") -> str:
    api_key = get_gemini_key()
    files = read_repo_files(repo_root)

    files_text = "\n\n".join([f"=== FILE: {path} ===\n{content}" for path, content in files.items()])

    if prompt_mode == "first_pass":
        instructions = f"""You are the Gemini Independent Security & Architecture Reviewer for an automated MetaTrader 5 trading engine.
Your mission is to perform a strict, read-only ADVERSARIAL AUDIT of the codebase below.

Evaluate the code specifically against these 6 non-negotiable areas:
1. Position sizing and monetary risk calculations:
   - Lot quantization, broker volume_min/volume_max/volume_step adherence.
   - Contract size and deposit currency conversion (does pip distance calculation hold for commodities XAU/XAG vs Forex EURUSD?).
   - Margin/leverage sufficiency check prior to order send.
   - Zero division or float overflow risks.
2. MT5 order execution and duplicate-order prevention:
   - Idempotency and duplicate order firing (what happens if tick arrives rapidly or daemon restarts?).
   - Magic number separation and position filtering.
   - Slippage deviation tolerance and order type filling modes (IOC vs RETURN).
   - In-flight order race conditions.
3. Risk Manager and kill-switch enforcement:
   - Can the kill switch or risk manager be bypassed by any code path?
   - Daily loss limit calculation and peak-to-trough drawdown logic.
   - Strict Stop-Loss enforcement.
4. Account verification and demo-only restrictions:
   - Can this code ever place an order on a real/live account?
   - Broker symbol suffixes (e.g., EURUSDm, XAUUSDm) vs standard symbol discovery.
   - Strict server name and trade_mode validation.
5. Persistence, recovery, and race conditions:
   - Atomic writes to run_state.json.
   - Daemon recovery after unexpected crash: does it recognize already open positions or does it double-down?
6. Backtest methodology, metrics, and data integrity:
   - Lookahead bias, spread/commission cost inclusion, train/test leakage.

RULES FOR YOUR FINDINGS:
- Be brutally critical and adversarial. Look for subtle edge cases and production bugs.
- For each finding, provide:
  * ID (e.g. AUDIT-01)
  * Severity: [CRITICAL | HIGH | MEDIUM | LOW]
  * Focus Area (1 through 6)
  * File and Approximate Line Reference
  * Vulnerability / Failure Scenario
  * Proposed Concrete Fix (code snippet)

SOURCE CODE TO AUDIT:
{files_text}
"""
    else:
        instructions = f"""You are the Gemini Independent Reviewer for the MT5 Demo Trading Engine.
This is the SECOND PASS verification. The engineering team has implemented fixes and provided updated code and test results.

Verify whether the previous audit findings have been adequately resolved and whether any new vulnerabilities or regressions were introduced.

CODE BASE & CHANGES:
{files_text}

EXTRA VERIFICATION CONTEXT & TEST RESULTS:
{extra_context}

Please provide:
1. Verification status for each previous finding (RESOLVED / PARTIALLY RESOLVED / UNRESOLVED).
2. Assessment of overall system robustness.
3. Final verdict: APPROVE for autonomous demo execution or REQUIRE FURTHER HARDENING.
"""

    models_to_try = ["gemini-flash-lite-latest", "gemini-3.1-flash-lite-preview", "gemini-2.5-flash"]
    last_err = None

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": instructions}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        try:
            print(f"Connecting to Gemini API using model '{model_name}'...")
            with urllib.request.urlopen(req, timeout=60) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                output_text = res["candidates"][0]["content"]["parts"][0]["text"]
                print(f"Gemini Independent Review completed successfully via {model_name}!")
                return output_text
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            print(f"Model {model_name} returned HTTP {e.code}: {err_body[:200]}")
            last_err = f"HTTP {e.code}: {err_body}"
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            last_err = str(e)

    raise RuntimeError(f"All Gemini models failed. Last error: {last_err}")


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[1]
    mode = sys.argv[1] if len(sys.argv) > 1 else "first_pass"
    result = run_gemini_audit(repo, prompt_mode=mode)
    
    audit_file = repo / "research" / "GEMINI_INDEPENDENT_AUDIT.md"
    audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    header = f"# Gemini Independent Adversarial Audit Report\n\n**Reviewer:** Google Gemini (Gemini Free Tier API)\n**Date:** {Path().cwd()}\n**Pass:** {mode.upper()}\n\n"
    if mode == "first_pass":
        audit_file.write_text(header + result, encoding="utf-8")
    else:
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write("\n\n---\n\n" + header + result)
            
    print(f"Audit report written to {audit_file}")
