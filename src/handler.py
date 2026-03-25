"""
AWS Lambda handler — Daily Briefing orchestrator.

Scheduled via EventBridge: cron(30 7 * * ? *) = 9:30 AM CEST (UTC+2)
Fetches news via Tavily, synthesizes with Claude, delivers to Telegram.
"""

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import boto3

from searcher import TavilySearcher
from synthesizer import ClaudeSynthesizer
from telegram_sender import TelegramBot
from topics import TOPICS

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = os.environ.get("AWS_REGION_NAME", "us-east-1")


def _get_secret(client, secret_id: str) -> str:
    return client.get_secret_value(SecretId=secret_id)["SecretString"]


def get_secrets() -> dict:
    client = boto3.client("secretsmanager", region_name=REGION)

    # Claude API key is stored as a raw string
    claude_api_key = _get_secret(client, "invoice-tracker/anthropic-api-key").strip()

    # Daily briefing secrets: Telegram + optional Tavily
    briefing = json.loads(_get_secret(client, "daily-briefing"))

    return {
        "claude_api_key": claude_api_key,
        "telegram_token": briefing["telegram_token"],
        "telegram_chat_id": briefing["telegram_chat_id"],
        "tavily_api_key": briefing.get("tavily_api_key", ""),
    }


def process_topic(topic: dict, searcher: TavilySearcher, synthesizer: ClaudeSynthesizer, date: str):
    """Fetch and format a single topic. Returns (topic_id, message, error)."""
    try:
        search_results = searcher.search_topic(topic)
        message = synthesizer.format_topic(topic, search_results, date)
        logger.info(f"[{topic['id']}] done — {len(search_results)} search results")
        return topic["id"], message, None
    except Exception as e:
        logger.error(f"[{topic['id']}] failed: {e}")
        return topic["id"], None, str(e)


def lambda_handler(event, context):
    logger.info("Daily briefing starting")
    start = time.time()

    secrets = get_secrets()

    searcher = TavilySearcher(secrets["tavily_api_key"])
    synthesizer = ClaudeSynthesizer(secrets["claude_api_key"])
    bot = TelegramBot(secrets["telegram_token"], secrets["telegram_chat_id"])

    today = datetime.utcnow().strftime("%B %d, %Y")

    # Opening message
    bot.send(
        f"<b>📰 Daily Briefing — {today}</b>\n\n"
        "Good morning! ☕ Your intelligence update is ready.\n\n"
        f"<i>Sections: {len(TOPICS)} topics</i>",
    )
    time.sleep(1)

    # Process all topics in parallel (max 4 workers to stay within Lambda concurrency)
    results: dict = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(process_topic, topic, searcher, synthesizer, today): topic["id"]
            for topic in TOPICS
        }
        for future in as_completed(futures):
            topic_id, message, error = future.result()
            results[topic_id] = (message, error)

    # Send in defined topic order with a short delay between messages
    for topic in TOPICS:
        message, error = results.get(topic["id"], (None, "Not processed"))
        if message:
            bot.send(message)
        else:
            bot.send(
                f"<b>⚠️ {topic['emoji']} {topic['title']}</b>\n"
                f"Could not load section today. ({error or 'unknown error'})"
            )
        time.sleep(1)

    elapsed = round(time.time() - start, 1)
    logger.info(f"Daily briefing complete in {elapsed}s")

    return {"status": "success", "date": today, "elapsed_seconds": elapsed}
