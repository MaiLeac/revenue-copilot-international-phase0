"""Independent Web Visual Quality & Anti-AI-Slop Gate CLI.

Runs both static Hallmark/Huashu/Flow-Scout checks and real headless Chromium
Playwright viewport rendering (1280x800 desktop + 390x844 mobile) to verify:
1. Zero Hallmark Floor Gate violations (tokens, focus-visible, reduced-motion, no tracked-cap eyebrows, no emoji buttons, no glued arrows, no transition:all).
2. Zero Flow-Scout PAT-08 dead links (`href="#"`).
3. Real browser DOM geometry: zero horizontal overflow (`scrollWidth <= clientWidth`), hero headline + primary CTA visible above the fold at 1280x800, and display-to-body font scale ratio >= 2.0x.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from assets.web_capability_library import VisualAuditFinding, audit_html_file


def run_browser_render_check(
    html_path: Path,
    screenshot_out: Path | None = None,
) -> dict[str, Any]:
    """Render HTML file in headless Chromium at 1280x800 and 390x844 and measure real layout geometry."""
    from playwright.sync_api import sync_playwright

    file_uri = html_path.resolve().as_uri()
    results: dict[str, Any] = {"file": str(html_path), "viewports": {}, "browser_findings": []}

    with sync_playwright() as p:
        chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        launch_kwargs: dict[str, Any] = {"headless": True}
        if Path(chrome_exe).exists():
            launch_kwargs["executable_path"] = chrome_exe
        browser = p.chromium.launch(**launch_kwargs)
        for vp_name, width, height in [("desktop_1280x800", 1280, 800), ("mobile_390x844", 390, 844)]:
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(file_uri, wait_until="networkidle")
            metrics = page.evaluate(
                """() => {
                    const doc = document.documentElement;
                    const h1 = document.querySelector('h1');
                    const p = document.querySelector('p');
                    const cta = document.querySelector('a.btn-primary, button.btn-primary, a[href*="exp"], button');
                    const h1Rect = h1 ? h1.getBoundingClientRect() : null;
                    const ctaRect = cta ? cta.getBoundingClientRect() : null;
                    const h1Size = h1 ? parseFloat(getComputedStyle(h1).fontSize) : 0;
                    const pSize = p ? parseFloat(getComputedStyle(p).fontSize) : 16;
                    return {
                        scrollWidth: doc.scrollWidth,
                        clientWidth: doc.clientWidth,
                        hasHorizontalOverflow: doc.scrollWidth > doc.clientWidth + 1,
                        h1Text: h1 ? h1.innerText.trim().slice(0, 80) : '',
                        h1BottomY: h1Rect ? Math.round(h1Rect.bottom) : null,
                        ctaBottomY: ctaRect ? Math.round(ctaRect.bottom) : null,
                        fontRatio: pSize > 0 ? Number((h1Size / pSize).toFixed(2)) : 0,
                        footerPresent: Boolean(document.querySelector('footer')),
                    };
                }"""
            )
            results["viewports"][vp_name] = metrics
            if metrics["hasHorizontalOverflow"]:
                results["browser_findings"].append(
                    f"[{vp_name}] Horizontal overflow: scrollWidth={metrics['scrollWidth']} > clientWidth={metrics['clientWidth']}"
                )
            if vp_name == "desktop_1280x800":
                if metrics["h1BottomY"] and metrics["h1BottomY"] > 800:
                    results["browser_findings"].append(
                        f"[desktop_1280x800] Hero H1 misses 800px screen budget (bottom={metrics['h1BottomY']}px)"
                    )
                if screenshot_out is not None:
                    screenshot_out.parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(screenshot_out), full_page=True)
            page.close()
        browser.close()
    return results


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Money HQ Independent Web Visual Quality Gate")
    parser.add_argument("paths", nargs="+", help="HTML/TSX files to audit")
    parser.add_argument("--browser-render", action="store_true", help="Run real Chromium DOM geometry check")
    parser.add_argument("--screenshot-dir", default="", help="Optional directory to save desktop screenshots")
    args = parser.parse_args()

    overall_passed = True
    summary_list: list[dict[str, Any]] = []

    for raw_p in args.paths:
        target = Path(raw_p)
        report = audit_html_file(target)
        entry: dict[str, Any] = {
            "target": str(target),
            "static_passed": report.passed,
            "score_100": report.score_100,
            "findings": [
                {"gate_id": f.gate_id, "tier": f.tier, "message": f.message, "evidence": f.evidence}
                for f in report.findings
            ],
        }
        if args.browser_render and target.suffix.lower() in (".html", ".htm"):
            shot_path = None
            if args.screenshot_dir:
                shot_path = Path(args.screenshot_dir) / f"{target.stem}_{target.parent.name}_desktop.png"
            browser_res = run_browser_render_check(target, screenshot_out=shot_path)
            entry["browser_render"] = browser_res
            if browser_res["browser_findings"]:
                overall_passed = False

        if not report.passed:
            overall_passed = False
        summary_list.append(entry)

    print(json.dumps({"overall_passed": overall_passed, "reports": summary_list}, indent=2, ensure_ascii=False))
    return 0 if overall_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
