import json

from tools import wink_private_model as model


def test_daily_snapshot_records_real_state_without_backfill(tmp_path, monkeypatch):
    monkeypatch.setattr(model, "DB_FILE", tmp_path / "wink.db")
    monkeypatch.setattr(model, "HOLDINGS_FILE", tmp_path / "holdings.json")
    monkeypatch.setattr(model, "PRICES_FILE", tmp_path / "prices.json")
    model.HOLDINGS_FILE.write_text(json.dumps({"assets": [{"id": "mai_silver", "owner": "Mai", "name": "Bạc",
        "quantity": 9, "unit": "kg", "price_code": "KNP", "cost_vnd": 400_000_000}]}), encoding="utf-8")
    model.PRICES_FILE.write_text(json.dumps({"quotes": {"KNP": {"value": 40_000_000}}}), encoding="utf-8")

    assert model.load_history() == []
    first = model.record_snapshot()
    assert first["assets"][0]["value_vnd"] == 360_000_000
    assert first["assets"][0]["quantity"] == 9

    model.update_asset("mai_silver", 10, 400_000_000, "2026-11-06")
    history = model.load_history()
    assert len(history) == 1  # latest observed state for the day, no made-up earlier dates
    assert history[0]["assets"][0]["quantity"] == 10
    assert history[0]["assets"][0]["value_vnd"] == 400_000_000
