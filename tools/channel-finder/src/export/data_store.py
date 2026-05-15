from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from src.utils import canonical_candidate_key, merge_missing, read_json, unique_list, utc_now_iso, write_json


def dedupe_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Dict[str, Dict[str, Any]] = {}
    for candidate in candidates:
        key = canonical_candidate_key(candidate)
        candidate["dedupe_key"] = key
        candidate.setdefault("review_status", "new")
        candidate.setdefault("review_notes", "")
        candidate.setdefault("source_providers", _as_list(candidate.get("source_provider")))
        candidate.setdefault("source_keywords", _as_list(candidate.get("source_keyword")))
        existing = seen.get(key)
        if not existing:
            seen[key] = candidate
            continue
        seen[key] = merge_candidate_records(existing, candidate)
    return list(seen.values())


def merge_candidate_records(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    existing_score = int(existing.get("fit_score") or 0)
    incoming_score = int(incoming.get("fit_score") or 0)
    base = dict(incoming) if incoming_score > existing_score else dict(existing)
    other = existing if incoming_score > existing_score else incoming
    merge_missing(base, other)

    source_providers = _as_list(existing.get("source_providers")) + _as_list(existing.get("source_provider"))
    source_providers += _as_list(incoming.get("source_providers")) + _as_list(incoming.get("source_provider"))
    source_keywords = _as_list(existing.get("source_keywords")) + _as_list(existing.get("source_keyword"))
    source_keywords += _as_list(incoming.get("source_keywords")) + _as_list(incoming.get("source_keyword"))
    base["source_providers"] = unique_list(source_providers)
    base["source_keywords"] = unique_list(source_keywords)
    base["source_provider"] = ", ".join(base["source_providers"]) or base.get("source_provider", "Unknown")
    base["source_keyword"] = ", ".join(base["source_keywords"]) or base.get("source_keyword", "Unknown")
    base["review_status"] = existing.get("review_status") or incoming.get("review_status") or "new"
    base["review_notes"] = existing.get("review_notes") or incoming.get("review_notes") or ""
    if existing.get("notes") and incoming.get("notes") and existing.get("notes") != incoming.get("notes"):
        base["notes"] = f"{existing.get('notes')}; {incoming.get('notes')}"
    return base


def update_master(master_path: Path, scored_candidates: List[Dict[str, Any]], run_id: str) -> List[Dict[str, Any]]:
    now = utc_now_iso()
    existing = read_json(master_path, default=[])
    if not isinstance(existing, list):
        existing = []
    master_by_key: Dict[str, Dict[str, Any]] = {}
    for item in existing:
        key = item.get("dedupe_key") or canonical_candidate_key(item)
        item["dedupe_key"] = key
        master_by_key[key] = item

    for candidate in scored_candidates:
        key = candidate.get("dedupe_key") or canonical_candidate_key(candidate)
        candidate["dedupe_key"] = key
        score = int(candidate.get("fit_score") or 0)
        if key not in master_by_key:
            record = dict(candidate)
            record.update({
                "first_seen_run_id": run_id,
                "last_seen_run_id": run_id,
                "first_seen_at": now,
                "last_seen_at": now,
                "seen_count": 1,
                "last_score": score,
                "best_score": score,
                "status": candidate.get("status", "new"),
                "review_status": candidate.get("review_status", "new"),
                "review_notes": candidate.get("review_notes", ""),
            })
            master_by_key[key] = record
        else:
            record = master_by_key[key]
            previous_review_status = record.get("review_status") or record.get("status") or "new"
            previous_review_notes = record.get("review_notes") or ""
            merged = merge_candidate_records(record, candidate)
            record.clear()
            record.update(merged)
            record["last_seen_run_id"] = run_id
            record["last_seen_at"] = now
            record["seen_count"] = int(record.get("seen_count") or 1) + 1
            record["last_score"] = score
            record["best_score"] = max(int(record.get("best_score") or 0), score)
            record["review_status"] = previous_review_status
            record["review_notes"] = previous_review_notes
            # Preserve user-maintained fields such as status/notes, but fill missing metadata.
            for field in [
                "contact_email", "contact_page", "sponsor_page", "media_kit_url",
                "subscribers_or_followers", "avg_views", "recent_activity", "topic", "audience",
            ]:
                if record.get(field) in (None, "", "Unknown") and candidate.get(field) not in (None, "", "Unknown"):
                    record[field] = candidate[field]
            if score >= int(record.get("fit_score") or 0):
                for field in ["fit_score", "priority", "score_breakdown", "score_reason", "recommended_collaboration"]:
                    record[field] = candidate.get(field)

    master = list(master_by_key.values())
    master.sort(key=lambda row: (int(row.get("best_score") or row.get("fit_score") or 0), int(row.get("seen_count") or 0)), reverse=True)
    write_json(master_path, master)
    return master


def select_top_candidates(scored_candidates: List[Dict[str, Any]], limit: int = 50) -> List[Dict[str, Any]]:
    deduped = dedupe_candidates(scored_candidates)
    deduped.sort(
        key=lambda c: (
            int(c.get("fit_score") or 0),
            1 if c.get("contact_email") not in (None, "", "Unknown") else 0,
            1 if c.get("contact_page") not in (None, "", "Unknown") else 0,
            1 if c.get("sponsor_page") not in (None, "", "Unknown") else 0,
        ),
        reverse=True,
    )
    selected = deduped[:limit]
    for idx, candidate in enumerate(selected, start=1):
        candidate["rank"] = idx
        candidate.setdefault("review_status", "new")
        candidate.setdefault("review_notes", "")
    return selected


def build_review_queue(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    queue: List[Dict[str, Any]] = []
    for candidate in candidates:
        item = dict(candidate)
        item.setdefault("review_status", "new")
        item.setdefault("review_notes", "")
        item["review_focus"] = _review_focus(item)
        queue.append(item)
    return queue


def _review_focus(candidate: Dict[str, Any]) -> List[str]:
    focus: List[str] = []
    if candidate.get("priority") == "High":
        focus.append("Validate priority fit before outreach")
    if candidate.get("contact_email") in (None, "", "Unknown") and candidate.get("contact_page") in (None, "", "Unknown"):
        focus.append("Find public contact path")
    if candidate.get("sponsor_page") in (None, "", "Unknown") and candidate.get("media_kit_url") in (None, "", "Unknown"):
        focus.append("Check sponsorship or partnership page")
    if candidate.get("subscribers_or_followers") in (None, "", "Unknown") and candidate.get("avg_views") in (None, "", "Unknown"):
        focus.append("Validate audience size manually")
    return focus or ["Manual validation"]


def _as_list(value: Any) -> List[str]:
    if value in (None, "", "Unknown"):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "", "Unknown")]
    return [part.strip() for part in str(value).split(",") if part.strip()]
