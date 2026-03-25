# Troubleshooting

## No Briefing Arrives in Telegram

### Step 1: Check the Lambda execution

```bash
make invoke-aws
```

Watch the output for errors. If it succeeds (returns `{"status": "success", ...}`), the Lambda ran correctly.

### Step 2: Check CloudWatch logs

```bash
make logs
```

Look for:
- `"Daily briefing starting"` — Lambda invoked successfully
- `"[topic_id] done — N search results"` — Topic processed OK
- `"[topic_id] failed: ..."` — Topic failed with error
- `"Daily briefing complete in Xs"` — Run finished

### Step 3: Verify secrets are accessible

If you see errors like `AccessDeniedException`, the Lambda execution role may not have permission to read secrets:

```bash
# Test secret access directly
aws secretsmanager get-secret-value \
  --secret-id daily-briefing \
  --profile personal \
  --region us-east-1

aws secretsmanager get-secret-value \
  --secret-id invoice-tracker/anthropic-api-key \
  --profile personal \
  --region us-east-1
```

If these fail, check that the secrets exist in the correct region (`us-east-1`).

### Step 4: Verify Telegram configuration

```bash
# Test the bot token directly
curl -s "https://api.telegram.org/botYOUR_TOKEN/getMe"
```

Should return `{"ok": true, "result": {"id": ..., "is_bot": true, ...}}`.

```bash
# Check bot info
curl -s "https://api.telegram.org/botYOUR_TOKEN/getChat?chat_id=YOUR_CHAT_ID"
```

Should return chat details. If you get `"chat not found"`, the bot is not in that chat.

## "Telegram API error 400"

Common causes:

1. **Invalid chat ID** — The chat ID format is incorrect. For private chats it should be a number (e.g., `123456789`). For groups it should be negative (e.g., `-1001234567890`).
2. **Bot not in chat** — Add the bot to the group/channel before sending messages.
3. **Bot was kicked** — The bot may have been removed from the group.

**Fix:** Update the `telegram_chat_id` in the `daily-briefing` secret.

## "Telegram API error 429" (Rate Limited)

Telegram rate-limits bots to ~30 messages per second. The code already enforces 1-second delays between messages. If you still hit rate limits:

1. Wait 5–10 minutes (rate limit windows reset)
2. The next scheduled run will succeed
3. Check [Telegram Bot API rate limits](https://core.telegram.org/bots/faq#my-bot-is-hitting-rate-limits) for updated limits

## Sections Missing or "Could not load section today"

### Tavily API unavailable

If Tavily is down or rate-limited, the system falls back to Claude knowledge. The section should still appear, but with potentially less current information.

To check if Tavily is working:

```bash
curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "tvly-YOUR_KEY", "query": "test", "max_results": 1}'
```

### Claude API errors

If Claude fails:
1. Check the API key is valid in Secrets Manager
2. Check your Anthropic account has available quota
3. Check CloudWatch logs for specific error messages

### All topics fail

If every topic fails simultaneously, check:
1. AWS network connectivity from Lambda (rare to fail)
2. The Lambda function wasn't updated after secrets were rotated
3. The function's execution role permissions were revoked

## Schedule Not Running

### Check the EventBridge rule state

```bash
aws events describe-rule \
  --name daily-briefing-schedule \
  --profile personal \
  --region us-east-1
```

If `State` is `DISABLED`, re-enable it:

```bash
make schedule-on
```

### Check EventBridge targets

```bash
aws events list-targets-by-rule \
  --rule daily-briefing-schedule \
  --profile personal \
  --region us-east-1
```

Verify the target shows the correct Lambda function ARN.

### CloudWatch Logs but No Telegram Messages

If the Lambda runs (seen in CloudWatch) but no Telegram messages arrive:

1. The bot token may have been revoked via @BotFather
2. The bot may have been removed from the group
3. Network issues between AWS and Telegram (try a manual `make invoke-aws`)

## Lambda Timeout or Slow Execution

If briefings take >8 minutes:

1. Check CloudWatch for which topics are slow
2. Tavily timeouts (25s each) accumulate if many queries fail slowly
3. Claude synthesis typically takes 3–8 seconds per topic

**Temporary fix:** Increase Lambda timeout in `template.yaml`:
```yaml
Timeout: 900  # 15 minutes
MemorySize: 2048  # If CPU-bound
```

## SNS Not Delivering

1. Verify subscriptions are confirmed (check email/SMS for subscription confirmation)
2. Check the SNS topic ARN matches what's deployed:

```bash
aws sns list-topics --profile personal --region us-east-1
```

3. Test SNS manually:

```bash
aws sns publish \
  --topic-arn "arn:aws:sns:us-east-1:ACCOUNT:daily-briefing" \
  --message "Test message" \
  --subject "Test" \
  --profile personal
```

## Redeployment Issues

### "ResourceExistsException: Stack already exists"

Use `make deploy` instead of `sam deploy --guided` for subsequent deployments. The Makefile uses the correct change-set approach.

### "No changes to deploy"

Normal — SAM detected no differences between the current CloudFormation stack and the new template. This happens if you ran `make deploy` without making any code changes.

### Lambda not updating after code changes

```bash
make clean && make deploy
```

Force a clean rebuild.

## Common CloudWatch Log Patterns

```
# Lambda cold start
INFO: Daily briefing starting

# Topic completed
INFO: [gut_health] done — 8 search results
INFO: [netherlands] done — 6 search results

# Topic failed
ERROR: [hardware] failed: API request failed: 401

# Run completed
INFO: Daily briefing complete in 47.3s

# SNS publish
INFO: SNS publish OK → arn:aws:sns:us-east-1:ACCOUNT:daily-briefing

# Warning (no Tavily key)
WARNING: Tavily API key not configured — briefing will use Claude knowledge only.
```

## Getting Help

If an issue persists:
1. Check CloudWatch logs for the specific error
2. Verify all configuration values in Secrets Manager
3. Run `make invoke-aws` and capture the full output
4. Check [AWS Lambda troubleshooting](https://docs.aws.amazon.com/lambda/latest/operatorguide/profile-errors.html)
