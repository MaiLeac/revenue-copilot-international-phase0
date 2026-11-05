from __future__ import annotations

from tools.auto_update_family_assets import prices_message, update_prices


class FakeValues:
    def __init__(self, rows):
        self.rows = rows
        self.written = None

    def get(self, **kwargs):
        return self

    def batchUpdate(self, **kwargs):
        self.written = kwargs["body"]["data"]
        return self

    def batchGet(self, **kwargs):
        self.readback = True
        return self

    def execute(self):
        if self.written is None:
            return {"values": self.rows}
        if getattr(self, "readback", False):
            return {"valueRanges": [{"values": [["OK"]]} for _ in range(4)]}
        return {}


class FakeService:
    def __init__(self, rows):
        self.api = FakeValues(rows)

    def values(self):
        return self.api


def test_rejects_changed_sheet_layout_before_writing():
    sheet = FakeService([["header"], ["wrong"], ["SOL_USD"], ["USD_VND"], ["PSOL_USD"]])
    try:
        update_prices(sheet, {"SOL": (90.0, "Coinbase")}, {})
    except ValueError as exc:
        assert "A5" in str(exc)
    else:
        raise AssertionError("Changed portfolio layout must block all writes")
    assert sheet.api.written is None


def test_writes_reference_prices_only_and_no_private_portfolio_fields():
    sheet = FakeService([["header"], ["BAC_KNP_2024"], ["SOL_USD"], ["USD_VND"], ["PSOL_USD"]])
    assert update_prices(sheet, {"SOL": (90.0, "Coinbase")}, {"KNP": "stale"}) == 1
    ranges = [entry["range"] for entry in sheet.api.written]
    assert all("Gia tai san" in range_ for range_ in ranges)
    assert not any("Danh muc" in range_ or "Lich su ngay" in range_ for range_ in ranges)
    assert "'Gia tai san'!H5" in ranges
    assert "'Gia tai san'!C6" in ranges


def test_telegram_price_bulletin_never_claims_sheet_was_updated():
    text = prices_message({"SOL": (90.0, "Coinbase")}, {"KNP": "unknown"}, "06/11 20:00")
    assert "SOL $90.00" in text
    assert "Sheet chưa ghi" in text
    assert len(text) < 160
