"""Meta WhatsApp Cloud API — send the daily briefing message."""

import httpx


def format_briefing(ranked_items: list[dict], name: str) -> str:
    """Format ranked items into a WhatsApp-friendly message."""
    lines = [f"Good morning {name}! Here's your Daily 10:\n"]

    for item in ranked_items:
        emoji = item.get("emoji", "")
        rank = item.get("rank", "")
        title = item.get("title", "")
        summary = item.get("summary", "")
        source = item.get("source", "")

        lines.append(f"{emoji} *[{rank}] {title}*")
        lines.append(f"    {summary}")
        if source:
            lines.append(f"    _{source}_")
        lines.append("")

    lines.append("Powered by your Daily Briefing AI")
    return "\n".join(lines)


async def send_whatsapp(
    message: str,
    phone_number_id: str,
    recipient_number: str,
    access_token: str,
) -> dict:
    """Send a text message via Meta WhatsApp Cloud API."""
    url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "text",
        "text": {"body": message},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
