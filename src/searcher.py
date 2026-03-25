"""
Tavily API integration for real-time web search.
Falls back gracefully if no API key is configured.
"""

import logging
from typing import List, Dict

import requests

logger = logging.getLogger(__name__)


class TavilySearcher:
    BASE_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: str):
        self.api_key = api_key.strip() if api_key else ""
        self.enabled = bool(self.api_key and self.api_key != "PLACEHOLDER")
        if not self.enabled:
            logger.warning(
                "Tavily API key not configured — briefing will use Claude knowledge only. "
                "Sign up at https://app.tavily.com to get fresh real-time news."
            )

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        if not self.enabled:
            return []

        try:
            response = requests.post(
                self.BASE_URL,
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_answer": False,
                    "include_raw_content": False,
                    "max_results": max_results,
                },
                timeout=25,
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except requests.exceptions.Timeout:
            logger.warning(f"Tavily timeout for query: {query}")
            return []
        except Exception as e:
            logger.warning(f"Tavily search failed for '{query}': {e}")
            return []

    def search_topic(self, topic: dict) -> List[Dict]:
        """Run up to 3 queries for a topic and return deduplicated results."""
        all_results: List[Dict] = []
        seen_urls: set = set()

        for query in topic["queries"][:3]:
            for result in self.search(query, max_results=4):
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(result)

        return all_results[:10]
