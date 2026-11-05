from __future__ import annotations

from tools.auto_update_family_assets import format_telegram_report


def test_report_names_each_owner_and_discloses_stale_exness():
    state = {
        "assets": [
            {"owner": "Mai", "name": "Bạc KNP", "price_code": "KNP", "quantity": 9,
             "cost_comparison_vnd": 409_400_000, "value_vnd": 356_850_000,
             "estimated_change_vnd": -52_550_000},
            {"owner": "Mai", "name": "PSOL", "price_code": "PSOL", "quantity": 19.65951,
             "cost_comparison_vnd": 44_300_000, "value_vnd": 50_200_000,
             "estimated_change_vnd": 5_900_000},
            {"owner": "Mai", "name": "Exness", "price_code": "FX", "quantity": 1287.82,
             "cost_usd": 3000.97, "change_usd": -1713.15,
             "estimated_change_vnd": -44_028_000, "quantity_asof": "2026-10-07"},
            {"owner": "Mẹ", "name": "Bạc", "price_code": "KNP", "quantity": 6,
             "cost_comparison_vnd": 327_500_000, "value_vnd": 237_900_000,
             "estimated_change_vnd": -89_600_000},
            {"owner": "Việt", "name": "Bạc", "price_code": "KNP", "quantity": 2,
             "cost_comparison_vnd": 174_900_000, "value_vnd": 79_300_000,
             "estimated_change_vnd": -95_600_000},
        ],
        "owner_totals_vnd": {"Mai": 440_150_000, "Mẹ": 237_900_000, "Việt": 79_300_000},
        "price_errors": {},
    }
    text = format_telegram_report(state, "06/11 20:00", 4)
    for token in ("MAI", "MẸ", "BẦU (VIỆT)", "Bạc KNP 9 kg", "PSOL", "3 000.97 USD", "2026-10-07"):
        assert token in text
    assert "vốn 409.4tr → 356.9tr (-52.5tr)" in text
    assert "không phải lãi đã chốt" in text
    assert "Sheet" not in text
