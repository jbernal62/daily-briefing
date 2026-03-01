"""Claude AI ranker — curates and summarizes the daily briefing."""

import json
import anthropic


def rank_and_summarize(items: list[dict], config: dict, api_key: str) -> list[dict]:
    """Send all fetched items to Claude and get back a curated, structured briefing."""
    max_items = config.get("limits", {}).get("max_items", 25)
    name = config.get("profile", {}).get("name", "User")
    interests = config.get("interests", {})

    items_text = json.dumps(items, indent=2, default=str)

    prompt = f"""You are a personal daily briefing assistant for {name}, based in the Netherlands.

CONTENT REQUIREMENTS — you MUST include all of these sections in this exact order:

1. JOBS (exactly 5 items): Remote jobs in NL/Europe for Cloud Architect, DevOps Engineer, Senior Solutions Architect. Include relocation opportunities. Show company, salary, location, and why it's a good fit.

2. ELASTIC (1-2 items): Latest Elasticsearch innovations, tricks, or tips. If nothing recent, include the best available.

3. CLOUD (2-3 items): Latest innovations from AWS, Azure, or GCP. New services, features, or significant updates.

4. CLAUDE CODE TIP (exactly 1 item): Include the Claude Code tip as-is — it's already curated.

5. ETF/MARKET (1-2 items): VWCE (VANG FTSE AW USDA) performance. Include price, daily change, and monthly trend.

6. CRYPTO (1 item): Bitcoin price, 24h change, 7d trend. Add a brief projection or market sentiment note.

7. DUTCH NEWS (exactly 3 items): Top news from the Netherlands. Summarize each in 1-2 sentences.

8. WEATHER (1 item): Best weather spots in Europe today. Include the weather item as-is.

9. POSITIVE NEWS (1-2 items): Uplifting, positive news. Something to start the day well.

Here are {len(items)} raw items collected today:

{items_text}

Your task:
- Select up to {max_items} items following the section requirements above
- For each item write a concise 1-2 sentence summary
- For jobs: include company, salary if available, location, remote/relocation status
- For financial items: include exact numbers and percentages
- For Bitcoin: add a brief 1-sentence market sentiment or projection
- KEEP items in the section order listed above

Return ONLY a JSON array of objects, each with these fields:
- "rank": sequential number
- "category": "jobs" | "elastic" | "cloud" | "claude_tip" | "etf" | "crypto" | "dutch_news" | "weather" | "positive"
- "emoji": a single relevant emoji
- "title": concise title (max 100 chars)
- "summary": 1-2 sentence summary
- "url": the original URL (keep it exactly as provided)
- "source": source name

Return valid JSON only, no markdown fences."""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0]

    return json.loads(response_text)
