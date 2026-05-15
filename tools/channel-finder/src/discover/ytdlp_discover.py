from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Any, Dict, Iterable, List
from urllib.parse import quote_plus

from src.utils import format_count, unique_list

LOGGER = logging.getLogger(__name__)


class YtDlpDiscoverer:
    """Discover YouTube creator candidates through yt-dlp metadata search.

    This does not download video media and does not use cookies or login data.
    """

    def __init__(self, max_results_per_keyword: int = 20):
        self.max_results_per_keyword = max(1, min(int(max_results_per_keyword or 20), 50))

    def discover(self, keywords: Iterable[str]) -> List[Dict[str, Any]]:
        try:
            import yt_dlp  # type: ignore
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("yt-dlp package is not available. Skipping yt-dlp discovery: %s", exc)
            return []

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": True,
            "ignoreerrors": True,
            "noplaylist": True,
        }
        videos_by_channel: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for keyword in keywords:
                query = f"ytsearch{self.max_results_per_keyword}:{keyword}"
                try:
                    payload = ydl.extract_info(query, download=False)
                except Exception as exc:  # noqa: BLE001
                    LOGGER.warning("yt-dlp discovery failed for %s: %s", keyword, exc)
                    continue
                for entry in (payload or {}).get("entries") or []:
                    if not entry:
                        continue
                    channel_id = _valid_youtube_channel_id(entry.get("channel_id"))
                    channel_url = entry.get("channel_url") or ""
                    channel_key = channel_id or channel_url or entry.get("uploader") or entry.get("channel") or ""
                    if not channel_key:
                        continue
                    videos_by_channel[str(channel_key)].append({
                        "video_id": entry.get("id") or "",
                        "title": entry.get("title") or "Unknown",
                        "description": entry.get("description") or "",
                        "channel_id": channel_id or "",
                        "channel": entry.get("channel") or entry.get("uploader") or "Unknown",
                        "channel_url": channel_url,
                        "view_count": entry.get("view_count"),
                        "upload_date": entry.get("upload_date") or "",
                        "timestamp": entry.get("timestamp"),
                        "source_keyword": keyword,
                        "webpage_url": entry.get("webpage_url") or entry.get("url") or "",
                    })

        candidates: List[Dict[str, Any]] = []
        for channel_key, videos in videos_by_channel.items():
            first = videos[0]
            channel_id = _valid_youtube_channel_id(first.get("channel_id")) or ""
            channel_url = first.get("channel_url") or ""
            if not channel_url and channel_id:
                channel_url = f"https://www.youtube.com/channel/{channel_id}"
            if not channel_url:
                channel_url = f"https://www.youtube.com/results?search_query={quote_plus(str(channel_key))}"
            view_values = [int(v["view_count"]) for v in videos if isinstance(v.get("view_count"), int)]
            avg_views = int(sum(view_values) / len(view_values)) if view_values else None
            upload_dates = [v.get("upload_date") for v in videos if v.get("upload_date")]
            recent_activity = max(upload_dates) if upload_dates else "Unknown"
            recent_titles = unique_list([str(v.get("title") or "") for v in videos])[:8]
            source_keywords = unique_list([str(v.get("source_keyword") or "") for v in videos])
            candidates.append({
                "channel_type": "YouTube Creator",
                "platform": "YouTube",
                "platform_id": channel_id or "",
                "name": first.get("channel") or "Unknown",
                "url": channel_url,
                "canonical_url": channel_url,
                "domain": "youtube.com",
                "topic": "; ".join(recent_titles[:3]) or "Unknown",
                "audience": "Developer / AI / SEO audience inferred from video topics",
                "subscribers_or_followers": "Unknown",
                "avg_views": format_count(avg_views),
                "recent_activity": recent_activity,
                "recent_titles": recent_titles,
                "description_excerpt": "\n".join(str(v.get("description") or "") for v in videos)[:1000],
                "source_keyword": ", ".join(source_keywords),
                "source_provider": "ytdlp",
                "source_url": channel_url,
                "discovery_query": ", ".join(source_keywords),
                "confidence": "medium",
                "contact_email": "Unknown",
                "contact_page": "Unknown",
                "sponsor_page": "Unknown",
                "media_kit_url": "Unknown",
                "raw": {"videos": videos},
            })
        return candidates


def _valid_youtube_channel_id(value: Any) -> str:
    text = str(value or "").strip()
    if re.fullmatch(r"UC[a-zA-Z0-9_-]{20,}", text):
        return text
    return ""
