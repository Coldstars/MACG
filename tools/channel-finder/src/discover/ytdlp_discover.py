from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Any, Dict, Iterable, List
from urllib.parse import quote_plus

from src.crawl.contact_extractor import extract_emails_from_text, first_or_unknown
from src.utils import format_count, unique_list

LOGGER = logging.getLogger(__name__)


class YtDlpDiscoverer:
    """Discover YouTube creator candidates through yt-dlp metadata search.

    This does not download video media and does not use cookies or login data.
    """

    def __init__(self, max_results_per_keyword: int = 20, enrich_video_details: bool = True, max_detail_channels: int = 80):
        self.max_results_per_keyword = max(1, min(int(max_results_per_keyword or 20), 50))
        self.enrich_video_details = bool(enrich_video_details)
        self.max_detail_channels = max(0, int(max_detail_channels or 0))

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

        if self.enrich_video_details and self.max_detail_channels > 0:
            self._enrich_video_descriptions(yt_dlp, videos_by_channel)

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
            description_text = "\n".join(str(v.get("description") or "") for v in videos)
            emails = extract_emails_from_text(description_text)
            competitor_keywords = [
                keyword for keyword in source_keywords
                if any(token in keyword.lower() for token in ["review", "alternative", "comparison", "sponsor", "sponsored"])
            ]
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
                "description_excerpt": description_text[:1000],
                "source_keyword": ", ".join(source_keywords),
                "source_provider": "ytdlp",
                "source_url": channel_url,
                "discovery_query": ", ".join(source_keywords),
                "confidence": "medium",
                "contact_email": first_or_unknown(emails),
                "contact_page": channel_url,
                "sponsor_page": "Unknown",
                "media_kit_url": "Unknown",
                "notes": "Discovered from competitor-related query." if competitor_keywords else "",
                "raw": {"videos": videos, "emails_from_video_descriptions": emails},
            })
        return candidates

    def _enrich_video_descriptions(self, yt_dlp: Any, videos_by_channel: Dict[str, List[Dict[str, Any]]]) -> None:
        detail_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "ignoreerrors": True,
            "noplaylist": True,
        }
        checked = 0
        with yt_dlp.YoutubeDL(detail_opts) as ydl:
            for videos in videos_by_channel.values():
                if checked >= self.max_detail_channels:
                    return
                target = next((video for video in videos if video.get("webpage_url")), None)
                if not target:
                    continue
                checked += 1
                try:
                    detail = ydl.extract_info(str(target.get("webpage_url")), download=False)
                except Exception as exc:  # noqa: BLE001
                    LOGGER.debug("yt-dlp detail enrichment failed for %s: %s", target.get("webpage_url"), exc)
                    continue
                if not detail:
                    continue
                description = detail.get("description") or ""
                if description:
                    target["description"] = description
                if detail.get("view_count") is not None:
                    target["view_count"] = detail.get("view_count")
                if detail.get("upload_date"):
                    target["upload_date"] = detail.get("upload_date")


def _valid_youtube_channel_id(value: Any) -> str:
    text = str(value or "").strip()
    if re.fullmatch(r"UC[a-zA-Z0-9_-]{20,}", text):
        return text
    return ""
