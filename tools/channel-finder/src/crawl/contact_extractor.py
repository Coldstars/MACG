from __future__ import annotations

import html
import re
from typing import Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.utils import normalize_url, unique_list

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
OBFUSCATED_EMAIL_RE = re.compile(
    r"\b([A-Za-z0-9._%+-]+)\s*(?:\[at\]|\(at\)|\sat\s)\s*"
    r"([A-Za-z0-9.-]+)\s*(?:\[dot\]|\(dot\)|\sdot\s)\s*([A-Za-z]{2,})\b",
    flags=re.IGNORECASE,
)

CONTACT_PATTERNS = [
    "contact", "about", "business", "inquiry", "inquiries", "work-with",
    "work with", "collab", "collaboration", "press", "media", "support",
    "hello", "email", "creator", "合作", "联系", "关于",
]
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
    emails = extract_emails_from_text(text + " " + str(html))

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


def extract_emails_from_text(value: str) -> List[str]:
    text = html.unescape(str(value or ""))
    emails = EMAIL_RE.findall(text)
    for match in OBFUSCATED_EMAIL_RE.finditer(text):
        emails.append(f"{match.group(1)}@{match.group(2)}.{match.group(3)}")
    return unique_list([email.strip().strip(".,;:") for email in emails if _is_public_email(email)])


def _is_public_email(email: str) -> bool:
    lowered = str(email or "").lower()
    if not EMAIL_RE.fullmatch(lowered):
        return False
    blocked_domains = {
        "example.com",
        "example.org",
        "example.net",
        "domain.com",
        "email.com",
        "yourdomain.com",
        "sentry.io",
        "w3.org",
    }
    domain = lowered.split("@")[-1]
    return domain not in blocked_domains


def first_or_unknown(values: List[str]) -> str:
    return values[0] if values else "Unknown"
