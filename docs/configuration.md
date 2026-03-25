# Configuration

## Environment Variables

These are automatically injected by AWS SAM and do not need manual configuration:

| Variable | Source | Purpose |
|---|---|---|
| `AWS_REGION_NAME` | `!Ref AWS::Region` in template.yaml | Region for all boto3 clients |
| `SNS_TOPIC_ARN` | `!Ref BriefingTopic` in template.yaml | SNS delivery target |

Both are defined in the `Globals.Function.Environment.Variables` section of `template.yaml`.

## AWS Secrets Manager

All sensitive configuration is stored in AWS Secrets Manager. The Lambda function reads secrets at runtime.

### Secret 1: `daily-briefing`

Contains Telegram and Tavily configuration. Stored as JSON.

```json
{
  "telegram_token": "Bot token from @BotFather",
  "telegram_chat_id": "Numeric or @username of the target chat",
  "tavily_api_key": "tvly-..."
}
```

**Create:**
```bash
aws secretsmanager create-secret \
  --name daily-briefing \
  --secret-string '{
    "telegram_token": "YOUR_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID",
    "tavily_api_key": "tvly-YOUR_KEY"
  }' \
  --profile personal \
  --region us-east-1
```

**Update:**
```bash
aws secretsmanager put-secret-value \
  --secret-id daily-briefing \
  --secret-string '{
    "telegram_token": "NEW_TOKEN",
    "telegram_chat_id": "NEW_CHAT_ID",
    "tavily_api_key": "tvly-NEW_KEY"
  }' \
  --profile personal \
  --region us-east-1
```

**Verify:**
```bash
aws secretsmanager get-secret-value \
  --secret-id daily-briefing \
  --profile personal \
  --region us-east-1 \
  --query SecretString --output text | jq .
```

### Secret 2: `invoice-tracker/anthropic-api-key`

Contains the Anthropic API key. Stored as a plain string (not JSON).

```bash
aws secretsmanager create-secret \
  --name invoice-tracker/anthropic-api-key \
  --secret-string "sk-ant-api03-YOUR_KEY" \
  --profile personal \
  --region us-east-1
```

**Update:**
```bash
aws secretsmanager put-secret-value \
  --secret-id invoice-tracker/anthropic-api-key \
  --secret-string "sk-ant-api03-NEW_KEY" \
  --profile personal \
  --region us-east-1
```

### IAM Permissions

The Lambda function's execution role has read access to both secrets. The policy is defined inline in `template.yaml`:

```yaml
Policies:
  - Statement:
      - Effect: Allow
        Action:
          - secretsmanager:GetSecretValue
        Resource:
          - !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:invoice-tracker/anthropic-api-key*"
          - !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:daily-briefing*"
```

The `*` suffix allows for versioned secret ARNs (which AWS creates automatically on rotation).

## Telegram Configuration

### Getting a Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow prompts (bot name, username)
4. Copy the token shown: `123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`

### Finding Your Chat ID

**For private chats:**
1. Message **@userinfobot** on Telegram
2. It will reply with your numeric user ID (e.g., `123456789`)

**For group chats:**
1. Add your bot to the group
2. Send a message in the group
3. Visit: `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
4. Look for `"chat":{"id":-123456789,...}` — this is your group chat ID
5. Make sure to start the chat with `/start` if needed

**Important:** The bot must be a member of the group/channel before it can send messages.

## Tavily Configuration

### Rate Limits

| Plan | Monthly Searches | Rate Limit |
|---|---|---|
| Free | 1,000 | ~1 req/sec |
| Pro | 5,000 | Higher |
| Enterprise | Unlimited | Higher |

Each briefing run uses approximately:
- 9 topics × 3 queries = 27 searches (advanced depth)
- Plus retries on timeouts

The free tier is sufficient for daily briefings (27 × ~22 weekdays = ~594 searches/month).

### API Key Format

Tavily keys start with `tvly-`. Example: `tvly-abc123def456...`

If no Tavily key is provided (or it equals `PLACEHOLDER`), the searcher silently skips API calls and returns empty results. Claude will then generate sections from its trained knowledge.

## SNS Subscriptions

SNS is optional — the briefing works fine with just Telegram. To enable email/SMS:

### Email Subscription

```bash
aws sns subscribe \
  --topic-arn "arn:aws:sns:us-east-1:ACCOUNT_ID:daily-briefing" \
  --protocol email \
  --notification-endpoint "you@example.com" \
  --profile personal
```

Check your email and click the confirmation link.

### SMS Subscription

```bash
aws sns subscribe \
  --topic-arn "arn:aws:sns:us-east-1:ACCOUNT_ID:daily-briefing" \
  --protocol sms \
  --notification-endpoint "+31612345678" \
  --profile personal
```

**SMS Cost:** AWS charges ~$0.08/SMS segment. The digest is designed to fit in ~4 segments (~$0.32/briefing).

### View Active Subscriptions

```bash
aws sns list-subscriptions-by-topic \
  --topic-arn "arn:aws:sns:us-east-1:ACCOUNT_ID:daily-briefing" \
  --profile personal
```

### Delete a Subscription

```bash
aws sns unsubscribe \
  --subscription-arn "arn:aws:sns:us-east-1:ACCOUNT_ID:daily-briefing:SUBSCRIPTION_ID" \
  --profile personal
```

## Configuration Checklist

Before deploying for the first time, verify:

- [ ] `daily-briefing` secret created with valid Telegram token and chat ID
- [ ] `invoice-tracker/anthropic-api-key` secret created with valid Anthropic key
- [ ] Telegram bot added to target chat and `/start` sent
- [ ] Tavily account created at [app.tavily.com](https://app.tavily.com)
- [ ] (Optional) SNS subscriptions confirmed
- [ ] AWS profile `personal` configured and tested
- [ ] `samconfig.toml` region matches your secrets region
