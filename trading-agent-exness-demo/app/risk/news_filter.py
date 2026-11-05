"""NewsBlackoutFilter: P0 Safety gatekeeper enforcing news embargo windows.

Protects accounts from catastrophic slippage, spread widening, and prop firm rule violations
during High-Impact economic news releases (CPI, Non-Farm Payrolls, FOMC, Rate Decisions).
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence

import requests

from app.config import NewsFilterConfig

logger = logging.getLogger("trading_agent.risk.news_filter")

FF_CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"


@dataclass(frozen=True)
class NewsEvent:
    title: str
    country: str
    date_utc: datetime
    impact: str
    forecast: str = ""
    previous: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "country": self.country,
            "date_utc": self.date_utc.isoformat(),
            "impact": self.impact,
            "forecast": self.forecast,
            "previous": self.previous,
        }

    @classmethod
    def from_dict(cls, data: dict) -> NewsEvent:
        return cls(
            title=data["title"],
            country=data["country"],
            date_utc=datetime.fromisoformat(data["date_utc"]),
            impact=data["impact"],
            forecast=data.get("forecast", ""),
            previous=data.get("previous", ""),
        )


class NewsBlackoutFilter:
    """Evaluates whether trade entries are forbidden due to high-impact economic news."""

    # Default mapping for major currency & commodity tickers
    SYMBOL_CURRENCY_MAP: dict[str, list[str]] = {
        "EURUSD": ["EUR", "USD"],
        "GBPUSD": ["GBP", "USD"],
        "USDJPY": ["USD", "JPY"],
        "AUDUSD": ["AUD", "USD"],
        "USDCAD": ["USD", "CAD"],
        "USDCHF": ["USD", "CHF"],
        "NZDUSD": ["NZD", "USD"],
        "XAUUSD": ["USD"],
        "XAGUSD": ["USD"],
    }

    def __init__(
        self,
        config: NewsFilterConfig | None = None,
        cache_file: Path | None = None,
        auto_fetch: bool = True,
    ) -> None:
        self.config = config or NewsFilterConfig()
        self._require_fresh_calendar = auto_fetch
        self.cache_file = cache_file or Path("data/economic_calendar_cache.json")
        self._events: list[NewsEvent] = []
        self._last_fetch_utc: datetime | None = None
        self._last_fetch_attempt_utc: datetime | None = None

        if self.cache_file.exists():
            self._load_cache()

        if auto_fetch and self.config.enabled:
            # Refresh if cache is older than 4 hours or empty
            now = datetime.now(timezone.utc)
            if not self._events or self._last_fetch_utc is None or (now - self._last_fetch_utc) > timedelta(hours=4):
                self.fetch_calendar()

    def get_currencies_for_symbol(self, symbol: str) -> list[str]:
        clean_sym = symbol.upper().replace(".M", "").replace(".S", "").replace("#", "")
        if clean_sym in self.SYMBOL_CURRENCY_MAP:
            return self.SYMBOL_CURRENCY_MAP[clean_sym]
        # Auto-extract 3-letter currency codes for FX pairs (e.g. EURGBP -> EUR, GBP)
        if len(clean_sym) == 6 and clean_sym.isalpha():
            return [clean_sym[:3], clean_sym[3:]]
        return ["USD"]

    def _load_cache(self) -> None:
        try:
            data = json.loads(self.cache_file.read_text(encoding="utf-8"))
            self._events = [NewsEvent.from_dict(item) for item in data.get("events", [])]
            if "last_fetch_utc" in data:
                self._last_fetch_utc = datetime.fromisoformat(data["last_fetch_utc"])
            logger.info(f"Loaded {len(self._events)} economic events from cache {self.cache_file}")
        except Exception as e:
            logger.warning(f"Could not load economic calendar cache: {e}")

    def _save_cache(self) -> None:
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "last_fetch_utc": datetime.now(timezone.utc).isoformat(),
                "events": [e.to_dict() for e in self._events],
            }
            tmp = self.cache_file.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            tmp.replace(self.cache_file)
        except Exception as e:
            logger.warning(f"Could not save economic calendar cache: {e}")

    def fetch_calendar(self) -> bool:
        """Fetch weekly calendar from public API. Fails safely to cache if network fails."""
        self._last_fetch_attempt_utc = datetime.now(timezone.utc)
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AutonomousTradingAgent/1.0"}
            resp = requests.get(FF_CALENDAR_URL, headers=headers, timeout=5.0)
            if resp.status_code != 200:
                logger.warning(f"ForexFactory calendar responded with HTTP {resp.status_code}")
                return False

            raw_items = resp.json()
            parsed_events: list[NewsEvent] = []
            for item in raw_items:
                try:
                    title = str(item.get("title", "")).strip()
                    country = str(item.get("country", "")).strip().upper()
                    impact = str(item.get("impact", "")).strip().capitalize()
                    date_str = str(item.get("date", "")).strip()

                    if not (title and country and date_str):
                        continue

                    # Parse ISO timestamp with timezone offset
                    dt = datetime.fromisoformat(date_str)
                    dt_utc = dt.astimezone(timezone.utc)

                    parsed_events.append(
                        NewsEvent(
                            title=title,
                            country=country,
                            date_utc=dt_utc,
                            impact=impact,
                            forecast=str(item.get("forecast", "")),
                            previous=str(item.get("previous", "")),
                        )
                    )
                except Exception:
                    continue

            if parsed_events:
                self._events = parsed_events
                self._last_fetch_utc = datetime.now(timezone.utc)
                self._save_cache()
                logger.info(f"Successfully fetched and cached {len(self._events)} calendar events.")
                return True
        except Exception as e:
            logger.warning(f"Failed to fetch economic calendar from online feed: {e}. Using cached data.")
        return False

    def inject_events(self, events: Sequence[NewsEvent]) -> None:
        """For testing or manual override."""
        self._events = list(events)

    def is_blackout(
        self, symbol: str, target_time: datetime | None = None
    ) -> tuple[bool, str]:
        """Check if trading is blacked out for the symbol at the target time.

        Returns (is_blocked: bool, reason: str).
        """
        if not self.config.enabled:
            return False, "News blackout filter disabled"

        eval_time = target_time or datetime.now(timezone.utc)
        if eval_time.tzinfo is None:
            eval_time = eval_time.replace(tzinfo=timezone.utc)

        # The live daemon must not treat an empty or old feed as proof that no
        # high-impact event is scheduled. Offline simulations opt out of this
        # gate explicitly and must disclose that historical news is unverified.
        stale_calendar = (
            self._last_fetch_utc is None
            or not self._events
            or self._last_fetch_utc.tzinfo is None
            or datetime.now(timezone.utc) - self._last_fetch_utc > timedelta(hours=4)
            or self._last_fetch_utc - datetime.now(timezone.utc) > timedelta(minutes=1)
        )
        if self._require_fresh_calendar and stale_calendar:
            now = datetime.now(timezone.utc)
            if self._last_fetch_attempt_utc is None or now - self._last_fetch_attempt_utc > timedelta(minutes=15):
                self.fetch_calendar()
                stale_calendar = self._last_fetch_utc is None or not self._events or now - self._last_fetch_utc > timedelta(hours=4)
        if self._require_fresh_calendar and stale_calendar:
            return True, "Economic calendar unavailable or older than four hours"

        currencies = set(self.get_currencies_for_symbol(symbol))
        before_delta = timedelta(minutes=self.config.blackout_minutes_before)
        after_delta = timedelta(minutes=self.config.blackout_minutes_after)

        for event in self._events:
            # Check impact level
            if self.config.min_impact == "HIGH" and event.impact.upper() != "HIGH":
                continue

            # Check if event affects any of the symbol's currencies
            if event.country.upper() not in currencies:
                continue

            # Check if current time falls within [event - before, event + after]
            blackout_start = event.date_utc - before_delta
            blackout_end = event.date_utc + after_delta

            if blackout_start <= eval_time <= blackout_end:
                diff_min = int((event.date_utc - eval_time).total_seconds() / 60)
                timing = f"in {diff_min}m" if diff_min >= 0 else f"{abs(diff_min)}m ago"
                reason = (
                    f"NEWS BLACKOUT: High-Impact [{event.country}] '{event.title}' scheduled "
                    f"at {event.date_utc.strftime('%H:%M')} UTC ({timing}). "
                    f"Window [{self.config.blackout_minutes_before}m before / {self.config.blackout_minutes_after}m after]."
                )
                logger.warning(f"Blocked trade on {symbol}: {reason}")
                return True, reason

        return False, "Clear: No conflicting high-impact news within blackout window"

    def get_upcoming_blackouts(
        self, symbol: str, hours_ahead: int = 12, start_time: datetime | None = None
    ) -> list[tuple[NewsEvent, datetime, datetime]]:
        """Return list of upcoming blackout windows (event, window_start, window_end) within hours_ahead."""
        now = start_time or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        horizon = now + timedelta(hours=hours_ahead)
        currencies = set(self.get_currencies_for_symbol(symbol))
        before_delta = timedelta(minutes=self.config.blackout_minutes_before)
        after_delta = timedelta(minutes=self.config.blackout_minutes_after)

        windows = []
        for event in self._events:
            if event.impact.upper() != "HIGH" or event.country.upper() not in currencies:
                continue
            window_start = event.date_utc - before_delta
            window_end = event.date_utc + after_delta
            if window_end >= now and window_start <= horizon:
                windows.append((event, window_start, window_end))
        return windows
