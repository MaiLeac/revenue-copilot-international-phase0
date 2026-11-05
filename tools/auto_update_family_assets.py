"""Update public reference prices in the family Sheet; never infer private holdings.

Google Sheets access uses Application Default Credentials with the Sheets scope.
The user's quantities, Exness equity, cost basis and history are left to the
existing verified Sheet workflow. This script never substitutes a silver futures
quote for the Exness account equity and never invents debt or past snapshots.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.telegram_notify import send_telegram_alert

SHEET_ID = "1UPReETEtQJVYTEXHyzLbOOm5aNVJpjzEYr6aJKWIals"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
ICT = timezone(timedelta(hours=7))
log = logging.getLogger("family_assets_prices")


def get_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "MoneyHQ-AssetPrices/1.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        return json.load(response)


def fetch_knp() -> tuple[float, float, str]:
    """Accept only a row explicitly identifying KNP's 2024 silver bar."""
    from bs4 import BeautifulSoup

    req = urllib.request.Request("https://kimnganphuc.vn/gia-vang", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        soup = BeautifulSoup(response.read(), "html.parser")
    for row in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"], recursive=False)]
        if not cells or "2024" not in cells[0] or "bạc" not in cells[0].lower():
            continue
        if not any(part in cells[0].lower() for part in ("1kilo", "1 kilo", "1kg")):
            continue
        prices: list[float] = []
        for cell in cells[1:]:
            match = re.fullmatch(r"\s*(\d{2,3}(?:[.,]\d{3})+)\s*", cell)
            if match:
                prices.append(float(match.group(1).replace(".", "").replace(",", "")) * 1000)
        if len(prices) >= 2 and all(20_000_000 <= p <= 200_000_000 for p in prices[:2]):
            return prices[0], prices[1], "KNP bạc thỏi 2024"
    raise ValueError("Không xác minh được đúng dòng bạc KNP 2024 và đơn vị giá")


def fetch_sol() -> tuple[float, str]:
    data = get_json("https://api.coinbase.com/v2/prices/SOL-USD/spot")["data"]
    if data.get("base") != "SOL" or data.get("currency") != "USD":
        raise ValueError("SOL/USD sai mã")
    price = float(data["amount"])
    if not 1 <= price <= 2000:
        raise ValueError("SOL/USD ngoài khoảng kiểm tra")
    return price, "Coinbase SOL/USD"


def fetch_psol() -> tuple[float, str, str]:
    data = get_json("https://api.coingecko.com/api/v3/simple/price?ids=phantom-staked-sol&vs_currencies=usd&include_last_updated_at=true")
    item = data["phantom-staked-sol"]
    price = float(item["usd"])
    source_at = datetime.fromtimestamp(int(item["last_updated_at"]), timezone.utc)
    if not 1 <= price <= 2000 or datetime.now(timezone.utc) - source_at > timedelta(days=2):
        raise ValueError("PSOL thiếu giá mới đáng tin")
    return price, source_at.astimezone(ICT).strftime("%d/%m/%Y %H:%M"), "CoinGecko phantom-staked-sol"


def fetch_usd_vnd() -> tuple[float, str, str]:
    data = get_json("https://open.er-api.com/v6/latest/USD")
    if data.get("result") != "success" or data.get("base_code") != "USD":
        raise ValueError("USD/VND sai nguồn hoặc mã")
    rate = float(data["rates"]["VND"])
    if not 20_000 <= rate <= 35_000:
        raise ValueError("USD/VND ngoài khoảng kiểm tra")
    source_at = datetime.strptime(data["time_last_update_utc"], "%a, %d %b %Y %H:%M:%S %z")
    return rate, source_at.astimezone(ICT).strftime("%d/%m/%Y %H:%M"), "open.er-api.com"


def sheets_service():
    import google.auth
    from googleapiclient.discovery import build

    credentials, _ = google.auth.default(scopes=[SCOPE])
    return build("sheets", "v4", credentials=credentials, cache_discovery=False).spreadsheets()


def update_prices(service, quotes: dict[str, tuple], errors: dict[str, str]) -> int:
    values = service.values()
    current = values.get(spreadsheetId=SHEET_ID, range="'Gia tai san'!A4:H8").execute().get("values", [])
    for row, code in ((5, "BAC_KNP_2024"), (6, "SOL_USD"), (7, "USD_VND"), (8, "PSOL_USD")):
        actual = current[row - 4][0] if len(current) > row - 4 and current[row - 4] else ""
        if actual != code:
            raise ValueError(f"Sheet đổi bố cục tại A{row}: chờ kiểm tra, không ghi")

    now = datetime.now(ICT).strftime("%d/%m/%Y %H:%M")
    updates = []

    def put(cell: str, value: Any) -> None:
        updates.append({"range": f"'Gia tai san'!{cell}", "values": [[value]]})

    if "KNP" in quotes:
        buy, sell, source = quotes["KNP"]
        for cell, value in (("C5", buy), ("D5", sell), ("E5", source), ("G5", now), ("H5", "Đã kiểm tra nguồn")):
            put(cell, value)
    if "SOL" in quotes:
        price, source = quotes["SOL"]
        for cell, value in (("C6", price), ("E6", source), ("G6", now), ("H6", "Đã kiểm tra nguồn")):
            put(cell, value)
    if "FX" in quotes:
        rate, source_at, source = quotes["FX"]
        for cell, value in (("C7", rate), ("E7", source), ("F7", source_at), ("G7", now), ("H7", "Đã kiểm tra nguồn")):
            put(cell, value)
    if "PSOL" in quotes:
        price, source_at, source = quotes["PSOL"]
        for cell, value in (("C8", price), ("E8", source), ("F8", source_at), ("G8", now), ("H8", "Đã kiểm tra nguồn")):
            put(cell, value)
    for code, row in (("KNP", 5), ("SOL", 6), ("FX", 7), ("PSOL", 8)):
        if code in errors:
            put(f"H{row}", f"Lỗi nguồn: {errors[code][:65]}")
    if not updates:
        raise ValueError("Không có giá hoặc trạng thái nào để ghi")
    values.batchUpdate(spreadsheetId=SHEET_ID, body={"valueInputOption": "USER_ENTERED", "data": updates}).execute()
    check = values.batchGet(spreadsheetId=SHEET_ID, ranges=[f"'Gia tai san'!H{row}" for row in (5, 6, 7, 8)]).execute()["valueRanges"]
    if len(check) != 4 or any(not item.get("values") for item in check):
        raise RuntimeError("Không đọc lại đủ trạng thái nguồn sau khi ghi Sheet")
    return len(quotes)


def collect_quotes() -> tuple[dict[str, tuple], dict[str, str]]:
    quotes, errors = {}, {}
    for code, fetch in (("KNP", fetch_knp), ("SOL", fetch_sol), ("FX", fetch_usd_vnd), ("PSOL", fetch_psol)):
        try:
            quotes[code] = fetch()
        except Exception as exc:
            errors[code] = str(exc)
            log.warning("%s source failed: %s", code, exc)
    return quotes, errors


def prices_message(quotes: dict[str, tuple], errors: dict[str, str], stamp: str) -> str:
    """Short, truthful bulletin when Sheets authorization is unavailable."""
    parts = []
    for code, label, unit in (("SOL", "SOL", "$"), ("PSOL", "PSOL", "$"), ("FX", "USD/VND", "")):
        if code in quotes:
            parts.append(f"{label} {unit}{quotes[code][0]:,.2f}")
    if not parts:
        return f"⚠️ Giá tài sản {stamp}: không lấy được nguồn; Sheet chưa ghi."
    note = "; bạc KNP chưa xác minh ngày" if "KNP" in quotes else "; bạc KNP lỗi nguồn"
    if errors and any(code != "KNP" for code in errors):
        note += "; lỗi " + ",".join(code for code in errors if code != "KNP")
    return f"📊 Giá {stamp}: " + ", ".join(parts) + note + ". Sheet chưa ghi."


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Fetch public prices only; no Sheet or Telegram")
    parser.add_argument("--check-auth", action="store_true", help="Check Google Sheets credentials only")
    parser.add_argument("--telegram-prices-only", action="store_true", help="Send public prices; explicitly state Sheet was not updated")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if args.check_auth:
        sheets_service()
        print("Google Sheets credentials available")
        return 0
    if args.dry_run:
        quotes, errors = collect_quotes()
        print(json.dumps({"quotes": quotes, "errors": errors}, ensure_ascii=False))
        return 0 if quotes else 1
    stamp = datetime.now(ICT).strftime("%d/%m %H:%M")
    if args.telegram_prices_only:
        quotes, errors = collect_quotes()
        message = prices_message(quotes, errors, stamp)
        result = send_telegram_alert(message)
        if not result.get("ok") or result.get("dry_run"):
            log.error("Telegram delivery not verified")
            return 1
        print(message)
        return 0 if quotes else 1
    try:
        service = sheets_service()
        quotes, errors = collect_quotes()
        count = update_prices(service, quotes, errors)
        message = f"📊 Giá tài sản {stamp}: Sheet đã ghi {count}/4 nguồn."
        if errors:
            message += " Lỗi: " + ", ".join(errors)
    except Exception as exc:
        log.error("Sheet update failed: %s", exc.__class__.__name__)
        message = f"⚠️ Giá tài sản {stamp}: chưa cập nhật Sheet ({exc.__class__.__name__})."
        result = send_telegram_alert(message)
        if not result.get("ok") or result.get("dry_run"):
            log.error("Telegram delivery not verified")
        return 1
    result = send_telegram_alert(message)
    if not result.get("ok") or result.get("dry_run"):
        log.error("Telegram delivery not verified")
        return 1
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
