from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, Iterable, List

CSV_FIELDS = [
    "rank",
    "channel_type",
    "platform",
    "name",
    "url",
    "topic",
    "audience",
    "subscribers_or_followers",
    "avg_views",
    "recent_activity",
    "fit_score",
    "priority",
    "review_status",
    "review_notes",
    "source_provider",
    "source_providers",
    "source_keyword",
    "source_url",
    "discovery_query",
    "confidence",
    "contact_email",
    "contact_page",
    "sponsor_page",
    "media_kit_url",
    "score_reason",
    "recommended_collaboration",
    "missing_fields",
    "notes",
]


def export_candidates_csv(path: Path, candidates: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    for idx, candidate in enumerate(candidates, start=1):
        row = {field: candidate.get(field, "Unknown") for field in CSV_FIELDS}
        row["rank"] = candidate.get("rank", idx)
        if isinstance(row.get("missing_fields"), list):
            row["missing_fields"] = ", ".join(row["missing_fields"])
        if isinstance(row.get("source_providers"), list):
            row["source_providers"] = ", ".join(row["source_providers"])
        rows.append(row)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
