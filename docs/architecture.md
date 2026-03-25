# Architecture

## System Overview

Daily Briefing is an event-driven, serverless application running on AWS. There are no persistent servers — everything runs on ephemeral Lambda functions triggered by EventBridge schedules.

```
┌─────────────────────────────────────────────────────────────┐
│  EventBridge Schedule (cron: 30 7 * * ? *)                 │
│  Runs every weekday at 07:30 UTC (09:30 AM CEST)           │
└─────────────────────────┬───────────────────────────────────┘
                          │ triggers
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  AWS Lambda — daily-briefing                                │
│  Runtime: Python 3.12 | Memory: 1024 MB | Timeout: 10 min   │
├─────────────────────────────────────────────────────────────┤
│  Handler (handler.py) — Orchestrator                      │
│  1. Fetches secrets from Secrets Manager                   │
│  2. Sends opening message to Telegram                      │
│  3. Processes topics in parallel (max 4 workers)           │
│  4. Delivers results sequentially to Telegram               │
│  5. Publishes to SNS (email + SMS)                         │
└──────┬───────────────┬───────────────┬─────────────────────┘
       │               │               │
       ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│  Tavily API  │ │Claude claude-│ │  Telegram Bot API│
│  (9 × 3      │ │  sonnet-4-6  │ │  (message        │
│   queries)   │ │  (9 calls)   │ │   delivery)      │
└──────────────┘ └──────────────┘ └──────────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │  AWS SNS Topic   │
                                    │  (email + SMS)   │
                                    └──────────────────┘
```

## Component Details

### EventBridge Schedule

The schedule is defined in `template.yaml` under `DailyBriefingFunction.Events`:

```yaml
Schedule: cron(30 7 * * ? *)
```

| Field | Value | Meaning |
|---|---|---|
| `cron(30 7 * * ? *)` | Minutes=30, Hour=7, Day=*, Month=*, Day-of-week=? | Every day at 07:30 UTC |

The timezone behavior:
- **April–October (CEST, UTC+2):** 09:30 AM local time
- **November–March (CET, UTC+1):** 08:30 AM local time

### Lambda Function

**Memory:** 1024 MB  
**Timeout:** 600 seconds (10 minutes)  
**Runtime:** Python 3.12

The function runs in two phases:

**Phase 1 — Parallel Processing**  
Topics are processed concurrently using `ThreadPoolExecutor(max_workers=4)`:
- Each topic gets its own searcher + synthesizer
- Tavily is called first (up to 3 queries per topic, first 4 results each)
- Claude synthesizes the results into HTML-formatted Telegram sections
- 4 workers means ~3 batches of topics process in parallel

**Phase 2 — Sequential Delivery**  
Once all topics are processed:
- Opening message sent to Telegram
- Each topic sent in order (with 1-second delays to respect Telegram rate limits)
- Full briefing published to SNS for email/SMS subscribers

### AWS Secrets Manager

Two secrets are accessed at runtime:

| Secret Name | Type | Contents |
|---|---|---|
| `invoice-tracker/anthropic-api-key` | Plain string | Anthropic API key |
| `daily-briefing` | JSON object | `telegram_token`, `telegram_chat_id`, `tavily_api_key` |

The `invoice-tracker/anthropic-api-key` secret is shared with another project (`invoice-tracker`). This is intentional — it avoids duplicating the same API key.

### AWS SNS Topic

The SNS topic (`daily-briefing`) uses `MessageStructure=json` to deliver different content per protocol:

| Protocol | Content | Length |
|---|---|---|
| `email` / `email-json` | Full plain-text briefing | ~3,000–5,000 chars |
| `sms` | Digest with first item per section | ~600 chars |
| `default` | Generic fallback message | Short |

### Processing Flow

```
EventBridge trigger (07:30 UTC daily)
  │
  ▼
lambda_handler()
  │
  ├─ get_secrets() ────▶ Secrets Manager
  │
  ├─ bot.send(opening_message)
  │
  ├─ ThreadPoolExecutor(4 workers)
  │    │
  │    ├─ process_topic(topic_1)
  │    │    ├─ searcher.search_topic() ──▶ Tavily API
  │    │    └─ synthesizer.format_topic() ──▶ Claude API
  │    ├─ process_topic(topic_2) ...
  │    └─ process_topic(topic_N)
  │
  ├─ bot.send(section_1)
  ├─ bot.send(section_2) ... (1s delay between each)
  │
  └─ sns_publisher.publish() ──▶ SNS Topic
       │
       ├─▶ Email subscriber (full briefing)
       └─▶ SMS subscriber (digest)
```

## Topic Data Flow

Each of the 9 topics follows this path:

1. **Query** — 3 queries sent to Tavily (e.g., "L reuteri probiotic latest research 2026")
2. **Search** — Results deduplicated by URL, capped at 10 total
3. **Synthesize** — Claude receives search results + topic context
4. **Format** — Claude returns HTML-formatted Telegram section
5. **Deliver** — Section sent to Telegram via Bot API
6. **Archive** — Section queued for SNS email/SMS delivery

If Tavily returns no results (API unavailable, rate-limited, or no API key), Claude generates the section using its trained knowledge. The briefing still succeeds, but with potentially less current information.

## Infrastructure as Code

All AWS resources are defined in `template.yaml` using AWS SAM:

| Resource | Type | Purpose |
|---|---|---|
| `DailyBriefingFunction` | `AWS::Serverless::Function` | Main Lambda function |
| `BriefingTopic` | `AWS::SNS::Topic` | SNS topic for email/SMS delivery |
| IAM Policy | Inline | Secrets Manager read + SNS publish |
| `DailyScheduleCEST` | Schedule Event | EventBridge trigger |

## Regional Considerations

- **Region:** `us-east-1` (configured in `samconfig.toml`)
- All boto3 clients use `region_name=REGION` from the `AWS_REGION_NAME` environment variable
- Secrets Manager calls use the same region
- SNS publishing uses the same region
