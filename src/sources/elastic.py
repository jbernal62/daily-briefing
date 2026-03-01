"""Elasticsearch innovations — from Elastic blog and HN/Dev.to."""

import httpx


async def fetch_elastic_news(tags: list[str]) -> list[dict]:
    """Fetch latest Elasticsearch/Elastic Stack innovations from Dev.to and HN."""
    items = []

    async with httpx.AsyncClient(timeout=15) as client:
        # Dev.to articles about Elasticsearch
        for tag in tags:
            try:
                resp = await client.get(
                    "https://dev.to/api/articles",
                    params={"tag": tag.lower().replace(" ", ""), "top": 7, "per_page": 3},
                )
                resp.raise_for_status()
                for article in resp.json():
                    items.append({
                        "category": "elastic",
                        "title": article["title"],
                        "description": article.get("description", "")[:200],
                        "source": f"Dev.to — {article.get('user', {}).get('name', 'Unknown')}",
                        "url": article.get("url", ""),
                        "published": article.get("published_at", ""),
                    })
            except httpx.HTTPError:
                continue

        # Also search HN for Elasticsearch content
        try:
            resp = await client.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={"query": "elasticsearch", "tags": "story", "hitsPerPage": 3},
            )
            resp.raise_for_status()
            for hit in resp.json().get("hits", []):
                items.append({
                    "category": "elastic",
                    "title": hit.get("title", ""),
                    "description": f"Points: {hit.get('points', 0)} | Comments: {hit.get('num_comments', 0)}",
                    "source": "HackerNews",
                    "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
                    "published": hit.get("created_at", ""),
                })
        except httpx.HTTPError:
            pass

    return items
