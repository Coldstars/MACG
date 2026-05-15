from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import requests

from src.utils import format_count, safe_get, unique_list

LOGGER = logging.getLogger(__name__)
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeDiscoverer:
    """Discover YouTube creator candidates using the official YouTube Data API.

    This module does not scrape private information or bypass platform limits.
    It only uses public API endpoints and returns Unknown when data is missing.
    """

    def __init__(self, api_key: str, max_results_per_keyword: int = 10):
        self.api_key = api_key
        self.max_results_per_keyword = max(1, min(max_results_per_keyword, 50))
        self.session = requests.Session()

    def discover(self, keywords: Iterable[str]) -> List[Dict[str, Any]]:
        if not self.api_key:
            LOGGER.info("YOUTUBE_API_KEY not configured. Skipping YouTube discovery.")
            return []

        videos_by_channel: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for keyword in keywords:
            videos = self._search_videos(keyword)
            for video in videos:
                channel_id = video.get("channel_id")
                if channel_id:
                    videos_by_channel[channel_id].append(video)

        channel_ids = list(videos_by_channel.keys())
        channel_details = self._get_channels(channel_ids)

        candidates: List[Dict[str, Any]] = []
        for channel_id, videos in videos_by_channel.items():
            details = channel_details.get(channel_id, {})
            recent_titles = unique_list([v.get("title", "") for v in videos])[:8]
            descriptions = "\n".join(v.get("description", "") for v in videos if v.get("description"))
            published_dates = [v.get("published_at") for v in videos if v.get("published_at")]
            recent_activity = max(published_dates) if published_dates else "Unknown"
            avg_views = self._average_video_views([v.get("video_id") for v in videos if v.get("video_id")])

            name = details.get("title") or videos[0].get("channel_title") or "Unknown"
            custom_url = details.get("custom_url") or ""
            url = f"https://www.youtube.com/channel/{channel_id}"
            if custom_url:
                url = f"https://www.youtube.com/{custom_url}" if custom_url.startswith("@") else url

            candidates.append({
                "channel_type": "YouTube Creator",
                "platform": "YouTube",
                "platform_id": channel_id,
                "name": name,
                "url": url,
                "canonical_url": f"https://www.youtube.com/channel/{channel_id}",
                "domain": "youtube.com",
                "topic": "; ".join(recent_titles[:3]) or "Unknown",
                "audience": "Developer / AI / SEO audience inferred from video topics",
                "subscribers_or_followers": format_count(details.get("subscriber_count")),
                "avg_views": format_count(avg_views),
                "recent_activity": recent_activity,
                "recent_titles": recent_titles,
                "description_excerpt": descriptions[:1000],
                "source_keyword": ", ".join(unique_list([v.get("source_keyword", "") for v in videos])),
                "source_provider": "youtube_api",
                "source_url": url,
                "discovery_query": ", ".join(unique_list([v.get("source_keyword", "") for v in videos])),
                "confidence": "high",
                "contact_email": "Unknown",
                "contact_page": "Unknown",
                "sponsor_page": "Unknown",
                "media_kit_url": "Unknown",
                "raw": {
                    "channel": details,
                    "videos": videos,
                },
            })

        return candidates

    def _search_videos(self, keyword: str) -> List[Dict[str, Any]]:
        params = {
            "key": self.api_key,
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "maxResults": self.max_results_per_keyword,
            "order": "relevance",
            "safeSearch": "none",
        }
        response = self.session.get(f"{YOUTUBE_API_BASE}/search", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        results: List[Dict[str, Any]] = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            results.append({
                "video_id": safe_get(item, "id", "videoId", default=""),
                "channel_id": snippet.get("channelId") or "",
                "channel_title": snippet.get("channelTitle") or "Unknown",
                "title": snippet.get("title") or "Unknown",
                "description": snippet.get("description") or "",
                "published_at": snippet.get("publishedAt") or "Unknown",
                "source_keyword": keyword,
            })
        return results

    def _get_channels(self, channel_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        if not channel_ids:
            return {}
        result: Dict[str, Dict[str, Any]] = {}
        for i in range(0, len(channel_ids), 50):
            batch = channel_ids[i:i + 50]
            params = {
                "key": self.api_key,
                "part": "snippet,statistics",
                "id": ",".join(batch),
                "maxResults": 50,
            }
            response = self.session.get(f"{YOUTUBE_API_BASE}/channels", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            for item in data.get("items", []):
                channel_id = item.get("id")
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                if not channel_id:
                    continue
                result[channel_id] = {
                    "title": snippet.get("title") or "Unknown",
                    "description": snippet.get("description") or "",
                    "custom_url": snippet.get("customUrl") or "",
                    "published_at": snippet.get("publishedAt") or "Unknown",
                    "subscriber_count": stats.get("subscriberCount"),
                    "view_count": stats.get("viewCount"),
                    "video_count": stats.get("videoCount"),
                }
        return result

    def _average_video_views(self, video_ids: List[str]) -> Optional[int]:
        if not video_ids:
            return None
        views: List[int] = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i + 50]
            params = {
                "key": self.api_key,
                "part": "statistics",
                "id": ",".join(batch),
                "maxResults": 50,
            }
            response = self.session.get(f"{YOUTUBE_API_BASE}/videos", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            for item in data.get("items", []):
                view_count = item.get("statistics", {}).get("viewCount")
                try:
                    if view_count is not None:
                        views.append(int(view_count))
                except ValueError:
                    continue
        if not views:
            return None
        return int(sum(views) / len(views))
