"""Lambda handler — orchestrates the daily briefing pipeline (Gemini-powered)."""

import asyncio
import os
from pathlib import Path
import yaml

from src.sources.adzuna import fetch_jobs
from src.sources.elastic import fetch_elastic_news
from src.sources.cloud_news import fetch_cloud_news
from src.sources.claude_tips import get_daily_tip
from src.sources.etf import fetch_etfs
from src.sources.crypto import fetch_crypto
from src.sources.dutch_news import fetch_dutch_news
from src.sources.weather import fetch_weather
from src.sources.positive_news import fetch_positive_news
from src.ranker import rank_and_summarize
from src.telegram import format_briefing_telegram, send_telegram

PROJECT_DIR = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    """Load config from file or environment."""
    config_path = os.environ.get("CONFIG_PATH", str(PROJECT_DIR / "config.yaml"))
    with open(config_path) as f:
        return yaml.safe_load(f)


async def fetch_all_sources(config: dict) -> list[dict]:
    """Fetch from all data sources concurrently."""
    interests = config["interests"]

    gnews_key = os.environ["GNEWS_API_KEY"]
    adzuna_app_id = os.environ["ADZUNA_APP_ID"]
    adzuna_key = os.environ["ADZUNA_API_KEY"]

    async_tasks = [
        # 1. Jobs (NL/EU remote)
        fetch_jobs(
            adzuna_app_id, adzuna_key,
            interests["job_keywords"],
            interests["job_locations"],
            interests["job_tags"],
            max_total=interests.get("jobs_count", 5),
        ),
        # 2. Elasticsearch innovations
        fetch_elastic_news(interests["elastic_tags"]),
        # 3. Cloud innovations
        fetch_cloud_news(interests["cloud_tags"]),
        # 6. Bitcoin
        fetch_crypto(interests["crypto"]),
        # 7. Dutch news
        fetch_dutch_news(interests.get("dutch_news_count", 3)),
        # 8. Weather
        fetch_weather(interests["weather_cities"]),
        # 9. Positive news
        fetch_positive_news(gnews_key),
    ]

    results = await asyncio.gather(*async_tasks, return_exceptions=True)

    # Synchronous fetchers
    # 4. Claude Code tip
    claude_tip = get_daily_tip()
    # 5. ETF data
    etf_items = fetch_etfs(interests["etfs"], interests.get("etf_names", {}))

    all_items = claude_tip + etf_items
    for result in results:
        if isinstance(result, list):
            all_items.extend(result)
        elif isinstance(result, Exception):
            print(f"Source error: {result}")

    return all_items


async def run_pipeline(config: dict) -> dict:
    """Run the full briefing pipeline."""
    # 1. Fetch all sources
    all_items = await fetch_all_sources(config)
    print(f"Fetched {len(all_items)} items from all sources")

    # 2. Rank and summarize with Gemini
    gemini_key = os.environ["GEMINI_API_KEY"]
    ranked = rank_and_summarize(all_items, config, gemini_key)
    print(f"Gemini selected top {len(ranked)} items")

    # 3. Format the message
    name = config["profile"]["name"]
    message = format_briefing_telegram(ranked, name)
    print(f"Message formatted ({len(message)} chars)")

    # 4. Send via Telegram
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if tg_token and tg_chat_id:
        result = await send_telegram(message, tg_token, tg_chat_id)
        print(f"Telegram sent: {result.get('ok')}")
    else:
        print("Telegram not configured - message returned in response body")

    return {"items_fetched": len(all_items), "items_selected": len(ranked), "message_length": len(message), "message": message}


def lambda_handler(event, context):
    """AWS Lambda entry point."""
    config = load_config()
    result = asyncio.run(run_pipeline(config))
    return {"statusCode": 200, "body": result}


if __name__ == "__main__":
    config = load_config()
    result = asyncio.run(run_pipeline(config))
    print(f"\nDone: {result}")
