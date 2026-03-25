# Getting Started

## Prerequisites

### Required Tools

| Tool | Version | Install | Purpose |
|---|---|---|---|
| **Python** | 3.12+ | `brew install python` | Local testing |
| **AWS CLI** | v2 | `brew install awscli` | AWS interactions |
| **SAM CLI** | Latest | `brew install aws-sam-cli` | Lambda deployment |
| **GitHub CLI** | Latest | `brew install gh` | (Future CI/CD use) |

### AWS Configuration

The project uses the AWS profile named `personal`. Configure it with:

```bash
aws configure --profile personal
# Enter: Access Key ID, Secret Access Key, default region (us-east-1), output format (json)
```

Verify connectivity:

```bash
aws sts get-caller-identity --profile personal
```

### Required API Keys

Before deploying, you need three external API keys:

#### 1. Anthropic (Claude)

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Create an API key from the API Keys section
3. Store it in AWS Secrets Manager (see [Configuration](configuration.md))

#### 2. Tavily

1. Sign up free at [app.tavily.com](https://app.tavily.com)
2. Free tier: 1,000 searches/month (9 topics × 3 queries = 27 searches/run)
3. Store the key in AWS Secrets Manager

#### 3. Telegram Bot

1. Open Telegram and chat with [@BotFather](https://t.me/BotFather)
2. Send `/newbot`, follow the prompts, copy the bot token
3. Find your chat ID by messaging [@userinfobot](https://t.me/userinfobot)
4. Store both in AWS Secrets Manager

## Initial Setup

### 1. Create AWS Secrets

```bash
# Secret 1: Daily briefing config (Telegram + Tavily)
aws secretsmanager create-secret \
  --name daily-briefing \
  --secret-string '{
    "telegram_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID",
    "tavily_api_key": "tvly-YOUR_TAVILY_KEY"
  }' \
  --profile personal \
  --region us-east-1

# Secret 2: Anthropic API key
aws secretsmanager create-secret \
  --name invoice-tracker/anthropic-api-key \
  --secret-string 'YOUR_ANTHROPIC_API_KEY' \
  --profile personal \
  --region us-east-1
```

Verify secrets were created:

```bash
aws secretsmanager list-secrets --profile personal --region us-east-1
```

### 2. Subscribe to SNS (Optional — for Email/SMS)

If you want the briefing delivered via email or SMS through SNS:

```bash
# Get the SNS topic ARN after deployment
aws sns list-topics --profile personal --region us-east-1

# Subscribe an email address
aws sns subscribe \
  --topic-arn "arn:aws:sns:us-east-1:ACCOUNT_ID:daily-briefing" \
  --protocol email \
  --notification-endpoint "you@example.com" \
  --profile personal

# Subscribe a phone number (must include country code)
aws sns subscribe \
  --topic-arn "arn:aws:sns:us-east-1:ACCOUNT_ID:daily-briefing" \
  --protocol sms \
  --notification-endpoint "+31612345678" \
  --profile personal
```

Check your email/phone for a subscription confirmation and confirm it.

### 3. Deploy

```bash
make deploy
```

This runs `sam build` followed by `sam deploy --guided` (first time) or a guided deployment. Confirm the stack name `daily-briefing` and note the output values.

### 4. Test Immediately

```bash
make invoke-aws
```

Check your Telegram channel for the briefing. If nothing arrives within 2 minutes, check the logs:

```bash
make logs
```

### 5. Verify the Schedule

The EventBridge rule should be active. Confirm:

```bash
aws events describe-rule \
  --name daily-briefing-schedule \
  --profile personal \
  --region us-east-1
```

Look for `"State": "ENABLED"`.

## Next Steps

- [Architecture overview](architecture.md) — Understand how the system works
- [Customization guide](customization.md) — Add or modify topics
- [Operations guide](operations.md) — Day-to-day management
