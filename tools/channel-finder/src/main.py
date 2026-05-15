from __future__ import annotations

import argparse
import importlib.util
import logging
import os
import socket
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from dotenv import load_dotenv
except Exception:  # noqa: BLE001
    def load_dotenv(*_args: Any, **_kwargs: Any) -> bool:
        return False

# Allow running as `python src/main.py` from tools/channel-finder.
CURRENT_DIR = Path(__file__).resolve().parent
TOOL_DIR = CURRENT_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from src.export.data_store import build_review_queue, dedupe_candidates, select_top_candidates, update_master
from src.export.export_csv import export_candidates_csv
from src.export.html_report import generate_html_report
from src.profile_context import build_profile_keywords, find_profile_path, load_profile_context, merge_profile_into_scoring_rules, profile_summary_text
from src.score.channel_scorer import ChannelScorer
from src.utils import guess_workspace_root, load_yaml, slugify, unique_list, utc_now_iso, write_json

LOGGER = logging.getLogger("channel-finder")

CORE_DEPENDENCIES = {
    "requests": "requests>=2.31.0",
    "yaml": "PyYAML>=6.0.1",
    "bs4": "beautifulsoup4>=4.12.3",
}

OPTIONAL_PROVIDER_DEPENDENCIES = {
    "ddgs": ("ddgs", "ddgs>=9.0.0"),
    "ytdlp": ("yt_dlp", "yt-dlp>=2025.1.15"),
}

PROVIDER_HOSTS = {
    "ytdlp": "www.youtube.com",
    "github": "api.github.com",
    "youtube_api": "www.googleapis.com",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MACG Channel Discovery Finder")
    parser.add_argument("--campaign-slug", default="", help="Campaign slug, e.g. profile-channel-discovery")
    parser.add_argument("--keywords", default="", help="Comma-separated keywords. If omitted, config/keywords.yaml is used.")
    parser.add_argument("--profile-path", default="", help="Path to profile.md. Defaults to nearest profile.md found in parent directories.")
    parser.add_argument("--product-name", default="", help="Optional product/campaign name. Defaults to profile or config.")
    parser.add_argument("--channel-types", default="", help="Comma-separated channel types: youtube,newsletter,technical_blog")
    parser.add_argument("--providers", default="", help="Comma-separated providers: auto,manual,seed,ddgs,ytdlp,github,serp,youtube_api")
    parser.add_argument("--workspace-root", default="", help="Path to MACG workspaces directory. Defaults to ../../workspaces.")
    parser.add_argument("--config-dir", default="", help="Path to config directory. Defaults to tools/channel-finder/config.")
    parser.add_argument("--max-results-per-keyword", type=int, default=10, help="Max search results per keyword for API discovery.")
    parser.add_argument("--selected-count", type=int, default=50, help="Number of candidates to show in HTML.")
    parser.add_argument("--recent-days", type=int, default=120, help="Recent activity scoring window.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


def setup_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level), format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def preflight_core_dependencies() -> List[Dict[str, str]]:
    missing: List[Dict[str, str]] = []
    for module_name, requirement in CORE_DEPENDENCIES.items():
        if importlib.util.find_spec(module_name) is None:
            missing.append({"module": module_name, "requirement": requirement})
    return missing


def print_dependency_error(missing: List[Dict[str, str]]) -> None:
    print("Channel Finder cannot start because required Python dependencies are missing.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Missing:", file=sys.stderr)
    for item in missing:
        print(f"- {item['requirement']} (module: {item['module']})", file=sys.stderr)
    print("", file=sys.stderr)
    print("Install from tools/channel-finder:", file=sys.stderr)
    print("  python -m venv .venv", file=sys.stderr)
    print("  source .venv/bin/activate", file=sys.stderr)
    print("  pip install -r requirements.txt", file=sys.stderr)
    print("", file=sys.stderr)
    print("If PyPI certificate verification fails on this machine, retry with:", file=sys.stderr)
    print("  pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt", file=sys.stderr)
    print("", file=sys.stderr)
    print("You can also use a trusted mirror configured for your environment.", file=sys.stderr)


def normalize_candidate_defaults(candidate: Dict[str, Any], run_id: str) -> Dict[str, Any]:
    defaults = {
        "channel_type": "Unknown",
        "platform": "Unknown",
        "platform_id": "",
        "name": "Unknown",
        "url": "Unknown",
        "canonical_url": candidate.get("url") or "Unknown",
        "domain": "Unknown",
        "topic": "Unknown",
        "audience": "Unknown",
        "subscribers_or_followers": "Unknown",
        "avg_views": "Unknown",
        "recent_activity": "Unknown",
        "contact_email": "Unknown",
        "contact_page": "Unknown",
        "sponsor_page": "Unknown",
        "media_kit_url": "Unknown",
        "source_keyword": "Unknown",
        "notes": "",
        "source_run_id": run_id,
        "source_provider": "Unknown",
        "source_url": candidate.get("url") or "Unknown",
        "discovery_query": candidate.get("source_keyword") or "Unknown",
        "confidence": "low",
        "review_status": "new",
        "review_notes": "",
    }
    merged = {**defaults, **candidate}
    for key, value in list(merged.items()):
        if value is None or value == "":
            merged[key] = "Unknown"
    return merged


def main() -> int:
    args = parse_args()
    setup_logging(args.log_level)
    load_dotenv(TOOL_DIR / ".env")

    missing_core = preflight_core_dependencies()
    if missing_core:
        print_dependency_error(missing_core)
        return 2

    from src.crawl.page_crawler import PageCrawler
    from src.discover.ddgs_discover import DDGSDiscoverer
    from src.discover.github_discover import GitHubDiscoverer
    from src.discover.newsletter_discover import NewsletterDiscoverer
    from src.discover.serp_discover import SerpDiscoverer
    from src.discover.youtube_discover import YouTubeDiscoverer
    from src.discover.ytdlp_discover import YtDlpDiscoverer

    config_dir = Path(args.config_dir).resolve() if args.config_dir else TOOL_DIR / "config"
    keyword_config = load_yaml(config_dir / "keywords.yaml")
    source_config = load_yaml(config_dir / "sources.yaml")
    scoring_rules = load_yaml(config_dir / "scoring-rules.yaml")
    profile_path = find_profile_path(TOOL_DIR, args.profile_path)
    profile_context = load_profile_context(profile_path)
    scoring_rules = merge_profile_into_scoring_rules(scoring_rules, profile_context)

    campaign_defaults = keyword_config.get("campaign", {})
    product_name = args.product_name or profile_context.product_name or campaign_defaults.get("product_name") or "Channel Discovery"
    campaign_slug = slugify(args.campaign_slug or campaign_defaults.get("default_slug") or product_name or "channel-discovery")
    generated_at = utc_now_iso()
    configured_keywords = list(keyword_config.get("keywords", []))
    profile_keywords = build_profile_keywords(profile_context)
    keywords: List[str] = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else unique_list(profile_keywords + configured_keywords)
    # Use a readable unique run id to avoid overwriting multiple runs on the same day.
    first_keyword = keywords[0] if keywords else "run"
    timestamp_slug = generated_at.replace("-", "").replace(":", "").replace("T", "-").replace("Z", "")
    run_id = slugify(f"{timestamp_slug}-{first_keyword}")
    channel_types: List[str] = [t.strip() for t in args.channel_types.split(",") if t.strip()] if args.channel_types else list(keyword_config.get("channel_types", []))
    providers, provider_statuses = resolve_provider_plan(args.providers, source_config)
    selected_count = min(max(args.selected_count or campaign_defaults.get("selected_count", 50), 1), 50)
    recent_days = args.recent_days or campaign_defaults.get("recent_days", 120)
    max_raw_candidates = int(campaign_defaults.get("max_raw_candidates", 500) or 500)
    workspace_root = Path(args.workspace_root).resolve() if args.workspace_root else guess_workspace_root(TOOL_DIR)
    campaign_dir = workspace_root / "channel-discovery" / campaign_slug
    data_dir = campaign_dir / "data"
    runs_dir = data_dir / "runs"
    campaign_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    input_config: Dict[str, Any] = {
        "campaign_slug": campaign_slug,
        "product_name": product_name,
        "product_website": profile_context.product_website,
        "profile_path": str(profile_path or ""),
        "profile_summary": profile_summary_text(profile_context),
        "profile_context": profile_context.to_dict(),
        "keywords": keywords,
        "channel_types": channel_types,
        "language": campaign_defaults.get("language", "English"),
        "recent_days": recent_days,
        "max_raw_candidates": max_raw_candidates,
        "selected_count": selected_count,
        "max_results_per_keyword": args.max_results_per_keyword,
        "providers": providers,
    }

    LOGGER.info("Starting channel discovery: campaign=%s run=%s", campaign_slug, run_id)
    raw_candidates: List[Dict[str, Any]] = []

    user_agent = source_config.get("user_agent", "MACG-ChannelFinder/1.0")
    crawl_config = source_config.get("crawl", {})
    crawler = PageCrawler(
        user_agent=user_agent,
        timeout=int(source_config.get("request_timeout_seconds", crawl_config.get("request_timeout_seconds", 20))),
        request_delay_seconds=float(source_config.get("request_delay_seconds", crawl_config.get("request_delay_seconds", 1.2))),
        obey_robots_txt=bool(crawl_config.get("obey_robots_txt", True)),
    )
    newsletter = NewsletterDiscoverer(crawler, max_links_per_seed=int(crawl_config.get("max_links_per_seed", 12)))

    def run_provider(name: str, fn: Any) -> None:
        nonlocal raw_candidates
        if len(raw_candidates) >= max_raw_candidates:
            provider_statuses.append(provider_status(name, "skipped", skipped_reason="max_raw_candidates_reached"))
            return
        before = len(raw_candidates)
        try:
            rows = fn()
            if rows:
                raw_candidates.extend(rows)
                raw_candidates = raw_candidates[:max_raw_candidates]
            count = len(raw_candidates) - before
            provider_statuses.append(provider_status(name, "ok", count=count))
            LOGGER.info("Provider %s returned %s candidates", name, count)
        except Exception as exc:  # noqa: BLE001
            provider_statuses.append(provider_status(name, "failed", error=str(exc)))
            LOGGER.warning("Provider %s failed: %s", name, exc)

    if "manual" in providers:
        manual_seeds = source_config.get("manual_seed_candidates", [])
        if not manual_seeds and source_config.get("demo_mode", False):
            manual_seeds = source_config.get("demo_seed_candidates", [])
        if manual_seeds:
            run_provider("manual", lambda: newsletter.from_manual_seeds(manual_seeds))
        else:
            provider_statuses.append(provider_status("manual", "skipped", skipped_reason="no_manual_seeds_enable_demo_mode_or_add_manual_seed_candidates"))

    if "seed" in providers:
        if "newsletter" in channel_types:
            run_provider("seed_newsletter", lambda: newsletter.discover_from_seed_urls(source_config.get("newsletter_seed_urls", []), channel_type="Newsletter"))
        if "technical_blog" in channel_types:
            run_provider("seed_technical_blog", lambda: newsletter.discover_from_seed_urls(source_config.get("technical_blog_seed_urls", []), channel_type="Technical Blog"))

    if "ddgs" in providers:
        ddgs_config = source_config.get("ddgs", {})
        ddgs = DDGSDiscoverer(
            max_results_per_keyword=int(ddgs_config.get("max_results_per_keyword", args.max_results_per_keyword)),
            region=str(ddgs_config.get("region", "us-en")),
            safesearch=str(ddgs_config.get("safesearch", "moderate")),
        )
        run_provider("ddgs", lambda: ddgs.discover(keywords))

    if "ytdlp" in providers and "youtube" in channel_types:
        ytdlp_config = source_config.get("ytdlp", {})
        ytdlp = YtDlpDiscoverer(max_results_per_keyword=int(ytdlp_config.get("max_results_per_keyword", args.max_results_per_keyword)))
        run_provider("ytdlp", lambda: ytdlp.discover(keywords))

    if "github" in providers:
        github_config = source_config.get("github", {})
        github = GitHubDiscoverer(
            max_results_per_keyword=int(github_config.get("max_results_per_keyword", min(args.max_results_per_keyword, 10))),
            timeout=int(github_config.get("request_timeout_seconds", 20)),
        )
        run_provider("github", lambda: github.discover(keywords))

    if "serp" in providers and "technical_blog" in channel_types:
        serp = SerpDiscoverer(source_config.get("serp_api_url_template", ""), max_results_per_keyword=args.max_results_per_keyword)
        run_provider("serp", lambda: serp.discover(keywords))

    if "youtube_api" in providers and "youtube" in channel_types:
        youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")
        yt = YouTubeDiscoverer(api_key=youtube_api_key, max_results_per_keyword=args.max_results_per_keyword)
        run_provider("youtube_api", lambda: yt.discover(keywords))

    normalized_candidates = [normalize_candidate_defaults(c, run_id) for c in raw_candidates]
    normalized_candidates = dedupe_candidates(normalized_candidates)

    scorer = ChannelScorer(scoring_rules, recent_days=recent_days, product_name=product_name)
    scored_candidates = [scorer.score(c) for c in normalized_candidates]
    selected_50 = select_top_candidates(scored_candidates, limit=selected_count)
    review_queue = build_review_queue(selected_50)

    master = update_master(data_dir / "master-candidates.json", scored_candidates, run_id=run_id)

    summary = {
        "raw_count": len(raw_candidates),
        "normalized_count": len(normalized_candidates),
        "scored_count": len(scored_candidates),
        "selected_count": len(selected_50),
        "master_count": len(master),
        "high_priority_count": sum(1 for c in selected_50 if c.get("priority") == "High"),
        "medium_priority_count": sum(1 for c in selected_50 if c.get("priority") == "Medium"),
        "low_priority_count": sum(1 for c in selected_50 if c.get("priority") == "Low"),
        "contact_available_count": sum(1 for c in selected_50 if c.get("contact_email") not in (None, "", "Unknown") or c.get("contact_page") not in (None, "", "Unknown")),
        "sponsor_page_found_count": sum(1 for c in selected_50 if c.get("sponsor_page") not in (None, "", "Unknown") or c.get("media_kit_url") not in (None, "", "Unknown")),
        "provider_statuses": provider_statuses,
        "warnings": build_run_warnings(selected_count, selected_50, provider_statuses),
    }

    run_payload = {
        "run_id": run_id,
        "campaign": campaign_slug,
        "generated_at": generated_at,
        "input": input_config,
        "raw_candidates": raw_candidates,
        "normalized_candidates": normalized_candidates,
        "scored_candidates": scored_candidates,
        "selected_50": selected_50,
        "review_queue": review_queue,
        "summary": summary,
    }

    write_json(runs_dir / f"{run_id}.json", run_payload)
    write_json(data_dir / "selected-50.json", selected_50)
    write_json(data_dir / "review-queue.json", review_queue)
    export_candidates_csv(data_dir / "selected-50.csv", selected_50)
    generate_html_report(campaign_dir / "index.html", campaign_slug, run_id, generated_at, input_config, selected_50, summary)

    LOGGER.info("Done. Open report: %s", campaign_dir / "index.html")
    LOGGER.info("Selected candidates: %s", len(selected_50))
    if not raw_candidates:
        LOGGER.warning("No raw candidates found. Check network access, free discovery dependencies, seed URLs, or manual_seed_candidates.")
    return 0


def provider_status(
    provider: str,
    status: str,
    count: int = 0,
    error: str = "",
    skipped_reason: str = "",
    dependency_missing: str = "",
    config_disabled: bool = False,
    missing_api_key: bool = False,
) -> Dict[str, Any]:
    return {
        "provider": provider,
        "status": status,
        "count": count,
        "error": error,
        "skipped_reason": skipped_reason,
        "dependency_missing": dependency_missing,
        "config_disabled": config_disabled,
        "missing_api_key": missing_api_key,
    }


def resolve_provider_plan(provider_arg: str, source_config: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
    configured = source_config.get("free_discovery", {}).get("providers", [])
    raw = [p.strip() for p in provider_arg.split(",") if p.strip()] if provider_arg else list(configured or ["auto"])
    statuses: List[Dict[str, Any]] = []
    if not raw or "auto" in raw:
        raw = ["manual", "seed", "ddgs", "ytdlp", "github", "serp", "youtube_api"]
    aliases = {"youtube": "youtube_api", "youtube_data_api": "youtube_api"}
    providers: List[str] = []
    for provider in raw:
        normalized = aliases.get(provider, provider)
        if normalized in {"manual", "seed"}:
            if normalized not in providers:
                providers.append(normalized)
            continue
        if normalized in {"ddgs", "ytdlp", "github"} and not provider_config_enabled(source_config, normalized):
            statuses.append(provider_status(normalized, "skipped", skipped_reason="config_disabled", config_disabled=True))
            continue
        if normalized in OPTIONAL_PROVIDER_DEPENDENCIES:
            module_name, requirement = OPTIONAL_PROVIDER_DEPENDENCIES[normalized]
            if importlib.util.find_spec(module_name) is None:
                statuses.append(provider_status(normalized, "skipped", skipped_reason="dependency_missing", dependency_missing=requirement))
                continue
        if normalized == "serp" and not source_config.get("serp_api_url_template"):
            statuses.append(provider_status(normalized, "skipped", skipped_reason="missing_serp_api_url_template"))
            continue
        if normalized == "youtube_api" and not os.getenv("YOUTUBE_API_KEY"):
            statuses.append(provider_status(normalized, "skipped", skipped_reason="missing_api_key", missing_api_key=True))
            continue
        host = PROVIDER_HOSTS.get(normalized)
        if host and not host_resolves(host):
            statuses.append(provider_status(normalized, "skipped", skipped_reason=f"network_unavailable:{host}"))
            continue
        if normalized not in providers:
            providers.append(normalized)
    return providers, statuses


def provider_config_enabled(source_config: Dict[str, Any], provider: str) -> bool:
    config = source_config.get(provider, {})
    if not isinstance(config, dict):
        return True
    return bool(config.get("enabled", True))


def host_resolves(host: str) -> bool:
    try:
        socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        return True
    except OSError:
        return False


def build_run_warnings(requested_count: int, selected: List[Dict[str, Any]], provider_statuses: List[Dict[str, Any]]) -> List[str]:
    warnings: List[str] = []
    selected_count = len(selected)
    if selected_count < requested_count:
        warnings.append(f"Selected {selected_count} candidates, below requested {requested_count}.")
    skipped = [s for s in provider_statuses if s.get("status") == "skipped"]
    failed = [s for s in provider_statuses if s.get("status") == "failed"]
    if skipped:
        warnings.append("Some providers were skipped. Check provider_statuses for dependency, config, API key, or template reasons.")
    if failed:
        warnings.append("Some providers failed during discovery. Check provider_statuses errors.")
    if selected_count < requested_count:
        warnings.append("Try enabling more providers, adding manual seeds, lowering filters, or increasing max-results-per-keyword.")
    return warnings


if __name__ == "__main__":
    raise SystemExit(main())
