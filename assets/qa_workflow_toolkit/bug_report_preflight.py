"""Compliant Bug Report Pre-Flight Validator & Formatter for Crowdtesting (CASH-01).

Helps the human tester catch rejection triggers (WAD/WNF traps, missing steps, missing
attachments, accidental PII leaks) BEFORE manually submitting on uTest, Test IO, or Testlio.
Does NOT automate platform submissions or interact with testing platforms.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")


@dataclass(frozen=True)
class BugReportDraft:
    title: str
    environment: str
    url_or_build: str
    steps_to_reproduce: list[str]
    actual_result: str
    expected_result: str
    attachments: list[str]
    reproducibility: str = "Always (3/3)"
    checked_known_issues_list: bool = False
    verified_clean_session_or_incognito: bool = False


@dataclass
class PreflightResult:
    ready_to_submit: bool
    score_pct: int
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    formatted_markdown: str = ""


class BugReportPreflightValidator:
    """Validates draft bug reports against evidence-backed crowdtesting acceptance rules."""

    WNF_WAD_KEYWORDS = (
        "0 results",
        "no results found",
        "empty state",
        "editorial grid",
        "guest cart",
    )

    def validate(self, draft: BugReportDraft) -> PreflightResult:
        blockers: list[str] = []
        warnings: list[str] = []

        # 1. Title check
        clean_title = draft.title.strip()
        if len(clean_title) < 20:
            blockers.append("Title is too short (<20 chars). Include [Feature/Component] and exact failure.")
        if "-" not in clean_title and ":" not in clean_title and "[" not in clean_title:
            warnings.append(
                "Title lacks component prefix (recommended format: '[Checkout / Promo Code] - ...')."
            )

        # 2. Environment & URL check
        if not draft.environment.strip():
            blockers.append("Environment (OS, Browser/Device version) is missing.")
        if not draft.url_or_build.strip():
            blockers.append("URL or App Build version is missing.")

        # 3. Steps to Reproduce check
        steps = [s.strip() for s in draft.steps_to_reproduce if s.strip()]
        if len(steps) < 3:
            blockers.append("Steps to Reproduce must contain at least 3 clear, atomic steps.")

        # 4. Actual vs Expected Result check
        actual = draft.actual_result.strip()
        expected = draft.expected_result.strip()
        if len(actual) < 20:
            blockers.append("Actual Result is too brief (<20 chars). State exact observed behavior/error message.")
        if len(expected) < 20:
            blockers.append("Expected Result is too brief (<20 chars). State expected behavior per spec/UI promise.")
        if actual and expected and actual.lower() == expected.lower():
            blockers.append("Actual Result and Expected Result cannot be identical.")

        # 5. Evidence attachments check
        atts = [a.strip() for a in draft.attachments if a.strip()]
        if not atts:
            blockers.append("No evidence attachments listed (minimum 1 screenshot or screen recording required).")
        else:
            has_video = any(a.lower().endswith((".mp4", ".mov", ".webm")) for a in atts)
            if not has_video:
                warnings.append(
                    "No video attachment (.mp4/.webm) listed. Functional bugs on uTest/TestIO usually require a short reproduction video."
                )

        # 6. Duplicate & Session hygiene gates (from BUG_LESSONS.md)
        if not draft.checked_known_issues_list:
            blockers.append("Known Issues / Duplicate list check is False. Verify cycle issue list before submitting.")
        if not draft.verified_clean_session_or_incognito:
            warnings.append(
                "Clean session / incognito verification is False. Confirm state does not leak from a prior account/cart."
            )

        # 7. WAD / WNF heuristic warnings from BUG_LESSONS.md
        combined_text = f"{clean_title} {actual} {expected}".lower()
        for kw in self.WNF_WAD_KEYWORDS:
            if kw in combined_text:
                warnings.append(
                    f"Heuristic caution ('{kw}'): Per BUG_LESSONS.md, verify whether user still has a recovery path "
                    "(e.g. clearing filter) or if guest cart retention is working-as-designed (WAD)."
                )

        # 8. PII / Secret leak check
        full_blob = "\n".join([clean_title, draft.environment, draft.url_or_build, *steps, actual, expected])
        if EMAIL_RE.search(full_blob) or CARD_RE.search(full_blob):
            blockers.append(
                "PRIVACY GATE: Detected raw email address or card-like number in report text. Redact PII before submitting."
            )

        deductions = len(blockers) * 25 + len(warnings) * 5
        score = max(0, 100 - deductions)
        ready = len(blockers) == 0

        return PreflightResult(
            ready_to_submit=ready,
            score_pct=score,
            blockers=blockers,
            warnings=warnings,
            formatted_markdown=self.format_report(draft),
        )

    @staticmethod
    def format_report(draft: BugReportDraft) -> str:
        steps_lines = [
            f"{idx}. {re.sub(r'^[0-9]+[.)]\\s*', '', step.strip())}"
            for idx, step in enumerate(draft.steps_to_reproduce, start=1)
            if step.strip()
        ]
        att_lines = [f"- `{a.strip()}`" for a in draft.attachments if a.strip()]

        return "\n".join(
            [
                f"### Title\n{draft.title.strip()}",
                "",
                "### Environment",
                f"- **Device / OS / Browser:** {draft.environment.strip()}",
                f"- **URL / Build:** {draft.url_or_build.strip()}",
                f"- **Reproducibility:** {draft.reproducibility.strip()}",
                "",
                "### Steps to Reproduce",
                *steps_lines,
                "",
                "### Actual Result",
                draft.actual_result.strip(),
                "",
                "### Expected Result",
                draft.expected_result.strip(),
                "",
                "### Attachments",
                *(att_lines or ["- None"]),
                "",
            ]
        )
