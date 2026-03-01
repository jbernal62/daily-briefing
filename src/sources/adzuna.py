"""Adzuna API — job listings across multiple countries."""

import httpx


async def fetch_jobs(
    app_id: str,
    api_key: str,
    keywords: list[str],
    locations: list[str],
    tags: list[str],
    max_total: int = 5,
) -> list[dict]:
    """Fetch remote/relocation job listings from Adzuna across multiple countries."""
    items = []
    seen_titles = set()

    async with httpx.AsyncClient(timeout=15) as client:
        for location in locations:
            for kw in keywords:
                # Add remote/relocation to search
                for tag in tags:
                    query = f"{kw} {tag}"
                    try:
                        resp = await client.get(
                            f"https://api.adzuna.com/v1/api/jobs/{location}/search/1",
                            params={
                                "app_id": app_id,
                                "app_key": api_key,
                                "what": query,
                                "results_per_page": 3,
                                "sort_by": "date",
                                "content-type": "application/json",
                            },
                        )
                        resp.raise_for_status()
                        for job in resp.json().get("results", []):
                            title = job.get("title", kw)
                            # Deduplicate
                            if title.lower() in seen_titles:
                                continue
                            seen_titles.add(title.lower())

                            salary = ""
                            if job.get("salary_min") and job.get("salary_max"):
                                currency = "EUR" if location in ("nl", "de") else "GBP"
                                salary = f"{currency} {int(job['salary_min']):,}-{int(job['salary_max']):,}"
                            elif job.get("salary_min"):
                                currency = "EUR" if location in ("nl", "de") else "GBP"
                                salary = f"{currency} {int(job['salary_min']):,}+"

                            company = job.get("company", {}).get("display_name", "Unknown")
                            loc = job.get("location", {}).get("display_name", "")
                            country = location.upper()

                            desc_parts = [f"{loc} ({country})"]
                            if salary:
                                desc_parts.append(salary)
                            if tag:
                                desc_parts.append(tag.capitalize())

                            items.append({
                                "category": "jobs",
                                "title": f"{title} @ {company}",
                                "description": " | ".join(desc_parts),
                                "source": "Adzuna",
                                "url": job.get("redirect_url", ""),
                                "published": job.get("created", ""),
                            })
                    except httpx.HTTPError:
                        continue

    # Return only the top N most recent
    return items[:max_total * 2]  # Give Claude extra to pick from
