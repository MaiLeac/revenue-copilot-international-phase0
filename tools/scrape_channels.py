"""Scraper for public Telegram channels via t.me/s/ web interface.
Extracts posts, timestamps, views, text, and paginates through history.
"""

import json
import logging
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("telegram_scraper")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_messages(html: str, channel: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    messages = []

    # Each post is inside div.tgme_widget_message_wrap
    posts = soup.find_all("div", class_="tgme_widget_message")
    for post in posts:
        msg_id_raw = post.get("data-post", "")
        if not msg_id_raw:
            continue
        
        # Text content
        text_elem = post.find("div", class_="tgme_widget_message_text")
        text = text_elem.get_text("\n", strip=True) if text_elem else ""

        # Date / time
        time_elem = post.find("time", class_="time")
        dt_str = time_elem.get("datetime", "") if time_elem else ""

        # Views
        views_elem = post.find("span", class_="tgme_widget_message_views")
        views = views_elem.get_text(strip=True) if views_elem else ""

        # Link
        post_link = f"https://t.me/{msg_id_raw}"

        if text:  # only keep posts with substantive text
            messages.append({
                "channel": channel,
                "post_id": msg_id_raw,
                "datetime": dt_str,
                "views": views,
                "link": post_link,
                "text": text,
            })

    return messages


def scrape_channel(channel: str, max_pages: int = 15) -> list[dict]:
    logger.info(f"Starting scrape for channel: {channel} (max_pages={max_pages})")
    all_messages = []
    seen_ids = set()

    current_url = f"https://t.me/s/{channel}"
    page = 0

    while current_url and page < max_pages:
        page += 1
        logger.info(f"Fetching page {page}: {current_url}")
        try:
            html = fetch_url(current_url)
        except Exception as e:
            logger.error(f"Failed to fetch {current_url}: {e}")
            break

        msgs = parse_messages(html, channel)
        new_msgs = [m for m in msgs if m["post_id"] not in seen_ids]
        
        if not new_msgs:
            logger.info("No new messages found on this page. Stopping.")
            break

        for m in new_msgs:
            seen_ids.add(m["post_id"])
            all_messages.append(m)

        logger.info(f"Page {page}: found {len(new_msgs)} new messages (Total so far: {len(all_messages)})")

        # Find "before" link for older messages
        # Telegram s/ pages contain <link rel="prev" href="/s/channel?before=..."> or a.tme_widget_message_previous
        soup = BeautifulSoup(html, "html.parser")
        prev_link = soup.find("a", class_="tme_messages_more") or soup.find("a", dict(href=re.compile(r"before=")))
        if prev_link and prev_link.get("href"):
            href = prev_link.get("href")
            if href.startswith("/"):
                current_url = f"https://t.me{href}"
            elif href.startswith("http"):
                current_url = href
            else:
                current_url = f"https://t.me/s/{channel}/{href}"
            time.sleep(1.0)  # Politeness delay
        else:
            logger.info("No previous pagination link found.")
            break

    logger.info(f"Finished scraping {channel}: {len(all_messages)} messages collected.")
    return all_messages


if __name__ == "__main__":
    channels = ["khoahoctaichinh_Vuongtolinh", "nhatlongtc"]
    output_dir = Path("data/scraped_telegram")
    output_dir.mkdir(parents=True, exist_ok=True)

    for ch in channels:
        data = scrape_channel(ch, max_pages=20)
        out_file = output_dir / f"{ch}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(data)} messages for {ch} to {out_file}")
