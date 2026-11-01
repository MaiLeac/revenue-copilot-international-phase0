"""TikTok Knowledge Mining System — Collector Engine.

Collects video list, metadata, and auto-captions/subtitles from a TikTok creator profile.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

import yt_dlp

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("tiktok_collector")


def extract_tiktok_channel_videos(
    channel_url_or_handle: str,
    output_dir: Path,
    max_videos: int = 100,
    download_audio_if_no_sub: bool = False,
) -> list[dict[str, Any]]:
    """Scan channel profile, extract video URLs, metadata, and subtitles."""
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "videos_manifest.json"

    # Normalize url
    clean_handle = channel_url_or_handle.strip().lstrip("@")
    if not clean_handle.startswith("http"):
        profile_url = f"https://www.tiktok.com/@{clean_handle}"
    else:
        profile_url = clean_handle

    logger.info(f"Connecting to TikTok profile: {profile_url} (limit={max_videos})...")

    ydl_opts: dict[str, Any] = {
        "extract_flat": True,
        "playlistend": max_videos,
        "quiet": False,
        "no_warnings": True,
        "ignoreerrors": True,
    }

    videos: list[dict[str, Any]] = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(profile_url, download=False)
            if not info:
                logger.error("Could not retrieve channel info.")
                return []
            entries = info.get("entries") or []
            logger.info(f"Discovered {len(entries)} videos on channel.")
            for entry in entries:
                if not entry:
                    continue
                v_data = {
                    "id": entry.get("id"),
                    "url": entry.get("url") or f"https://www.tiktok.com/@{clean_handle}/video/{entry.get('id')}",
                    "title": entry.get("title", ""),
                    "description": entry.get("description", ""),
                    "duration": entry.get("duration"),
                    "uploader": entry.get("uploader", clean_handle),
                    "timestamp": entry.get("timestamp"),
                }
                videos.append(v_data)
        except Exception as e:
            logger.error(f"Error during video list extraction: {e}")

    manifest_path.write_text(json.dumps(videos, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Saved metadata for {len(videos)} videos to {manifest_path}")
    return videos


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python collector.py <tiktok_username_or_url> [output_directory]")
        sys.exit(1)

    target = sys.argv[1]
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "data"
    extract_tiktok_channel_videos(target, out_dir)
