"""Claude AI ranker — picks the top 10 items and summarizes them."""

import json
import anthropic


def rank_and_summarize(items: list[dict], config: dict, api_key: str) -> list[dict]:
    """Send all fetched items to Claude and get back the top 10 ranked and summarized."""
    weights = config.get("limits", {}).get("weights", {})
    max_items = config.get("limits", {}).get("max_items", 10)
    name = config.get("profile", {}).get("name", "User")
    interests = config.get("interests", {})

    items_text = json.dumps(items, indent=2, default=str)

    prompt = f"""You are a personal briefing assistant for {name}.

Their interests:
- News topics: {interests.get('news_topics', [])}
- Stock watchlist: {interests.get('stocks', [])}
- Job keywords: {interests.get('job_keywords', [])}
- Tech tags: {interests.get('tech_tags', [])}

Category weights (higher = more slots): {json.dumps(weights)}

Here are {len(items)} raw items collected today:

{items_text}

Your task:
1. Pick exactly {max_items} items that are most valuable, interesting, and actionable for {name}.
2. Respect the category weights — allocate roughly proportional slots to each category.
3. For each selected item, write a concise 1-2 sentence summary that captures why it matters.
4. For stock items, include the price movement and a brief explanation if notable.
5. For job items, include company, salary range if available, and key requirements.

Return ONLY a JSON array of exactly {max_items} objects, each with these fields:
- "rank": 1-{max_items}
- "category": "news" | "stocks" | "jobs" | "tech" | "knowledge"
- "emoji": a single relevant emoji for the category
- "title": concise title (max 80 chars)
- "summary": 1-2 sentence summary
- "url": the original URL
- "source": source name

Return valid JSON only, no markdown fences."""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()
    # Handle potential markdown fences in response
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    return json.loads(response_text)
