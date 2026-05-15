from __future__ import annotations

import re
from typing import Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.utils import normalize_url, unique_list

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

CONTACT_PATTERNS = ["contact", "business", "inquiry", "inquiries", "work-with", "work with", "合作", "联系"]
SPONSOR_PATTERNS = ["sponsor", "sponsorship", "advertise", "advertising", "partner", "partnership", "collaboration", "media-kit", "media kit"]
MEDIA_KIT_PATTERNS = ["media kit", "mediakit", "media-kit", "rate card", "advertising kit"]


def extract_contacts(html: str, base_url: str = "") -> Dict[str, List[str]]:
    """Extract public contact and sponsorship signals from HTML.

    This function only parses provided public HTML. It does not bypass login,
    CAPTCHA, paywalls, or hidden data.
    """
    if not html:
        return {"emails": [], "contact_pages": [], "sponsor_pages": [], "media_kit_urls": [], "external_links": []}

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    emails = unique_list(EMAIL_RE.findall(text))

    contact_pages: List[str] = []
    sponsor_pages: List[str] = []
    media_kit_urls: List[str] = []
    external_links: List[str] = []

    for a in soup.find_all("a", href=True):
        href = str(a.get("href") or "").strip()
        label = " ".join([str(a.get_text(" ", strip=True) or ""), href]).lower()
        if href.startswith("mailto:"):
            email = href.replace("mailto:", "").split("?")[0]
            if EMAIL_RE.fullmatch(email):
                emails.append(email)
            continue
        absolute = normalize_url(urljoin(base_url, href))
        if not absolute:
            continue
        external_links.append(absolute)
        if any(p in label for p in CONTACT_PATTERNS):
            contact_pages.append(absolute)
        if any(p in label for p in SPONSOR_PATTERNS):
            sponsor_pages.append(absolute)
        if any(p in label for p in MEDIA_KIT_PATTERNS):
            media_kit_urls.append(absolute)

    return {
        "emails": unique_list(emails),
        "contact_pages": unique_list(contact_pages),
        "sponsor_pages": unique_list(sponsor_pages),
        "media_kit_urls": unique_list(media_kit_urls),
        "external_links": unique_list(external_links),
    }


def first_or_unknown(values: List[str]) -> str:
    return values[0] if values else "Unknown"
