from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterable, List
from urllib.parse import quote_plus

import requests

from src.utils import domain_from_url, normalize_url

LOGGER = logging.getLogger(__name__)


class SerpDiscoverer:
    """Optional generic SERP discovery.

    This module supports a user-provided URL template in config/sources.yaml:
    `https://api.example.com/search?q={query}&num={num}`

    Expected response formats supported:
    - {"organic_results": [{"title": "...", "link": "...", "snippet": "..."}]}
    - {"results": [{"title": "...", "url": "...", "snippet": "..."}]}

    If no template is configured, this module returns no candidates.
    """

    def __init__(self, url_template: str = "", max_results_per_keyword: int = 10):
        self.url_template = url_template or ""
        self.max_results_per_keyword = max_results_per_keyword
        self.session = requests.Session()

    def discover(self, keywords: Iterable[str]) -> List[Dict[str, Any]]:
        if not self.url_template:
            LOGGER.info("No SERP URL template configured. Skipping generic SERP discovery.")
            return []
        candidates: List[Dict[str, Any]] = []
        for keyword in keywords:
            url = self.url_template.format(query=quote_plus(keyword), num=self.max_results_per_keyword, api_key=os.getenv("SERP_API_KEY", ""))
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                payload = response.json()
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("SERP discovery failed for %s: %s", keyword, exc)
                continue
            rows = payload.get("organic_results") or payload.get("results") or []
            for row in rows[: self.max_results_per_keyword]:
                link = normalize_url(row.get("link") or row.get("url") or "")
                if not link:
                    continue
                title = row.get("title") or domain_from_url(link) or "Unknown"
                snippet = row.get("snippet") or row.get("description") or ""
                candidates.append({
                    "channel_type": "Technical Blog",
                    "platform": "Web",
                    "platform_id": "",
                    "name": title,
                    "url": link,
                    "canonical_url": link,
                    "domain": domain_from_url(link),
                    "topic": snippet[:240] or title,
                    "audience": "Unknown",
                    "subscribers_or_followers": "Unknown",
                    "avg_views": "Unknown",
                    "recent_activity": "Unknown",
                    "contact_email": "Unknown",
                    "contact_page": "Unknown",
                    "sponsor_page": "Unknown",
                    "media_kit_url": "Unknown",
                    "source_keyword": keyword,
                    "source_provider": "serp",
                    "source_url": link,
                    "discovery_query": keyword,
                    "confidence": "medium",
                    "raw": row,
                })
        return candidates
