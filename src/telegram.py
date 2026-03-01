"""Telegram Bot API — send the daily briefing message."""

import httpx

# Section headers for visual grouping
SECTION_HEADERS = {
    "jobs": "REMOTE JOBS",
    "elastic": "ELASTICSEARCH",
    "cloud": "CLOUD INNOVATIONS",
    "claude_tip": "CLAUDE CODE TIP",
    "etf": "ETF & MARKET",
    "crypto": "BITCOIN",
    "dutch_news": "NETHERLANDS NEWS",
    "weather": "BEST WEATHER IN EUROPE",
    "positive": "POSITIVE NEWS",
}


def format_briefing_telegram(ranked_items: list[dict], name: str) -> str:
    """Format ranked items as a Telegram message with HTML."""
    lines = [f"<b>Good morning {name}! Here's your Daily Briefing:</b>\n"]

    current_section = None
    for item in ranked_items:
        emoji = item.get("emoji", "")
        title = item.get("title", "")
        summary = item.get("summary", "")
        source = item.get("source", "")
        url = item.get("url", "")
        category = item.get("category", "")

        # Add section header when category changes
        section = SECTION_HEADERS.get(category, "")
        if section and section != current_section:
            current_section = section
            lines.append(f"\n{'=' * 20}")
            lines.append(f"<b>{section}</b>")
            lines.append(f"{'=' * 20}")

        # Title with link
        if url:
            lines.append(f"{emoji} <a href=\"{url}\">{_escape_html(title)}</a>")
        else:
            lines.append(f"{emoji} <b>{_escape_html(title)}</b>")
        lines.append(f"   {_escape_html(summary)}")
        if source:
            lines.append(f"   <i>{_escape_html(source)}</i>")
        lines.append("")

    lines.append("\nPowered by your Daily Briefing AI")
    return "\n".join(lines)


def _escape_html(text: str) -> str:
    """Escape HTML special chars for Telegram."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


async def send_telegram(message: str, bot_token: str, chat_id: str) -> dict:
    """Send message via Telegram Bot API, splitting if over 4096 chars."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    last_result = {}

    chunks = _split_message(message, max_len=4096)

    async with httpx.AsyncClient(timeout=30) as client:
        for chunk in chunks:
            payload = {
                "chat_id": chat_id,
                "text": chunk,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }
            resp = await client.post(url, json=payload)
            # If HTML parse fails, retry as plain text
            if resp.status_code != 200:
                payload["parse_mode"] = ""
                payload["text"] = _strip_html(chunk)
                resp = await client.post(url, json=payload)
            resp.raise_for_status()
            last_result = resp.json()

    return last_result


def _split_message(text: str, max_len: int = 4096) -> list[str]:
    """Split a long message into chunks at line boundaries."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_len:
            if current:
                chunks.append(current)
            current = line
        else:
            current = current + "\n" + line if current else line
    if current:
        chunks.append(current)
    return chunks


def _strip_html(text: str) -> str:
    """Remove HTML tags for plain text fallback."""
    import re
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
