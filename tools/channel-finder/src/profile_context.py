from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List

from src.utils import unique_list


@dataclass
class ProfileContext:
    path: str = ""
    product_name: str = ""
    product_website: str = ""
    industry_keywords: List[str] = field(default_factory=list)
    product_lines: List[str] = field(default_factory=list)
    target_users: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    value_props: List[str] = field(default_factory=list)
    competitor_reference_sites: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "product_name": self.product_name,
            "product_website": self.product_website,
            "industry_keywords": self.industry_keywords,
            "product_lines": self.product_lines,
            "target_users": self.target_users,
            "use_cases": self.use_cases,
            "value_props": self.value_props,
            "competitor_reference_sites": self.competitor_reference_sites,
        }


def find_profile_path(start: Path, explicit_path: str = "") -> Path | None:
    if explicit_path:
        path = Path(explicit_path).expanduser().resolve()
        return path if path.exists() else None
    for parent in [start.resolve(), *start.resolve().parents]:
        candidate = parent / "profile.md"
        if candidate.exists():
            return candidate
    return None


def load_profile_context(path: Path | None) -> ProfileContext:
    if not path or not path.exists():
        return ProfileContext()
    text = path.read_text(encoding="utf-8")
    sections = _parse_sections(text)
    context = ProfileContext(
        path=str(path),
        product_website=_extract_url("\n".join(sections.get("Product Website", []))),
        industry_keywords=_section_items(sections, "Industry"),
        product_lines=_section_items(sections, "Main Product Lines"),
        target_users=_section_items(sections, "Target Users"),
        use_cases=_section_items(sections, "Main Use Cases"),
        value_props=_section_items(sections, "Core Product Value Propositions"),
        competitor_reference_sites=_section_items(sections, "Main Competitors / Reference Sites"),
    )
    context.product_name = _infer_product_name(text, context)
    return context


def build_profile_keywords(context: ProfileContext, limit: int = 40) -> List[str]:
    keyword_candidates: List[str] = []
    keyword_candidates.extend(context.industry_keywords)
    keyword_candidates.extend(context.product_lines)
    keyword_candidates.extend(context.use_cases)

    expanded: List[str] = []
    for keyword in keyword_candidates:
        clean = _clean_item(keyword)
        if not clean:
            continue
        expanded.append(clean)
        lowered = clean.lower()
        if not any(token in lowered for token in ["tutorial", "guide", "automation", "workflow", "api"]):
            expanded.append(f"{clean} tutorial")
            expanded.append(f"{clean} guide")
    return unique_list(expanded)[:limit]


def merge_profile_into_scoring_rules(scoring_rules: Dict[str, Any], context: ProfileContext) -> Dict[str, Any]:
    merged: Dict[str, Any] = dict(scoring_rules or {})
    audience_keywords = dict(merged.get("audience_keywords", {}))
    audience_keywords["profile_industry"] = unique_list(context.industry_keywords + context.product_lines)
    audience_keywords["profile_users"] = unique_list(context.target_users)
    audience_keywords["profile_use_cases"] = unique_list(context.use_cases)
    merged["audience_keywords"] = {key: value for key, value in audience_keywords.items() if value}

    content_fit = list(merged.get("content_fit_keywords", []))
    content_fit.extend(context.product_lines)
    content_fit.extend(context.use_cases)
    merged["content_fit_keywords"] = unique_list(content_fit)
    merged["competitor_reference_terms"] = _reference_terms(context.competitor_reference_sites)
    return merged


def profile_summary_text(context: ProfileContext) -> str:
    parts = []
    if context.product_name:
        parts.append(context.product_name)
    if context.product_website:
        parts.append(context.product_website)
    if context.target_users:
        parts.append("Target users: " + ", ".join(context.target_users[:8]))
    if context.industry_keywords:
        parts.append("Topics: " + ", ".join(context.industry_keywords[:12]))
    return " | ".join(parts)


def _parse_sections(text: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}
    current = ""
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(line)
    return sections


def _section_items(sections: Dict[str, List[str]], name: str) -> List[str]:
    lines = sections.get(name, [])
    items: List[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(_clean_item(stripped[2:]))
    return unique_list([item for item in items if item])


def _infer_product_name(text: str, context: ProfileContext) -> str:
    match = re.search(r"^([A-Za-z0-9][^\n。]{2,80}?)\s+helps?\s+", text, flags=re.MULTILINE | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"([A-Za-z][A-Za-z0-9 ]{1,60}?\s+(?:API|Platform|Tool|Suite))\s+帮助", text)
    if match:
        return match.group(1).strip()
    if context.product_lines:
        return context.product_lines[0]
    return ""


def _extract_url(text: str) -> str:
    match = re.search(r"https?://[^\s)]+", text)
    return match.group(0).strip() if match else ""


def _clean_item(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip(" -。.;；"))


def _reference_terms(values: Iterable[str]) -> List[str]:
    terms: List[str] = []
    for value in values:
        clean = _clean_item(value).lower()
        if not clean:
            continue
        terms.append(clean)
        match = re.search(r"https?://(?:www\.)?([^/\s)]+)", clean)
        if match:
            domain = match.group(1).strip()
            terms.append(domain)
            terms.append(domain.split(".")[0])
    return unique_list([term for term in terms if term])
