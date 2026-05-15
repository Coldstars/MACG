from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List

from src.utils import domain_from_url, normalize_url

LOGGER = logging.getLogger(__name__)


class DDGSDiscoverer:
    """Discover public web candidates from DuckDuckGo search results.

    Uses the optional `ddgs` package. This is a free discovery source, but it is
    still best-effort and should be run with conservative limits.
    """

    def __init__(self, max_results_per_keyword: int = 20, region: str = "us-en", safesearch: str = "moderate"):
        self.max_results_per_keyword = max(1, min(int(max_results_per_keyword or 20), 50))
        self.region = region or "us-en"
        self.safesearch = safesearch or "moderate"

    def discover(self, keywords: Iterable[str]) -> List[Dict[str, Any]]:
        try:
            from ddgs import DDGS  # type: ignore
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning("ddgs package is not available. Skipping DDGS discovery: %s", exc)
            return []

        candidates: List[Dict[str, Any]] = []
        with DDGS() as ddgs:
            for keyword in keywords:
                query = self._expand_query(keyword)
                try:
                    rows = list(ddgs.text(
                        query,
                        region=self.region,
                        safesearch=self.safesearch,
                        max_results=self.max_results_per_keyword,
                    ))
                except Exception as exc:  # noqa: BLE001
                    LOGGER.warning("DDGS discovery failed for %s: %s", keyword, exc)
                    continue

                for row in rows[: self.max_results_per_keyword]:
                    href = normalize_url(str(row.get("href") or row.get("url") or ""))
                    if not href:
                        continue
                    title = str(row.get("title") or domain_from_url(href) or "Unknown")
                    body = str(row.get("body") or row.get("snippet") or "")
                    candidates.append({
                        "channel_type": self._infer_channel_type(title, body, href),
                        "platform": "Web",
                        "platform_id": "",
                        "name": title,
                        "url": href,
                        "canonical_url": href,
                        "domain": domain_from_url(href),
                        "topic": body[:240] or title,
                        "audience": "Unknown",
                        "subscribers_or_followers": "Unknown",
                        "avg_views": "Unknown",
                        "recent_activity": "Unknown",
                        "contact_email": "Unknown",
                        "contact_page": "Unknown",
                        "sponsor_page": "Unknown",
                        "media_kit_url": "Unknown",
                        "source_keyword": keyword,
                        "source_provider": "ddgs",
                        "source_url": href,
                        "discovery_query": query,
                        "confidence": "medium",
                        "raw": row,
                    })
        return candidates

    def _expand_query(self, keyword: str) -> str:
        keyword = (keyword or "").strip()
        if any(token in keyword.lower() for token in ["sponsor", "newsletter", "blog", "youtube"]):
            return keyword
        return f"{keyword} tutorial blog newsletter sponsor advertising"

    def _infer_channel_type(self, title: str, body: str, url: str) -> str:
        text = f"{title} {body} {url}".lower()
        if "youtube.com" in text or "youtu.be" in text:
            return "YouTube Creator"
        if "newsletter" in text or "substack" in text or "beehiiv" in text:
            return "Newsletter"
        if any(token in text for token in ["sponsor", "advertise", "media kit", "partnership"]):
            return "Sponsor Page"
        return "Technical Blog"
