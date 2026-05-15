from __future__ import annotations

import logging
from dataclasses import dataclass
from time import monotonic, sleep
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

LOGGER = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    url: str
    status_code: int
    html: str
    error: str = ""


class PageCrawler:
    def __init__(self, user_agent: str, timeout: int = 20, request_delay_seconds: float = 0.0, obey_robots_txt: bool = True):
        self.timeout = timeout
        self.user_agent = user_agent
        self.request_delay_seconds = max(float(request_delay_seconds or 0), 0)
        self.obey_robots_txt = obey_robots_txt
        self._last_request_at = 0.0
        self._robots_cache: dict[str, RobotFileParser] = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def fetch(self, url: str) -> CrawlResult:
        try:
            if self.obey_robots_txt and not self._can_fetch(url):
                return CrawlResult(url=url, status_code=0, html="", error="Blocked by robots.txt")
            self._wait_for_delay()
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return CrawlResult(url=str(response.url), status_code=response.status_code, html="", error=f"Unsupported content-type: {content_type}")
            return CrawlResult(url=str(response.url), status_code=response.status_code, html=response.text)
        except requests.RequestException as exc:
            LOGGER.warning("Failed to fetch %s: %s", url, exc)
            return CrawlResult(url=url, status_code=0, html="", error=str(exc))

    def _wait_for_delay(self) -> None:
        if self.request_delay_seconds <= 0:
            return
        elapsed = monotonic() - self._last_request_at
        remaining = self.request_delay_seconds - elapsed
        if remaining > 0:
            sleep(remaining)
        self._last_request_at = monotonic()

    def _can_fetch(self, url: str) -> bool:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        root = f"{parsed.scheme}://{parsed.netloc}"
        robot = self._robots_cache.get(root)
        if robot is None:
            robot = RobotFileParser()
            robot.set_url(f"{root}/robots.txt")
            try:
                robot.read()
            except Exception as exc:  # noqa: BLE001
                LOGGER.debug("Could not read robots.txt for %s: %s", root, exc)
            self._robots_cache[root] = robot
        try:
            return robot.can_fetch(self.user_agent, url)
        except Exception:  # noqa: BLE001
            return True
