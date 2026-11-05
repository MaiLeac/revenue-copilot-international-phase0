from datetime import datetime, timezone
from tools.public_demand_scout import classify, normalize_hits, run_once


def test_source_and_gap_remain_unverified():
    hit = {"signal_id": "hn:123", "source": "hn", "source_url": "https://news.ycombinator.com/item?id=123", "posted_at": "2026-11-05", "title": "Need help with manual spreadsheet", "excerpt": "Willing to pay. Tried a tool but it fails.", "topic": "operations"}
    row = classify(hit, "2026-11-05T00:00:00Z")
    assert row["opportunity_status"] == "buyer_intent_to_verify"
    assert row["alternative_failure_claimed"]
    assert row["gap_verification"].startswith("needed")


def test_prs_are_excluded():
    rows = normalize_hits("github", {"items": [{"id": 1, "html_url": "https://github.com/a/b/issues/1", "title": "Help", "body": "<b>Manual</b> work"}, {"id": 2, "html_url": "https://github.com/a/b/pull/2", "title": "PR", "pull_request": {}}]}, "operations")
    assert len(rows) == 1
    assert rows[0]["excerpt"] == "Manual work"


def test_github_feature_request_is_not_a_buyer_without_pay_language():
    hit = {"signal_id": "github:1", "source": "github", "source_url": "https://github.com/a/b/issues/1", "posted_at": "2026-11-05", "title": "Need help with manual CSV import", "excerpt": "We need a tool for this", "topic": "operations"}
    row = classify(hit, "2026-11-05T00:00:00Z")
    assert row["opportunity_status"] == "context_only"


def test_job_seeker_and_email_are_not_sold_as_buyer_signal():
    hit = {"signal_id": "hn:456", "source": "hn", "source_url": "https://news.ycombinator.com/item?id=456", "posted_at": "2026-11-05", "title": "Ask HN: Who wants to be hired?", "excerpt": "I need freelance work. Email me at person@example.com", "topic": "open"}
    row = classify(hit, "2026-11-05T00:00:00Z")
    assert row["opportunity_status"] == "context_only"
    assert "person@example.com" not in normalize_hits("hn", {"hits": [{"objectID": "456", "story_title": "Ask HN", "comment_text": "Email person@example.com"}]}, "open")[0]["excerpt"]


def test_dedup_and_bounded_queries(tmp_path):
    now = datetime(2026, 11, 5, tzinfo=timezone.utc)
    calls = []
    def fake_fetch(url):
        calls.append(url)
        return {"hits": [{"objectID": "123", "comment_text": "I need help with our spreadsheet. CSV import is broken. Looking for a tool; would pay for it.", "story_title": "Ask HN"}]} if "hn.algolia.com" in url else {"items": []}
    assert run_once(tmp_path, fake_fetch, now)["new_pain_signals"] == 1
    assert run_once(tmp_path, fake_fetch, now)["new_pain_signals"] == 0
    assert len(calls) == 12


def test_all_sources_fail_preserves_state(tmp_path):
    state = tmp_path / "state.json"
    state.write_text('{"seen_ids":["hn:old"]}', encoding="utf-8")
    def fail(_url):
        raise TimeoutError()
    assert run_once(tmp_path, fail, datetime(2026, 11, 5, tzinfo=timezone.utc))["successful_queries"] == 0
    assert state.read_text(encoding="utf-8") == '{"seen_ids":["hn:old"]}'
