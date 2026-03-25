# API Reference

## External API Integrations

The Daily Briefing integrates with 4 external services. All API calls are made from the Lambda function at runtime.

## Tavily Search API

Used to fetch real-time web search results for each topic.

### Endpoint

```
POST https://api.tavily.com/search
```

### Request

```python
requests.post(
    "https://api.tavily.com/search",
    json={
        "api_key": "tvly-...",
        "query": "L reuteri probiotic latest research 2026",
        "search_depth": "advanced",    # "basic" or "advanced"
        "include_answer": False,
        "include_raw_content": False,
        "max_results": 4,              # 1–10
    },
    timeout=25,
)
```

### Response

```json
{
  "results": [
    {
      "title": "L. reuteri Shows Promise in Human Trials",
      "url": "https://example.com/article",
      "content": "A 2026 study published in Nature...",
      "score": 0.95
    }
  ]
}
```

### Rate Limits

| Plan | Monthly | Concurrent |
|---|---|---|
| Free | 1,000 searches | ~1/sec |
| Pro | 5,000 | Higher |

### Error Handling

- **Timeout (>25s):** Returns empty results, logs warning, continues
- **Rate limit (429):** Returns empty results, logs warning
- **Invalid key (401):** Raises exception, topic fails
- **No key configured:** Silently returns empty results, Claude falls back to knowledge

### Implementation

See `src/searcher.py` — `TavilySearcher.search()`.

---

## Anthropic Claude API

Used to synthesize search results into formatted Telegram sections.

### Endpoint

```
POST https://api.anthropic.com/v1/messages
```

### Request

```python
anthropic_client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1400,
    system=SYSTEM_PROMPT,
    messages=[
        {
            "role": "user",
            "content": "Create a briefing section for: 🧬 Gut Health..."
        }
    ],
)
```

### System Prompt

The system prompt (`src/synthesizer.py`) instructs Claude to:
- Format output as Telegram HTML
- Use numbered items (1., 2., etc.)
- Include complete URLs as `<a href>` tags
- Be specific with numbers, dosages, and percentages
- Output only the formatted section (no preamble)

### Model: `claude-sonnet-4-6`

The Sonnet 4-6 model provides a good balance of reasoning quality, speed, and cost. It supports longer context (200K tokens) sufficient for 8–10 search results plus topic context.

### Token Budget

Each topic section request uses approximately:
- System prompt: ~300 tokens
- User message (with results): ~800 tokens
- Claude response: ~1,000 tokens
- **Total per topic:** ~2,100 tokens
- **Total per run (9 topics):** ~19,000 tokens

Monthly cost estimate (22 runs): ~$0.20–$0.50 depending on message mix.

### Error Handling

- **Invalid key (401):** Lambda invocation fails, error logged to CloudWatch
- **Rate limit (429):** `anthropic` SDK retries automatically with exponential backoff
- **Timeout:** No timeout configured for Claude calls — relies on Lambda's 10-minute timeout

### Implementation

See `src/synthesizer.py` — `ClaudeSynthesizer.format_topic()`.

---

## Telegram Bot API

Used to deliver formatted messages to the user's Telegram chat.

### Endpoint

```
POST https://api.telegram.org/bot{TOKEN}/sendMessage
```

### Request

```python
requests.post(
    "https://api.telegram.org/bot{token}/sendMessage",
    json={
        "chat_id": "123456789",
        "text": "<b>Header</b>\n\n1. <a href=\"...\">Item</a>",
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    },
    timeout=15,
)
```

### Message Limits

| Limit | Value | Handling |
|---|---|---|
| Max message length | 4,096 chars | Auto-split by newline boundaries |
| Rate limit | 1 msg/sec to same chat | 1-second delay between sends |
| Max URL length | 512 chars | Tavily URLs rarely exceed this |

### HTML Parse Mode

Telegram's `parse_mode=HTML` supports a subset of HTML:

| Tag | Support |
|---|---|
| `<b>...</b>` | Bold |
| `<i>...</i>` | Italic |
| `<a href="URL">text</a>` | Hyperlinks |
| `&amp;` | Escaped ampersand |

**Note:** `<strong>`, `<em>`, and other tags are NOT supported. The Claude system prompt enforces compatible tags.

### Error Handling

- **HTML parse error (400):** Retries as plain text (HTML stripped via regex)
- **Chat not found (400):** Logs error, does not retry
- **Rate limited (429):** Does not retry within the Lambda run
- **Network error:** Returns False, logs error

### Implementation

See `src/telegram_sender.py` — `TelegramBot.send()`.

---

## AWS SNS

Used to deliver the briefing to email and SMS subscribers.

### Publish Request

```python
sns.publish(
    TopicArn="arn:aws:sns:us-east-1:ACCOUNT:daily-briefing",
    Subject="Daily Briefing — March 25, 2026",
    Message=json.dumps({
        "default": "Daily Briefing — March 25, 2026",
        "email": "FULL_PLAIN_TEXT_BRIEFING...",
        "email-json": "FULL_PLAIN_TEXT_BRIEFING...",
        "sms": "SHORT_DIGEST...",
    }),
    MessageStructure="json",
)
```

### Message Structure

`MessageStructure=json` allows different content per protocol. SNS inspects the `protocol` of each subscription and delivers the matching key.

### Email Format

HTML converted to plain text:
- `<b>TITLE</b>` → `TITLE` (uppercase)
- `<a href="URL">text</a>` → `text → URL`
- Excess blank lines collapsed

### SMS Format

Digest of ~600 characters containing:
- Date header
- Each section title (emoji + name)
- First numbered item from each section (title only, no URL)

### Error Handling

- **SNS publish disabled:** If `SNS_TOPIC_ARN` is empty, skips publish silently
- **SNS error:** Logs error, briefing continues (Telegram delivery is not affected)
- **No subscribers:** SNS delivers to zero recipients (no error)

### Implementation

See `src/sns_publisher.py` — `publish()`.

---

## AWS Secrets Manager

Used to retrieve all API credentials at Lambda cold start.

### Get Secret Value

```
GET /secretsmanager/get-secret-value
```

```python
secretsmanager.get_secret_value(SecretId="daily-briefing")
# Returns: {"SecretString": '{"telegram_token": "...", ...}'}
```

### Secret ARNs Used

| Secret | ARN Pattern |
|---|---|
| Anthropic key | `arn:aws:secretsmanager:${Region}:${AccountId}:secret:invoice-tracker/anthropic-api-key*` |
| Daily briefing config | `arn:aws:secretsmanager:${Region}:${AccountId}:secret:daily-briefing*` |

The `*` suffix allows access to all versions of the secret (AWS auto-versions on update).

### Permissions

The Lambda execution role needs:

```json
{
  "Effect": "Allow",
  "Action": ["secretsmanager:GetSecretValue"],
  "Resource": [
    "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:invoice-tracker/anthropic-api-key*",
    "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:daily-briefing*"
  ]
}
```

### Implementation

See `src/handler.py` — `get_secrets()`.

---

## Cost Summary

| API | Calls/Run | Cost/Run | Monthly (22 runs) |
|---|---|---|---|
| Tavily | ~27 (free tier) | $0 | $0 |
| Claude | 9 | ~$0.015 | ~$0.33 |
| Telegram | ~11 (1 opening + 9 sections + 1 footer) | $0 | $0 |
| AWS SNS | 1 | $0 | $0 |
| AWS Lambda | 1 × 60s × 1024MB | ~$0.002 | ~$0.05 |
| **Total** | | | **~$0.40/month** |
