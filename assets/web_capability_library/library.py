"""Web Capability Library Query Engine & Independent Visual Quality Gate.

Enforces Hallmark Floor Gates (`Nutlope/hallmark`), Huashu Design hierarchy rules
(`alchaincyf/huashu-design`), and Flow-Scout UX patterns (`MaiLeac/flow-scout-core`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any

CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"
TOKENS_CSS_PATH = Path(__file__).resolve().parent / "tokens.css"


@dataclass(frozen=True)
class VisualAuditFinding:
    gate_id: str
    tier: str  # "FLOOR" (blocks ship), "REFLEX" (warn/waive), "UX_PAT" (Flow-Scout defect)
    message: str
    evidence: str = ""


@dataclass
class VisualAuditReport:
    target_path: str
    passed: bool
    score_100: int
    findings: list[VisualAuditFinding] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def floor_failures(self) -> list[VisualAuditFinding]:
        return [f for f in self.findings if f.tier in ("FLOOR", "UX_PAT")]


def load_catalog(catalog_path: Path = CATALOG_PATH) -> dict[str, Any]:
    return json.loads(catalog_path.read_text(encoding="utf-8"))


def search_capabilities(
    category: str | None = None,
    project: str | None = None,
    reuse_mode: str | None = None,
    query: str | None = None,
) -> list[dict[str, Any]]:
    """Query the curated GitHub capability catalog before implementing any UI feature."""
    catalog = load_catalog()
    results: list[dict[str, Any]] = []
    for item in catalog.get("resources", []):
        if category:
            cats = [c.lower() for c in item.get("categories", [])]
            if not any(category.lower() in c for c in cats):
                continue
        if project:
            projs = [p.lower() for p in item.get("target_projects", [])]
            if not any(project.lower() in p for p in projs):
                continue
        if reuse_mode and item.get("reuse_mode") != reuse_mode:
            continue
        if query:
            haystack = json.dumps(item, ensure_ascii=False).lower()
            if query.lower() not in haystack:
                continue
        results.append(item)
    return results


def get_approved_dependencies() -> dict[str, list[dict[str, str]]]:
    """Return license-verified, approved dependencies for React/TS and static HTML stacks."""
    return load_catalog().get("approved_dependencies", {})


def get_decision_guide() -> dict[str, str]:
    """Return the decision rules for when to reuse, adapt, or build from scratch."""
    return {
        "1_direct_reuse": (
            "Use directly when an approved MIT/Apache-2.0/ISC package or local module "
            "already solves the exact need (`tokens.css` for design tokens, `lucide-react` "
            "for icons, `Sisan/src/utils/distance.ts` for OSRM route distance, "
            "`flow-scout-core` for UX pattern validation)."
        ),
        "2_adapt_pattern": (
            "Adapt architectural/visual patterns when the target stack differs (`Nutlope/hallmark` "
            "material palettes & Floor Gates adapted into CSS variables; `eternity4719/HowToLiveBetter` "
            "cost-benefit-evidence card layout adapted into `EXP-03` Dưỡng Nhan; `alchaincyf/huashu-design` "
            "2.5x display/body hierarchy and 8pt spacing grid)."
        ),
        "3_build_from_scratch": (
            "Build from scratch ONLY for domain-specific business logic (e.g., 7-constitution "
            "Eastern medicine scoring or SKU margin leak detection), while still binding every "
            "visual surface to `tokens.css` and passing `tools/web_quality_gate.py`."
        ),
    }


_EMOJI_IN_HEADING_OR_BTN_RE = re.compile(
    r"<(h[1-3]|button)\b[^>]*>[^<]*[\U0001F300-\U0001FAFF\u2600-\u27BF]",
    re.IGNORECASE,
)
_GLUED_ARROW_IN_CTA_RE = re.compile(
    r"<(a|button)\b[^>]*>[^<]*(?:→|->|➔)\s*</\1>",
    re.IGNORECASE,
)
_DEAD_HREF_HASH_RE = re.compile(r'<a\b[^>]*\bhref=["\']#["\'][^>]*>', re.IGNORECASE)
_TRANSITION_ALL_RE = re.compile(r"(?:transition\s*:\s*all\b|\btransition-all\b)", re.IGNORECASE)
_TRACKED_UPPERCASE_EYEBROW_RE = re.compile(
    r"(?:text-transform\s*:\s*uppercase[^}]*letter-spacing\s*:\s*0\.[1-9]|letter-spacing\s*:\s*0\.[1-9][^}]*text-transform\s*:\s*uppercase|\buppercase\s+tracking-(?:wider|widest)\b)",
    re.IGNORECASE | re.DOTALL,
)


def audit_html_source(html_content: str, target_path: str = "<memory>") -> VisualAuditReport:
    """Run deterministic Hallmark Floor + Huashu + Flow-Scout quality checks on HTML/CSS/JSX."""
    findings: list[VisualAuditFinding] = []
    links_tokens_css = "tokens.css" in html_content

    # Gate 1: Design tokens (:root or tokens.css)
    if ":root" not in html_content and not links_tokens_css:
        findings.append(
            VisualAuditFinding(
                gate_id="GATE-TOKEN-01",
                tier="FLOOR",
                message="Missing `:root` CSS custom properties or link to `tokens.css` (Hallmark Floor #1).",
            )
        )

    # Gate 2: Never `transition: all` or `transition-all`
    m_trans = _TRANSITION_ALL_RE.search(html_content)
    if m_trans:
        findings.append(
            VisualAuditFinding(
                gate_id="GATE-TRANSITION-02",
                tier="FLOOR",
                message="Forbidden `transition: all` / `transition-all` detected (Hallmark Floor #2). Specify exact properties.",
                evidence=m_trans.group(0),
            )
        )

    # Gate 4: Horizontal overflow protection (`overflow-x: clip` or `tokens.css`) and no `100vw`
    if "100vw" in html_content:
        findings.append(
            VisualAuditFinding(
                gate_id="GATE-OVERFLOW-04",
                tier="FLOOR",
                message="Forbidden `100vw` detected (causes horizontal scrollbar when vertical scrollbar is present; Hallmark Floor #4).",
                evidence="100vw",
            )
        )

    # Gate 6 & 7: `:focus-visible` and `prefers-reduced-motion` (in inline CSS or via linked tokens.css)
    is_full_html_doc = "<html" in html_content.lower()
    if is_full_html_doc and not links_tokens_css:
        if ":focus-visible" not in html_content:
            findings.append(
                VisualAuditFinding(
                    gate_id="GATE-FOCUS-06",
                    tier="FLOOR",
                    message="Missing `:focus-visible` keyboard focus styles (Hallmark Floor #6).",
                )
            )
        if "prefers-reduced-motion" not in html_content:
            findings.append(
                VisualAuditFinding(
                    gate_id="GATE-MOTION-07",
                    tier="FLOOR",
                    message="Missing `@media (prefers-reduced-motion: reduce)` fallback (Hallmark Floor #7).",
                )
            )

    # Gate 9: Tracked-uppercase eyebrow labels
    m_eyebrow = _TRACKED_UPPERCASE_EYEBROW_RE.search(html_content)
    if m_eyebrow:
        findings.append(
            VisualAuditFinding(
                gate_id="GATE-EYEBROW-09",
                tier="FLOOR",
                message="Tracked-capitals eyebrow/label detected (Hallmark Floor #9). Use sentence case in body/label font.",
                evidence=m_eyebrow.group(0)[:80],
            )
        )

    # Gate 10: Glued arrows on CTA links/buttons
    m_arrow = _GLUED_ARROW_IN_CTA_RE.search(html_content)
    if m_arrow:
        findings.append(
            VisualAuditFinding(
                gate_id="GATE-PUNCT-10",
                tier="FLOOR",
                message="Arrow character glued to CTA link/button text (Hallmark Floor #10).",
                evidence=m_arrow.group(0)[:80],
            )
        )

    # Gate 11: Emoji used inside headings or buttons
    m_emoji = _EMOJI_IN_HEADING_OR_BTN_RE.search(html_content)
    if m_emoji:
        findings.append(
            VisualAuditFinding(
                gate_id="GATE-SLOP-11",
                tier="FLOOR",
                message="Emoji used inside heading or button (Hallmark Floor #11). Use SVG icons or clean typography.",
                evidence=m_emoji.group(0)[:80],
            )
        )

    # Gate Flow-Scout PAT-08: Dead `<a href="#">` links
    m_dead = _DEAD_HREF_HASH_RE.search(html_content)
    if m_dead:
        findings.append(
            VisualAuditFinding(
                gate_id="GATE-FLOWSCOUT-PAT08",
                tier="UX_PAT",
                message="Dead placeholder link `<a href=\"#\">` detected (Flow-Scout PAT-08).",
                evidence=m_dead.group(0)[:80],
            )
        )

    # Gate 12: Commercial footer on full HTML pages
    if is_full_html_doc and "<footer" not in html_content.lower():
        findings.append(
            VisualAuditFinding(
                gate_id="GATE-TRUST-12",
                tier="FLOOR",
                message="Missing semantic `<footer>` element with support/provenance details.",
            )
        )

    deduction = sum(20 if f.tier in ("FLOOR", "UX_PAT") else 8 for f in findings)
    score = max(0, 100 - deduction)
    passed = len([f for f in findings if f.tier in ("FLOOR", "UX_PAT")]) == 0

    return VisualAuditReport(
        target_path=target_path,
        passed=passed,
        score_100=score,
        findings=findings,
        metrics={
            "total_findings": len(findings),
            "floor_failures": len([f for f in findings if f.tier in ("FLOOR", "UX_PAT")]),
            "links_tokens_css": links_tokens_css,
        },
    )


def audit_html_file(path: Path) -> VisualAuditReport:
    content = path.read_text(encoding="utf-8", errors="replace")
    return audit_html_source(content, target_path=str(path))
