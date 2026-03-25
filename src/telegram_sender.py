"""
Telegram Bot API integration for sending the daily briefing.
Handles message splitting (4096 char limit) and HTML parse mode.
"""

import logging
import re
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

MAX_LENGTH = 4096


class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token.strip()
        self.chat_id = str(chat_id).strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send(self, text: str, parse_mode: Optional[str] = "HTML") -> bool:
        """Send a message, splitting if needed."""
        if len(text) <= MAX_LENGTH:
            return self._post(text, parse_mode)

        for chunk in self._split(text):
            self._post(chunk, parse_mode)
            time.sleep(0.8)  # Telegram rate limit: 1 msg/sec to same chat
        return True

    def _post(self, text: str, parse_mode: Optional[str]) -> bool:
        payload: dict = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": False,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        try:
            r = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=15,
            )
            if r.ok:
                return True

            logger.error(f"Telegram API error {r.status_code}: {r.text[:200]}")

            # Retry as plain text if HTML parsing failed
            if parse_mode:
                logger.warning("Retrying without parse_mode")
                plain_payload = {**payload}
                plain_payload.pop("parse_mode", None)
                plain_payload["text"] = self._strip_html(text)
                r2 = requests.post(
                    f"{self.base_url}/sendMessage",
                    json=plain_payload,
                    timeout=15,
                )
                return r2.ok

            return False

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def _split(self, text: str) -> list:
        """Split text at newlines to stay under MAX_LENGTH."""
        chunks = []
        lines = text.split("\n")
        current_lines = []
        current_len = 0

        for line in lines:
            line_len = len(line) + 1  # +1 for newline
            if current_len + line_len > MAX_LENGTH - 100 and current_lines:
                chunks.append("\n".join(current_lines))
                current_lines = [line]
                current_len = line_len
            else:
                current_lines.append(line)
                current_len += line_len

        if current_lines:
            chunks.append("\n".join(current_lines))

        return chunks

    @staticmethod
    def _strip_html(text: str) -> str:
        return re.sub(r"<[^>]+>", "", text)
