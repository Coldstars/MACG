from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from src.utils import contains_any, flatten_text, parse_int, utc_now_iso


class ChannelScorer:
    def __init__(self, scoring_rules: Dict[str, Any], recent_days: int = 120, product_name: str = "the product"):
        self.rules = scoring_rules or {}
        self.weights = self.rules.get("weights", {})
        self.thresholds = self.rules.get("priority_thresholds", {"high": 80, "medium": 60})
        self.recent_days = recent_days
        self.product_name = product_name or "the product"

    def score(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        text = flatten_text(
            candidate.get("name"),
            candidate.get("topic"),
            candidate.get("audience"),
            candidate.get("description_excerpt"),
            " ".join(candidate.get("recent_titles") or []),
            candidate.get("source_keyword"),
        )
        breakdown = {
            "audience_match": self._audience_score(text),
            "content_fit": self._content_fit_score(text),
            "activity": self._activity_score(candidate.get("recent_activity")),
            "sponsorship_readiness": self._sponsor_score(candidate),
            "contactability": self._contact_score(candidate),
            "authority_reach": self._reach_score(candidate),
            "long_term_search_value": self._long_term_score(text),
        }
        total = sum(breakdown.values())
        competitor_terms = self.rules.get("competitor_reference_terms", [])
        is_competitor_reference = contains_any(
            flatten_text(candidate.get("name"), candidate.get("url"), candidate.get("canonical_url"), candidate.get("domain")),
            competitor_terms,
        )
        if is_competitor_reference:
            total = min(total, 35)
        priority = self._priority(total)
        result = dict(candidate)
        result["score_breakdown"] = breakdown
        result["fit_score"] = total
        result["priority"] = priority
        result["estimated_priority"] = priority
        result["score_reason"] = self._score_reason(result, text)
        result["recommended_collaboration"] = self._recommend_collaboration(text)
        result["missing_fields"] = self._missing_fields(result)
        result.setdefault("notes", "")
        if is_competitor_reference:
            existing_notes = result.get("notes")
            suffix = "命中 profile 中的竞品/参考站；建议用于竞品观察，不默认作为 outreach 候选。"
            result["notes"] = f"{existing_notes}; {suffix}" if existing_notes and existing_notes != "Unknown" else suffix
            result["review_notes"] = suffix
        return result

    def _audience_score(self, text: str) -> int:
        max_score = int(self.weights.get("audience_match", 30))
        audience_keywords = self.rules.get("audience_keywords", {})
        matched_groups = 0
        for keywords in audience_keywords.values():
            if contains_any(text, keywords):
                matched_groups += 1
        if matched_groups >= 3:
            return max_score
        if matched_groups == 2:
            return int(max_score * 0.8)
        if matched_groups == 1:
            return int(max_score * 0.55)
        return int(max_score * 0.2)

    def _content_fit_score(self, text: str) -> int:
        max_score = int(self.weights.get("content_fit", 20))
        keywords = self.rules.get("content_fit_keywords", [])
        hit_count = sum(1 for kw in keywords if kw.lower() in text.lower())
        if hit_count >= 3:
            return max_score
        if hit_count == 2:
            return int(max_score * 0.75)
        if hit_count == 1:
            return int(max_score * 0.5)
        return int(max_score * 0.25)

    def _activity_score(self, recent_activity: Any) -> int:
        max_score = int(self.weights.get("activity", 15))
        text = str(recent_activity or "")
        if not text or text == "Unknown":
            return int(max_score * 0.35)
        try:
            # Supports YouTube ISO timestamps like 2026-05-13T00:00:00Z.
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            days = (datetime.now(timezone.utc) - dt).days
            if days <= 30:
                return max_score
            if days <= self.recent_days:
                return int(max_score * 0.8)
            if days <= 365:
                return int(max_score * 0.45)
            return int(max_score * 0.2)
        except ValueError:
            lowered = text.lower()
            if any(token in lowered for token in ["day", "week", "month", "active"]):
                return int(max_score * 0.75)
            return int(max_score * 0.35)

    def _sponsor_score(self, candidate: Dict[str, Any]) -> int:
        max_score = int(self.weights.get("sponsorship_readiness", 10))
        if candidate.get("sponsor_page") not in (None, "", "Unknown"):
            return max_score
        if candidate.get("media_kit_url") not in (None, "", "Unknown"):
            return max_score
        text = flatten_text(candidate.get("topic"), candidate.get("description_excerpt"), candidate.get("notes"))
        sponsor_keywords = self.rules.get("sponsor_keywords", [])
        if contains_any(text, sponsor_keywords):
            return int(max_score * 0.7)
        return int(max_score * 0.25)

    def _contact_score(self, candidate: Dict[str, Any]) -> int:
        max_score = int(self.weights.get("contactability", 10))
        if candidate.get("contact_email") not in (None, "", "Unknown"):
            return max_score
        if candidate.get("contact_page") not in (None, "", "Unknown"):
            return int(max_score * 0.8)
        if candidate.get("url") not in (None, "", "Unknown"):
            return int(max_score * 0.35)
        return 0

    def _reach_score(self, candidate: Dict[str, Any]) -> int:
        max_score = int(self.weights.get("authority_reach", 10))
        subs = parse_int(candidate.get("subscribers_or_followers")) or 0
        avg_views = parse_int(candidate.get("avg_views")) or 0
        value = max(subs, avg_views * 5)
        if value >= 500_000:
            return max_score
        if value >= 100_000:
            return int(max_score * 0.85)
        if value >= 20_000:
            return int(max_score * 0.65)
        if value >= 5_000:
            return int(max_score * 0.45)
        if value > 0:
            return int(max_score * 0.25)
        return int(max_score * 0.2)

    def _long_term_score(self, text: str) -> int:
        max_score = int(self.weights.get("long_term_search_value", 5))
        long_term_terms = ["tutorial", "guide", "how to", "build", "template", "workflow", "python", "seo", "langchain", "rag"]
        if contains_any(text, long_term_terms):
            return max_score
        return int(max_score * 0.4)

    def _priority(self, score: int) -> str:
        if score >= int(self.thresholds.get("high", 80)):
            return "High"
        if score >= int(self.thresholds.get("medium", 60)):
            return "Medium"
        return "Low"

    def _score_reason(self, candidate: Dict[str, Any], text: str) -> str:
        reasons: List[str] = []
        if contains_any(text, ["ai agent", "langchain", "llamaindex", "rag", "llm"]):
            reasons.append("匹配 AI Agent / LLM 工作流主题")
        if contains_any(text, ["python", "web scraping", "api", "developer"]):
            reasons.append("匹配开发者和数据 API 受众")
        if contains_any(text, ["seo", "rank tracking", "serp", "google search"]):
            reasons.append("匹配 SEO 和搜索数据场景")
        if candidate.get("contact_email") not in (None, "", "Unknown") or candidate.get("contact_page") not in (None, "", "Unknown"):
            reasons.append("有公开联系路径")
        if candidate.get("sponsor_page") not in (None, "", "Unknown") or candidate.get("media_kit_url") not in (None, "", "Unknown"):
            reasons.append("有赞助页或 media kit 信号")
        if not reasons:
            reasons.append("有一定相关性，需要人工确认")
        return "；".join(reasons) + "。"

    def _recommend_collaboration(self, text: str) -> str:
        templates = self.rules.get("collaboration_templates", {})
        lowered = text.lower()
        selected = templates.get("general", "赞助技术教程：介绍 {product_name}。")
        if any(k in lowered for k in ["n8n", "workflow", "automation"]):
            selected = templates.get("n8n") or selected
            return self._format_template(selected)
        if any(k in lowered for k in ["rag", "llamaindex", "retrieval"]):
            selected = templates.get("rag") or selected
            return self._format_template(selected)
        if any(k in lowered for k in ["ai agent", "langchain", "agentic"]):
            selected = templates.get("ai_agent") or selected
            return self._format_template(selected)
        if any(k in lowered for k in ["python", "scraping", "web scraping"]):
            selected = templates.get("python_scraping") or selected
            return self._format_template(selected)
        if any(k in lowered for k in ["seo", "rank", "serp"]):
            selected = templates.get("seo") or selected
            return self._format_template(selected)
        return self._format_template(selected)

    def _format_template(self, template: str) -> str:
        return str(template or "").format(product_name=self.product_name)

    def _missing_fields(self, candidate: Dict[str, Any]) -> List[str]:
        fields = ["contact_email", "contact_page", "sponsor_page", "media_kit_url", "subscribers_or_followers", "avg_views"]
        return [field for field in fields if candidate.get(field) in (None, "", "Unknown")]
