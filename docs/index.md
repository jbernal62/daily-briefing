# Daily Briefing — Documentation

AI-powered personal news briefing delivered to Telegram every weekday morning.

## Contents

- [Getting Started](getting-started.md) — Prerequisites and initial setup
- [Architecture](architecture.md) — System design and component overview
- [Configuration](configuration.md) — Secrets, environment variables, and API keys
- [Deployment](deployment.md) — Building and deploying to AWS
- [Operations](operations.md) — Day-to-day management and monitoring
- [Customization](customization.md) — Adding and configuring topics
- [API Reference](api-reference.md) — External API integrations (Tavily, Claude, Telegram, SNS)
- [Troubleshooting](troubleshooting.md) — Common issues and debugging
- [Development](development.md) — Local development workflow

## Overview

Daily Briefing is an event-driven system that runs on AWS Lambda, delivering a personalized morning intelligence report covering 9 curated topics. Each run fetches real-time news via Tavily, synthesizes it with Claude AI, and delivers formatted messages to Telegram and SNS (email/SMS).

**Schedule:** Weekdays at 09:30 AM CEST (07:30 UTC)

**Key technologies:**
- AWS Lambda (Python 3.12)
- AWS EventBridge (scheduling)
- AWS Secrets Manager (credentials)
- AWS SNS (email + SMS delivery)
- Anthropic Claude (`claude-sonnet-4-6`)
- Tavily API (real-time web search)
- Telegram Bot API (message delivery)

## Quick Links

| Resource | URL |
|---|---|
| AWS Console (Lambda) | https://console.aws.amazon.com/lambda |
| AWS Console (Secrets) | https://console.aws.amazon.com/secretsmanager |
| AWS Console (EventBridge) | https://console.aws.amazon.com/events |
| CloudWatch Logs | `aws logs tail /aws/lambda/daily-briefing` |
| Tavily Dashboard | https://app.tavily.com |
| Anthropic Console | https://console.anthropic.com |
