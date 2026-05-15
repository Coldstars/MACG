from __future__ import annotations

from typing import Any, Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.crawl.contact_extractor import extract_contacts, first_or_unknown
from src.crawl.page_crawler import PageCrawler
from src.utils import domain_from_url, normalize_url, unique_list


class NewsletterDiscoverer:
    """Discover newsletter/blog candidates from configured public seed URLs."""

    def __init__(self, crawler: PageCrawler, max_links_per_seed: int = 12):
        self.crawler = crawler
        self.max_links_per_seed = max(0, int(max_links_per_seed or 0))

    def discover_from_seed_urls(self, urls: List[str], channel_type: str = "Newsletter") -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = []
        for url in urls:
            normalized = normalize_url(url)
            seed_candidate, links = self._candidate_from_url(normalized, channel_type, source_keyword="seed_url")
            candidates.append(seed_candidate)
            for link in links[: self.max_links_per_seed]:
                linked_candidate, _ = self._candidate_from_url(link, channel_type, source_keyword="seed_link")
                candidates.append(linked_candidate)
        return candidates

    def from_manual_seeds(self, seeds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = []
        for seed in seeds or []:
            url = normalize_url(str(seed.get("url") or ""))
            if not url:
                continue
            channel_type = seed.get("channel_type") or seed.get("platform") or "Manual Seed"
            candidate = self._base_candidate(url, channel_type)
            candidate.update({
                "name": seed.get("name") or domain_from_url(url) or "Unknown",
                "platform": seed.get("platform") or channel_type,
                "topic": seed.get("topic") or "Unknown",
                "audience": seed.get("audience") or "Unknown",
                "subscribers_or_followers": seed.get("subscribers_or_followers") or "Unknown",
                "avg_views": seed.get("avg_views") or "Unknown",
                "recent_activity": seed.get("recent_activity") or "Unknown",
                "contact_email": seed.get("contact_email") or "Unknown",
                "contact_page": seed.get("contact_page") or "Unknown",
                "sponsor_page": seed.get("sponsor_page") or "Unknown",
                "media_kit_url": seed.get("media_kit_url") or "Unknown",
                "source_keyword": seed.get("source_keyword") or "manual_seed",
                "source_provider": "manual",
                "source_url": url,
                "discovery_query": seed.get("source_keyword") or "manual_seed",
                "confidence": seed.get("confidence") or "high",
                "raw": seed,
            })
            candidates.append(candidate)
        return candidates

    def _candidate_from_url(self, url: str, channel_type: str, source_keyword: str) -> tuple[Dict[str, Any], List[str]]:
        result = self.crawler.fetch(url)
        if result.status_code == 0 or not result.html:
            return self._base_candidate(url, channel_type, error=result.error, source_keyword=source_keyword), []

        soup = BeautifulSoup(result.html, "html.parser")
        extracted = self._extract_readable_metadata(result.html, result.url)
        title = extracted.get("title") or "Unknown"
        if title == "Unknown" and soup.title and soup.title.string:
            title = soup.title.string.strip()
        meta_desc = extracted.get("description") or ""
        if not meta_desc:
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                meta_desc = str(meta.get("content"))
        text_excerpt = extracted.get("text") or ""
        contacts = extract_contacts(result.html, result.url)
        candidate = self._base_candidate(result.url, channel_type, source_keyword=source_keyword)
        candidate.update({
            "name": title or domain_from_url(result.url) or "Unknown",
            "topic": meta_desc[:240] or text_excerpt[:240] or title or "Unknown",
            "audience": "Unknown",
            "contact_email": first_or_unknown(contacts["emails"]),
            "contact_page": first_or_unknown(contacts["contact_pages"]),
            "sponsor_page": first_or_unknown(contacts["sponsor_pages"]),
            "media_kit_url": first_or_unknown(contacts["media_kit_urls"]),
            "description_excerpt": text_excerpt[:1000],
            "raw": {"status_code": result.status_code, "meta_description": meta_desc, "crawl_error": result.error},
        })
        return candidate, self._extract_candidate_links(result.html, result.url)

    def _extract_readable_metadata(self, html: str, url: str) -> Dict[str, str]:
        try:
            import trafilatura  # type: ignore
        except Exception:  # noqa: BLE001
            return {}
        try:
            metadata = trafilatura.extract_metadata(html)
            text = trafilatura.extract(html, url=url, include_comments=False, include_tables=False) or ""
        except Exception:  # noqa: BLE001
            return {}
        return {
            "title": (getattr(metadata, "title", "") or "").strip() if metadata else "",
            "description": (getattr(metadata, "description", "") or "").strip() if metadata else "",
            "text": text.strip(),
        }

    def _extract_candidate_links(self, html: str, base_url: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links: List[str] = []
        positive_tokens = [
            "newsletter", "blog", "sponsor", "advertise", "advertising", "media-kit",
            "media kit", "partner", "partnership", "creator", "youtube", "substack",
            "beehiiv", "publication", "directory",
        ]
        negative_tokens = ["login", "signin", "signup", "privacy", "terms", "cookie", "facebook.com", "twitter.com/intent"]
        for a in soup.find_all("a", href=True):
            href = str(a.get("href") or "").strip()
            label = f"{a.get_text(' ', strip=True)} {href}".lower()
            if any(token in label for token in negative_tokens):
                continue
            absolute = normalize_url(urljoin(base_url, href))
            if not absolute:
                continue
            if any(token in label for token in positive_tokens):
                links.append(absolute)
        return unique_list(links)

    def _base_candidate(self, url: str, channel_type: str, error: str = "", source_keyword: str = "seed_url") -> Dict[str, Any]:
        domain = domain_from_url(url)
        return {
            "channel_type": channel_type,
            "platform": channel_type,
            "platform_id": "",
            "name": domain or "Unknown",
            "url": url,
            "canonical_url": url,
            "domain": domain,
            "topic": "Unknown",
            "audience": "Unknown",
            "subscribers_or_followers": "Unknown",
            "avg_views": "Unknown",
            "recent_activity": "Unknown",
            "contact_email": "Unknown",
            "contact_page": "Unknown",
            "sponsor_page": "Unknown",
            "media_kit_url": "Unknown",
            "source_keyword": source_keyword,
            "source_provider": "seed",
            "source_url": url,
            "discovery_query": source_keyword,
            "confidence": "low" if error else "medium",
            "notes": error or "",
            "raw": {},
        }
