"""TikTok Knowledge Mining System — Collector Engine.

Collects video list, metadata, and auto-captions/subtitles/audio from a TikTok creator profile.
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
    subtitles_dir = output_dir / "transcripts"
    audio_dir = output_dir / "audio"
    subtitles_dir.mkdir(parents=True, exist_ok=True)
    if download_audio_if_no_sub:
        audio_dir.mkdir(parents=True, exist_ok=True)

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
                    "has_subtitle": False,
                    "subtitle_file": None,
                }
                videos.append(v_data)
        except Exception as e:
            logger.error(f"Error during video list extraction: {e}")

    # Second pass: download captions or audio for each video
    logger.info(f"Checking subtitles & transcripts for {len(videos)} videos...")
    for idx, v in enumerate(videos, start=1):
        v_url = v["url"]
        v_id = v["id"]
        sub_opts: dict[str, Any] = {
            "skip_download": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["vi", "en"],
            "subtitlesformat": "vtt/json3/srt/best",
            "outtmpl": str(subtitles_dir / f"{v_id}.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
        }
        try:
            with yt_dlp.YoutubeDL(sub_opts) as sub_ydl:
                sub_ydl.download([v_url])
            
            # Check if subtitle file was created
            created_subs = list(subtitles_dir.glob(f"{v_id}*"))
            if created_subs:
                v["has_subtitle"] = True
                v["subtitle_file"] = str(created_subs[0])
            elif download_audio_if_no_sub:
                # Fallback to audio download
                audio_opts: dict[str, Any] = {
                    "format": "bestaudio/best",
                    "outtmpl": str(audio_dir / f"{v_id}.%(ext)s"),
                    "quiet": True,
                    "no_warnings": True,
                    "ignoreerrors": True,
                }
                with yt_dlp.YoutubeDL(audio_opts) as aud_ydl:
                    aud_ydl.download([v_url])
        except Exception as err:
            logger.warning(f"Could not download transcript/audio for {v_id}: {err}")

    manifest_path.write_text(json.dumps(videos, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Saved complete manifest for {len(videos)} videos to {manifest_path}")
    return videos


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python collector.py <tiktok_username_or_url> [output_directory]")
        sys.exit(1)

    target = sys.argv[1]
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "data"
    extract_tiktok_channel_videos(target, out_dir, download_audio_if_no_sub=True)
