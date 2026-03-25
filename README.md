# Daily Briefing

AI-powered daily news briefing delivered to Telegram every morning at 9:30 AM CEST.

## How it works

```
EventBridge cron (07:30 UTC)
    → Lambda (Python 3.12)
        → Tavily API (real-time web search per topic)
        → Claude claude-sonnet-4-6 (synthesizes results into briefing sections)
        → Telegram Bot API (sends formatted messages)
```

## Topics covered

| Section | Focus |
|---------|-------|
| 🧬 Gut Health & Microbiome | L. reuteri, microbiome foods, avoid list, clinical studies |
| 🇳🇱 Netherlands & Expat Life | Organic markets near Lelystad, food safety, IND/tax news |
| 💻 Hardware & Gadgets | Best laptops, GPU rankings, new tech releases |
| ⌚ Health Wearables | Smart rings, health tracking, validation studies |
| 🤖 AI & Productivity | New tools to try, productivity workflows, AI income strategies |
| ✈️ Jobs & Australia Relocation | Cloud architect roles, 482 visa sponsorship, AUD salaries |
| 📈 ETF & Markets | IWDA (IE00BK5BQT80) performance, MSCI World outlook |
| 🏥 Health Optimization | Supplements, sleep, longevity, gut health protocols |
| ☁️ Cloud & DevOps | AWS/Azure launches, serverless patterns, IaC updates |

## Setup

### 1. Prerequisites

- AWS CLI with profile `personal` configured
- SAM CLI installed (`brew install aws-sam-cli`)
- GitHub CLI installed (`brew install gh`)

### 2. Tavily API key (required for real-time news)

Sign up free at [app.tavily.com](https://app.tavily.com) — free tier gives 1,000 searches/month (enough for this app).

### 3. Create AWS secret

```bash
aws secretsmanager create-secret \
  --name daily-briefing \
  --secret-string '{
    "telegram_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID",
    "tavily_api_key": "tvly-YOUR_KEY"
  }' \
  --profile personal \
  --region us-east-1
```

### 4. Deploy

```bash
make deploy
```

### 5. Test immediately

```bash
make invoke-aws
```

## Operations

```bash
make invoke-aws      # Trigger a briefing immediately
make logs            # Tail CloudWatch logs live
make schedule-off    # Pause the daily schedule
make schedule-on     # Resume the daily schedule
make deploy          # Redeploy after code changes
```

## Schedule

The EventBridge cron runs at **07:30 UTC**:
- April–October (CEST, UTC+2): **09:30 AM local time** ✅
- November–March (CET, UTC+1): **08:30 AM local time**

To adjust, edit `template.yaml` → `Schedule: cron(30 7 * * ? *)`.

## Architecture

```
┌─────────────────────┐
│  EventBridge        │
│  cron(30 7 * * ? *) │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐     ┌──────────────────────┐
│  Lambda             │────▶│  Secrets Manager     │
│  daily-briefing     │     │  - anthropic-api-key  │
│  1024 MB / 10 min   │     │  - daily-briefing     │
└────────┬────────────┘     └──────────────────────┘
         │
         ├──▶ Tavily API (web search per topic, parallel)
         │
         ├──▶ Claude claude-sonnet-4-6 (synthesis per topic, parallel)
         │
         └──▶ Telegram Bot API (sequential delivery)
```

## Adding topics

Edit `src/topics.py` and add a new entry to `TOPICS`. Each topic needs:
- `id` — unique string identifier
- `emoji` — section emoji
- `title` — display title
- `queries` — list of 3–4 Tavily search queries
- `context` — instructions for Claude on what to focus on

## Suggested additional topics

- 🧠 **Mental Performance** — nootropics, focus protocols, cognitive research
- 💰 **Side Income** — freelance rates, passive income, consulting opportunities
- 🔐 **Cloud Security** — CVEs, AWS security advisories, zero-trust patterns
- 🌿 **Nutrition Science** — specific food research, meal timing, metabolomics
- 🏋️ **Exercise & Recovery** — training science, HRV-guided protocols
- 🌍 **Macro & Geopolitics** — market-moving global events for ETF context
