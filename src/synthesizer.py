"""
Claude API integration for synthesizing search results into formatted Telegram briefings.
"""

import logging
from typing import List, Dict

import anthropic

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are Jeff's personal daily intelligence briefing writer. Jeff is a senior cloud/AWS architect
living near Lelystad, Netherlands, who is passionate about health optimization, microbiome science,
AI productivity, and long-term investing.

Your job: synthesize news and research into a concise, high-value Telegram section.

FORMAT RULES (Telegram HTML parse mode):
- Header line: <b>EMOJI TITLE — DATE</b>
- One blank line after header
- Each item:
    N. <a href="URL">Item Title</a>
    1–2 sentences with the key finding, number, or actionable takeaway.
- Blank line between items
- Max 6–8 items per section
- Items must be numbered (1., 2., etc.)
- Links MUST be complete https:// URLs you are confident exist
- If you are NOT confident a URL exists, write the title as plain text (no link)
- In plain text: escape & as &amp; — never use raw < or > outside HTML tags
- No trailing newlines, no preamble, no commentary outside the section

TONE: Specific, dense, actionable. Include numbers, percentages, dosages, prices, strain names.
Avoid vague statements like "studies show" — say which study, what outcome, what dose.
"""


class ClaudeSynthesizer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key.strip())

    def format_topic(self, topic: dict, search_results: List[Dict], date: str) -> str:
        if search_results:
            results_block = "\n\n".join(
                f"Title: {r.get('title', 'No title')}\n"
                f"URL: {r.get('url', '')}\n"
                f"Snippet: {r.get('content', '')[:450]}"
                for r in search_results[:8]
            )
            user_msg = (
                f"Create a briefing section for: {topic['emoji']} {topic['title']}\n"
                f"Date: {date}\n"
                f"Focus: {topic['context']}\n\n"
                f"Use these search results as your sources. Include their URLs as links:\n\n"
                f"{results_block}\n\n"
                f"Output ONLY the formatted Telegram HTML section."
            )
        else:
            user_msg = (
                f"Create a briefing section for: {topic['emoji']} {topic['title']}\n"
                f"Date: {date}\n"
                f"Focus: {topic['context']}\n\n"
                f"No live search results available. Use your knowledge to provide 5–6 "
                f"relevant, recent items. Include real URLs only when you are confident "
                f"they exist and are correct. Omit links if uncertain.\n\n"
                f"Output ONLY the formatted Telegram HTML section."
            )

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )

        return response.content[0].text.strip()
