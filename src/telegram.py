"""Telegram Bot API — send the daily briefing message."""

import httpx


def format_briefing_telegram(ranked_items: list[dict], name: str) -> str:
    """Format ranked items as a Telegram message with markdown."""
    lines = [f"Good morning {name}! Here's your *Daily 10:*\n"]

    for item in ranked_items:
        emoji = item.get("emoji", "")
        rank = item.get("rank", "")
        title = item.get("title", "")
        summary = item.get("summary", "")
        source = item.get("source", "")
        url = item.get("url", "")

        if url:
            lines.append(f"{emoji} *\\[{rank}\\] [{title}]({url})*")
        else:
            lines.append(f"{emoji} *\\[{rank}\\] {title}*")
        lines.append(f"    {summary}")
        if source:
            lines.append(f"    _{source}_")
        lines.append("")

    lines.append("Powered by your Daily Briefing AI")
    return "\n".join(lines)


async def send_telegram(message: str, bot_token: str, chat_id: str) -> dict:
    """Send a text message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload)
        # If MarkdownV2 fails, retry with plain text
        if resp.status_code != 200:
            payload["parse_mode"] = ""
            payload["text"] = message.replace("*", "").replace("_", "").replace("\\[", "[").replace("\\]", "]")
            resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
