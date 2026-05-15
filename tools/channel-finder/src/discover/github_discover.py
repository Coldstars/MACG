from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List

import requests

from src.utils import domain_from_url, format_count, normalize_url

LOGGER = logging.getLogger(__name__)
GITHUB_SEARCH_REPOS = "https://api.github.com/search/repositories"


class GitHubDiscoverer:
    """Discover developer-facing candidates from the public GitHub API.

    Uses unauthenticated REST calls by default, so limits are intentionally
    conservative. A GitHub token is not required.
    """

    def __init__(self, max_results_per_keyword: int = 10, timeout: int = 20):
        self.max_results_per_keyword = max(1, min(int(max_results_per_keyword or 10), 30))
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "User-Agent": "MACG-ChannelFinder/1.0",
        })

    def discover(self, keywords: Iterable[str]) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = []
        for keyword in keywords:
            query = self._expand_query(keyword)
            try:
                response = self.session.get(
                    GITHUB_SEARCH_REPOS,
                    params={"q": query, "sort": "stars", "order": "desc", "per_page": self.max_results_per_keyword},
                    timeout=self.timeout,
                )
                if response.status_code in (403, 429):
                    LOGGER.warning("GitHub discovery hit rate limit for %s: %s", keyword, response.text[:200])
                    break
                response.raise_for_status()
                payload = response.json()
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning("GitHub discovery failed for %s: %s", keyword, exc)
                continue
            for repo in payload.get("items", [])[: self.max_results_per_keyword]:
                repo_url = normalize_url(repo.get("html_url") or "")
                if not repo_url:
                    continue
                homepage = normalize_url(repo.get("homepage") or "")
                target_url = homepage or repo_url
                owner = repo.get("owner") or {}
                candidates.append({
                    "channel_type": "Developer Project",
                    "platform": "GitHub",
                    "platform_id": str(repo.get("id") or ""),
                    "name": repo.get("full_name") or repo.get("name") or "Unknown",
                    "url": target_url,
                    "canonical_url": repo_url,
                    "domain": domain_from_url(target_url) or "github.com",
                    "topic": (repo.get("description") or repo.get("full_name") or "Unknown")[:240],
                    "audience": "Developers / open-source users inferred from GitHub repository",
                    "subscribers_or_followers": format_count(repo.get("stargazers_count")),
                    "avg_views": "Unknown",
                    "recent_activity": repo.get("pushed_at") or repo.get("updated_at") or "Unknown",
                    "contact_email": "Unknown",
                    "contact_page": homepage or repo_url,
                    "sponsor_page": normalize_url(owner.get("html_url") or ""),
                    "media_kit_url": "Unknown",
                    "source_keyword": keyword,
                    "source_provider": "github",
                    "source_url": repo_url,
                    "discovery_query": query,
                    "confidence": "medium",
                    "raw": repo,
                })
        return candidates

    def _expand_query(self, keyword: str) -> str:
        keyword = (keyword or "").strip()
        base = f"{keyword} stars:>20"
        # GitHub search syntax is passed through requests params, but quote-like
        # terms still keep the search focused.
        return f"{base} in:name,description,readme"
