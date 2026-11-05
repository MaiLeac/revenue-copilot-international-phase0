"""Read-only public demand scout. No LLM, credentials, outreach, or paid API."""
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "operations" / "public_demand_scout"
SEARCHES = (
    ("hn", "our spreadsheet", "operations"),
    ("hn", "CSV import", "catalogue"),
    ("hn", "looking for a tool", "open"),
    ("hn", "would pay for", "open"),
    ("github", "CSV import error", "catalogue"),
    ("github", "manual data entry", "operations"),
)
ALTERNATIVES = {
    "catalogue": [
        {"name": "Shopify CSV help", "url": "https://help.shopify.com/en/manual/products/import-export/common-import-issues"},
        {"name": "CSVwise", "url": "https://apps.shopify.com/csvwise"},
        {"name": "Matrixify", "url": "https://apps.shopify.com/excel-export-import"},
    ],
    "operations": [], "open": [],
}
PAIN = re.compile(r"\b(struggl\w*|frustrat\w*|manual(?:ly)?|painful|tedious|broken|can't|cannot|doesn.t work|need help|looking for|wish there|time.consuming|import error|duplicate\s+sku)\b", re.I)
FIRST_PERSON_PROBLEM = re.compile(r"\b(?:i|we|our|my)\b.{0,100}\b(?:need|can't|cannot|struggl\w*|spend|wish|looking for|manual|painful|problem|fails?)\b", re.I | re.S)
REQUEST = re.compile(r"\b(?:need|looking for|anyone know|how do you|find a way)\b.{0,80}\b(?:tool|service|automation|csv|spreadsheet|data entry)\b", re.I | re.S)
JOB_SEEKER = re.compile(r"who wants to be hired|resume/cv|looking for (?:part.time |full.time |freelance )?(?:contract|work|job)", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PAY = re.compile(r"\b(willing to pay|happy to pay|budget(?:ed)?|hire|paid help|pay someone|looking for a contractor|looking to buy)\b|\$\s?\d{2,}", re.I)
FAILED_TOOL = re.compile(r"\b(tried|already use|using|alternatives? to|current tool|existing tool)\b.{0,100}\b(but|doesn.t|cannot|can't|fails?|missing|expensive|too costly)\b", re.I | re.S)


def clean_text(value: object) -> str:
    plain = re.sub(r"<[^>]+>", " ", html.unescape(str(value or "")))
    return re.sub(r"\s+", " ", EMAIL.sub("[redacted-email]", plain)).strip()[:800]


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "MoneyHQ-PublicDemandScout/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=12) as response:
        body = response.read(1_000_001)
    if len(body) > 1_000_000:
        raise ValueError("response_too_large")
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ValueError("unexpected_response_shape")
    return data


def query_url(source: str, query: str, since: datetime) -> str:
    if source == "hn":
        return "https://hn.algolia.com/api/v1/search_by_date?" + urlencode({"tags": "comment", "query": query, "numericFilters": f"created_at_i>{int(since.timestamp())}", "hitsPerPage": 15})
    if source == "github":
        return "https://api.github.com/search/issues?" + urlencode({"q": f'is:issue is:open created:>={since.date().isoformat()} "{query}"', "sort": "created", "order": "desc", "per_page": 15})
    raise ValueError(f"unsupported_source:{source}")


def normalize_hits(source: str, payload: dict, topic: str) -> list[dict]:
    rows = payload.get("hits", []) if source == "hn" else payload.get("items", [])
    if not isinstance(rows, list):
        raise ValueError("unexpected_hits_shape")
    result = []
    for row in rows[:15]:
        if not isinstance(row, dict):
            continue
        if source == "hn":
            item_id = str(row.get("objectID") or "")
            url = f"https://news.ycombinator.com/item?id={item_id}" if item_id.isdigit() else ""
            title, body = row.get("story_title") or "Hacker News discussion", row.get("comment_text")
        else:
            if "pull_request" in row:
                continue
            item_id = str(row.get("id") or "")
            url = str(row.get("html_url") or "")
            title, body = row.get("title") or "GitHub issue", row.get("body")
        if item_id and url:
            result.append({"signal_id": f"{source}:{item_id}", "source": source, "source_url": url, "posted_at": str(row.get("created_at") or ""), "title": clean_text(title)[:160], "excerpt": clean_text(body), "topic": topic})
    return result


def classify(hit: dict, checked_at: str) -> dict:
    text = f"{hit['title']} {hit['excerpt']}"
    has_pain = bool(PAIN.search(text)) and bool(FIRST_PERSON_PROBLEM.search(text) or REQUEST.search(text)) and not bool(JOB_SEEKER.search(text))
    has_pay = bool(PAY.search(text))
    if hit["topic"] == "open" and not has_pay:
        has_pain = False  # Broad general discussion is not yet a commercial lead.
    status = "buyer_intent_to_verify" if has_pain and has_pay else "pain_only" if has_pain else "context_only"
    return {**hit, "checked_at": checked_at, "evidence_level": "L1_candidate" if has_pain else "L0_context", "buyer_intent": "explicit_language" if has_pay else "not_shown", "alternative_failure_claimed": bool(FAILED_TOOL.search(text)), "known_alternatives": ALTERNATIVES[hit["topic"]], "gap_verification": "needed_even_if_post_claims_failure", "opportunity_status": status, "next_step": "Verify original context, current need, payer, competing solutions, why they fail, and allowed response channel."}


def run_once(output_dir: Path = OUTPUT, fetcher=fetch_json, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    checked_at = now.isoformat()
    state_file = output_dir / "state.json"
    try:
        seen = set(json.loads(state_file.read_text(encoding="utf-8")).get("seen_ids", []))
    except (OSError, ValueError):
        seen = set()
    signals, errors, successes = [], [], 0
    for source, query, topic in SEARCHES:
        try:
            rows = normalize_hits(source, fetcher(query_url(source, query, now - timedelta(days=7))), topic)
            successes += 1
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            errors.append({"source": source, "query": query, "error_type": type(exc).__name__})
            continue
        for hit in rows:
            # Search APIs may match the parent story or text outside our bounded
            # excerpt. Require the actual captured post to contain the phrase.
            if query.casefold() not in f"{hit['title']} {hit['excerpt']}".casefold():
                continue
            if hit["signal_id"] in seen:
                continue
            seen.add(hit["signal_id"])
            hit["search_query"] = query
            record = classify(hit, checked_at)
            if record["opportunity_status"] != "context_only":
                signals.append(record)
    result = {"checked_at": checked_at, "source_queries": len(SEARCHES), "successful_queries": successes, "new_pain_signals": len(signals), "buyer_intent_to_verify": sum(s["opportunity_status"] == "buyer_intent_to_verify" for s in signals), "errors": errors, "cash_collected_vnd": None, "note": "Public discussion signals only; no customer, sale, or market gap validated."}
    if successes:
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "signals.jsonl").open("a", encoding="utf-8") as stream:
            for signal in signals:
                stream.write(json.dumps(signal, ensure_ascii=False) + "\n")
        (output_dir / "latest.json").write_text(json.dumps({"run": result, "new_signals": signals[:20]}, ensure_ascii=False, indent=2), encoding="utf-8")
        (output_dir / "state.json").write_text(json.dumps({"last_checked_at": checked_at, "seen_ids": sorted(seen)[-5000:]}, ensure_ascii=False), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded public discussion scout")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    result = run_once(parser.parse_args().output_dir)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["successful_queries"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
