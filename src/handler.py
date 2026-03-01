"""Lambda handler — orchestrates the daily briefing pipeline."""

import asyncio
import os
from pathlib import Path
import yaml

from src.sources.gnews import fetch_news
from src.sources.stocks import fetch_stocks
from src.sources.hackernews import fetch_hackernews
from src.sources.devto import fetch_devto
from src.sources.adzuna import fetch_jobs
from src.sources.wikipedia import fetch_wikipedia
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
        fetch_news(gnews_key, interests["news_topics"]),
        fetch_hackernews(max_items=10),
        fetch_devto(interests["tech_tags"]),
        fetch_jobs(adzuna_app_id, adzuna_key, interests["job_keywords"], interests["job_location"]),
        fetch_wikipedia(),
    ]

    results = await asyncio.gather(*async_tasks, return_exceptions=True)

    # Stocks is synchronous
    stock_items = fetch_stocks(interests["stocks"])

    all_items = stock_items
    for result in results:
        if isinstance(result, list):
            all_items.extend(result)

    return all_items


async def run_pipeline(config: dict) -> dict:
    """Run the full briefing pipeline."""
    # 1. Fetch all sources
    all_items = await fetch_all_sources(config)
    print(f"Fetched {len(all_items)} items from all sources")

    # 2. Rank and summarize with Claude
    claude_key = os.environ["ANTHROPIC_API_KEY"]
    ranked = rank_and_summarize(all_items, config, claude_key)
    print(f"Claude selected top {len(ranked)} items")

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
