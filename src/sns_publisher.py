"""
SNS publisher for daily briefing.
Sends full plain-text briefing to email subscribers and a short digest to SMS subscribers.
Uses SNS MessageStructure=json to deliver different content per protocol.
"""

import json
import logging
import re

import boto3

logger = logging.getLogger(__name__)


def _html_to_text(html: str) -> str:
    """Convert Telegram HTML to readable plain text."""
    text = html
    # <b>Title</b> → TITLE
    text = re.sub(r"<b>(.*?)</b>", lambda m: m.group(1).upper(), text, flags=re.DOTALL)
    # <a href="url">label</a> → label\n  → url
    text = re.sub(
        r'<a href="([^"]+)">(.*?)</a>',
        lambda m: f"{m.group(2).strip()}  →  {m.group(1)}",
        text,
        flags=re.DOTALL,
    )
    # Strip remaining tags
    text = re.sub(r"<[^>]+>", "", text)
    # Unescape HTML entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    # Collapse excess blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _build_email(sections: list, date: str) -> str:
    """Build full plain-text email body."""
    lines = [
        f"DAILY BRIEFING — {date}",
        "=" * 60,
        "",
    ]
    for section in sections:
        lines.append(_html_to_text(section))
        lines.append("")
        lines.append("-" * 60)
        lines.append("")
    return "\n".join(lines)


def _build_sms(sections: list, date: str) -> str:
    """
    Build a short SMS digest (~600 chars, ~4 segments at $0.08 each).
    Contains just the section emoji/title and the first item from each section.
    """
    parts = [f"Daily Briefing {date}"]

    for section in sections:
        plain = _html_to_text(section)
        section_lines = [l.strip() for l in plain.split("\n") if l.strip()]

        if not section_lines:
            continue

        # Header (e.g. "CLOUD & DEVOPS — March 25, 2026")
        header = section_lines[0]

        # First numbered item — look for "1." prefix
        first_item = ""
        for line in section_lines[1:]:
            if re.match(r"^1\.", line):
                # Trim the URL part for SMS
                item_text = re.sub(r"\s+→\s+https?://\S+", "", line)
                first_item = item_text[:120]
                break

        if first_item:
            parts.append(f"{header}\n• {first_item}")
        else:
            parts.append(header)

    digest = "\n\n".join(parts)
    return digest[:600] if len(digest) > 600 else digest


def publish(topic_arn: str, sections: list, date: str, region: str = "us-east-1") -> bool:
    """
    Publish to SNS topic with per-protocol content:
      - email / email-json → full formatted plain-text briefing
      - sms               → short digest (~600 chars)
      - default           → used by any other protocol

    SNS subscriptions to create:
      aws sns subscribe --protocol email --notification-endpoint you@example.com ...
      aws sns subscribe --protocol sms   --notification-endpoint +31XXXXXXXXX  ...
    """
    if not topic_arn:
        logger.warning("SNS_TOPIC_ARN not set — skipping SNS publish")
        return False

    email_body = _build_email(sections, date)
    sms_body = _build_sms(sections, date)

    message_map = {
        "default": f"Daily Briefing — {date}",
        "email": email_body,
        "email-json": email_body,
        "sms": sms_body,
    }

    try:
        sns = boto3.client("sns", region_name=region)
        sns.publish(
            TopicArn=topic_arn,
            Subject=f"Daily Briefing — {date}",
            Message=json.dumps(message_map),
            MessageStructure="json",
        )
        logger.info(f"SNS publish OK → {topic_arn}")
        return True
    except Exception as e:
        logger.error(f"SNS publish failed: {e}")
        return False
