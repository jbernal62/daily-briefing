# Daily Briefing Assistant — Design Document

**Date:** 2026-03-01
**Status:** Approved

## Problem

Get a personalized, AI-curated summary of the 10 most valuable items across news, stocks, jobs, tech, and general knowledge — delivered via WhatsApp every morning.

## Architecture

Single AWS Lambda function triggered daily by EventBridge (cron).

```
EventBridge (cron: 7:00 AM) → Lambda → Claude API → Meta WhatsApp Cloud API
```

### Flow

1. Load `config.yaml` from S3 (or bundled)
2. Fetch all data sources in parallel (async HTTP)
3. Send ~50-100 raw items to Claude API for ranking and summarization
4. Format top 10 as a WhatsApp message
5. Deliver via Meta WhatsApp Cloud API

## Data Sources

| Category | Source | Auth |
|---|---|---|
| Global News | GNews API (100 req/day free) | API key |
| Stocks | yfinance (no limit) | None |
| Tech/Dev | HackerNews API | None |
| Tech/Dev | Dev.to API | None |
| Jobs | Adzuna API (250 req/day free) | API key |
| Knowledge | Wikipedia Featured Article API | None |

## Configuration

YAML file defining user interests:

```yaml
profile:
  name: Ezra
  timezone: America/New_York
  delivery_time: "07:00"

interests:
  news_topics: ["technology", "world", "business", "science"]
  stocks: ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
  job_keywords: ["DevOps", "Cloud Engineer", "Platform Engineer", "SRE"]
  job_location: "United States"
  tech_tags: ["AI", "kubernetes", "cloud", "serverless"]

limits:
  max_items: 10
  weights:
    news: 3
    stocks: 2
    jobs: 2
    tech: 2
    knowledge: 1
```

## Delivery

Meta WhatsApp Cloud API (direct, no middleman). Utility messages at ~$0.005/msg.

### Message Format

```
Good morning Ezra! Here's your Daily 10:

[1] Title of top news story
    2-line summary. Source: Reuters

[2] TSLA +4.2% ($187.50)
    Why it moved: Earnings beat expectations...

[3] Senior DevOps Engineer — $180K @ Stripe
    Remote · Kubernetes, Terraform, AWS

... (up to 10 items)
```

## Security

- API keys in AWS Secrets Manager (or Lambda env vars encrypted with KMS)
- WhatsApp token in Secrets Manager
- No secrets in source code
- S3 bucket is private

## Tech Stack

- **Runtime:** Python 3.12
- **Infrastructure:** AWS Lambda + EventBridge + S3
- **AI:** Claude API (Anthropic)
- **Delivery:** Meta WhatsApp Cloud API
- **IaC:** SAM or CDK (TBD in implementation plan)
- **Dependencies:** httpx (async HTTP), yfinance, anthropic SDK, pyyaml

## Cost Estimate

| Service | Monthly Cost |
|---|---|
| AWS Lambda | ~$0.00 (free tier) |
| Claude API | ~$0.50-1.50 |
| WhatsApp | ~$0.15 |
| News/Job APIs | $0.00 (free tiers) |
| S3 | ~$0.00 |
| **Total** | **~$1-2/month** |

## Decisions

- **Monolithic Lambda** over Step Functions — one daily invocation doesn't justify orchestration complexity
- **Meta Cloud API** over Twilio — no markup, cheapest option for low volume
- **YAML config** over web UI — simple, version-controlled, no extra infrastructure
- **Claude API** over GPT-4o — already in ecosystem, excellent summarization, cost-competitive
