"""Adzuna API — job listings."""

import httpx


async def fetch_jobs(app_id: str, api_key: str, keywords: list[str], location: str, max_per_keyword: int = 3) -> list[dict]:
    """Fetch job listings from Adzuna for each keyword."""
    items = []
    async with httpx.AsyncClient(timeout=15) as client:
        for kw in keywords:
            try:
                resp = await client.get(
                    f"https://api.adzuna.com/v1/api/jobs/{location}/search/1",
                    params={
                        "app_id": app_id,
                        "app_key": api_key,
                        "what": kw,
                        "results_per_page": max_per_keyword,
                        "sort_by": "date",
                        "content-type": "application/json",
                    },
                )
                resp.raise_for_status()
                for job in resp.json().get("results", []):
                    salary = ""
                    if job.get("salary_min") and job.get("salary_max"):
                        salary = f"${int(job['salary_min']):,}-${int(job['salary_max']):,}"
                    elif job.get("salary_min"):
                        salary = f"${int(job['salary_min']):,}+"
                    company = job.get("company", {}).get("display_name", "Unknown")
                    loc = job.get("location", {}).get("display_name", "")
                    items.append({
                        "category": "jobs",
                        "title": f"{job.get('title', kw)} @ {company}",
                        "description": f"{loc} | {salary}".strip(" | "),
                        "source": "Adzuna",
                        "url": job.get("redirect_url", ""),
                        "published": job.get("created", ""),
                    })
            except httpx.HTTPError:
                continue
    return items
