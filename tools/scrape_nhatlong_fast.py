"""Fast concurrent scraper for substantive posts from nhatlongtc (?embed=1).
Focuses on substantive knowledge posts (text length >= 120 chars).
"""

import concurrent.futures
import json
import logging
import re
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("nhatlong_scraper")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
}


def fetch_post(post_id: int) -> dict | None:
    url = f"https://t.me/nhatlongtc/{post_id}?embed=1"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            if "tgme_widget_message_text" not in html:
                return None
            soup = BeautifulSoup(html, "html.parser")
            txt_elem = soup.find("div", class_="tgme_widget_message_text")
            if not txt_elem:
                return None
            text = txt_elem.get_text("\n", strip=True)
            if len(text) < 100:  # skip short chat replies
                return None
            time_elem = soup.find("time")
            dt_str = time_elem.get("datetime", "") if time_elem else ""
            author_elem = soup.find("div", class_="tgme_widget_message_author")
            author = author_elem.get_text(strip=True) if author_elem else ""

            return {
                "id": post_id,
                "author": author,
                "datetime": dt_str,
                "link": f"https://t.me/nhatlongtc/{post_id}",
                "text": text,
            }
    except Exception:
        return None


def scrape_range(start_id: int, end_id: int, step: int = 1, max_workers: int = 15) -> list[dict]:
    ids = list(range(start_id, end_id, step))
    logger.info(f"Probing {len(ids)} posts between {start_id} and {end_id} with {max_workers} threads...")
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(fetch_post, pid): pid for pid in ids}
        for future in concurrent.futures.as_completed(future_to_id):
            res = future.result()
            if res:
                results.append(res)

    results.sort(key=lambda x: x["id"])
    logger.info(f"Collected {len(results)} substantive posts from range {start_id}-{end_id}")
    return results


if __name__ == "__main__":
    # We sample across the full history of nhatlongtc (from id 2 to 16500)
    # We test high-density ranges and step-sampled historical ranges
    all_posts = []

    # Dense sampling in early foundational posts (id 2 to 1000)
    p1 = scrape_range(2, 600, step=1, max_workers=20)
    all_posts.extend(p1)

    # Sample across subsequent periods
    p2 = scrape_range(600, 3000, step=3, max_workers=20)
    all_posts.extend(p2)

    p3 = scrape_range(3000, 8000, step=5, max_workers=20)
    all_posts.extend(p3)

    p4 = scrape_range(8000, 16500, step=8, max_workers=20)
    all_posts.extend(p4)

    out_file = Path("C:/Users/ACER/Documents/Codex/revenue-copilot-international-phase0/data/scraped_telegram/nhatlongtc.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(all_posts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Total substantive posts saved for nhatlongtc: {len(all_posts)}")
