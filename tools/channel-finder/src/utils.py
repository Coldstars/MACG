from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse, urlunparse

try:
    import yaml
except Exception:  # noqa: BLE001
    yaml = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str, fallback: str = "channel-discovery") -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or fallback


def load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load configuration files. Install dependencies with `pip install -r requirements.txt`.")
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping: {path}")
    return data


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = re.sub(r"/+$", "", parsed.path or "")
    return urlunparse((scheme, netloc, path, "", "", ""))


def domain_from_url(url: str) -> str:
    normalized = normalize_url(url)
    if not normalized:
        return ""
    netloc = urlparse(normalized).netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    return netloc


def flatten_text(*parts: Any) -> str:
    return " ".join(str(p or "") for p in parts).strip()


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    text_l = (text or "").lower()
    return any((kw or "").lower() in text_l for kw in keywords)


def unique_list(items: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if not item:
            continue
        key = item.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(item.strip())
    return result


def parse_int(value: Any) -> Optional[int]:
    if value is None or value == "Unknown":
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).strip().replace(",", "")
    multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)([kmbKMB]?)", text)
    if match:
        number = float(match.group(1))
        suffix = match.group(2).lower()
        return int(number * multipliers.get(suffix, 1))
    digits = re.sub(r"[^0-9]", "", text)
    return int(digits) if digits else None


def format_count(value: Any) -> str:
    n = parse_int(value)
    if n is None:
        return "Unknown"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.1f}K".replace(".0K", "K")
    return str(n)


def safe_get(mapping: Dict[str, Any], *keys: str, default: Any = "Unknown") -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current if current not in (None, "") else default


def sleep_delay(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


def merge_missing(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in source.items():
        if target.get(key) in (None, "", "Unknown", [], {}):
            target[key] = value
    return target


def canonical_candidate_key(candidate: Dict[str, Any]) -> str:
    platform = str(candidate.get("platform") or "").lower()
    platform_id = str(candidate.get("platform_id") or "").strip().lower()
    if platform_id and platform_id not in {"unknown", "none", "n/a", "na"}:
        return f"{platform}:id:{platform_id}"
    canonical_url = normalize_url(str(candidate.get("canonical_url") or candidate.get("url") or ""))
    if canonical_url:
        domain = domain_from_url(canonical_url)
        if platform in {"youtube", "youtube creator"}:
            return f"youtube:url:{canonical_url}"
        if domain:
            return f"domain:{domain}"
        return f"url:{canonical_url}"
    name = re.sub(r"[^a-z0-9]+", "", str(candidate.get("name") or "").lower())
    return f"{platform}:name:{name}"


def guess_workspace_root(tool_dir: Path) -> Path:
    env_root = os.getenv("WORKSPACE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    # tools/channel-finder -> MACG root -> workspaces
    return (tool_dir / ".." / ".." / "workspaces").resolve()
