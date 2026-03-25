# Operations

## Day-to-Day Commands

All operations use the Makefile for consistency:

```bash
make invoke-aws   # Trigger an immediate briefing run
make logs         # Tail CloudWatch logs in real-time
make schedule-on  # Enable the daily schedule
make schedule-off # Disable the daily schedule
make deploy       # Redeploy after code changes
make clean        # Remove local build artifacts
```

## Manual Invocation

Trigger a briefing run immediately without waiting for the schedule:

```bash
make invoke-aws
```

This invokes the Lambda function directly and prints the response. To see full execution logs:

```bash
make logs
```

## Monitoring

### CloudWatch Logs

The Lambda function writes logs to `/aws/lambda/daily-briefing`.

```bash
# Tail logs in real-time
make logs

# Get the last 100 log lines
aws logs filter-log-events \
  --log-group-name /aws/lambda/daily-briefing \
  --profile personal \
  --region us-east-1 \
  --limit 100 \
  --query 'sortBy(@, &timestamp)' \
  --output table

# Get logs from a specific time range
aws logs filter-log-events \
  --log-group-name /aws/lambda/daily-briefing \
  --profile personal \
  --region us-east-1 \
  --start-time $(date -d '1 hour ago' +%s000) \
  --filter-pattern ""
```

### CloudWatch Metrics

Monitor Lambda performance in the AWS Console under **CloudWatch → Metrics → Lambda**:

| Metric | What it tells you |
|---|---|
| Invocations | How many times the function ran |
| Duration | How long each run took |
| Errors | Failed executions |
| Throttles | Times Lambda hit concurrency limits |
| IteratorAge | (Not applicable — no stream trigger) |

Set a duration alarm to alert if briefings start taking too long (approaching the 10-minute timeout):

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name "daily-briefing-duration-high" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Maximum \
  --period 60 \
  --threshold 480000 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --alarm-actions "arn:aws:sns:us-east-1:ACCOUNT_ID:daily-briefing" \
  --dimensions Name=FunctionName,Value=daily-briefing \
  --profile personal
```

## Schedule Management

### Disable the Daily Schedule

```bash
make schedule-off
```

This disables the EventBridge rule. No briefings will run on schedule until re-enabled.

**Use case:** Vacation, maintenance, or testing to avoid spamming Telegram.

### Enable the Daily Schedule

```bash
make schedule-on
```

Re-enables the EventBridge rule. The next briefing will run at the next scheduled time.

### Verify Schedule Status

```bash
aws events describe-rule \
  --name daily-briefing-schedule \
  --profile personal \
  --region us-east-1 \
  --query State --output text
```

Returns `ENABLED` or `DISABLED`.

### Change the Schedule Time

Edit `template.yaml`, find the `Schedule` field, and change the cron expression:

```yaml
Schedule: cron(30 7 * * ? *)  # 07:30 UTC
Schedule: cron(0 8 * * ? *)   # 08:00 UTC
Schedule: cron(30 6 * * ? *)  # 06:30 UTC
```

Then redeploy:

```bash
make deploy
```

### Schedule Across Timezones

The EventBridge schedule runs in UTC. To get a briefing at a specific local time across DST transitions:

| Local Time (CEST, UTC+2) | UTC | Cron Expression |
|---|---|---|
| 09:30 AM (Apr–Oct) | 07:30 | `cron(30 7 * * ? *)` |
| 08:30 AM (CET, UTC+1) | 07:30 | `cron(30 7 * * ? *)` |
| 09:00 AM (CEST, UTC+2) | 07:00 | `cron(0 7 * * ? *)` |
| 08:00 AM (CET, UTC+1) | 07:00 | `cron(0 7 * * ? *)` |

Because the schedule is fixed in UTC, the local time shifts by 1 hour on DST transition dates. To maintain a consistent local time across DST:

1. Use EventBridge rules with two schedules (one for each DST offset), or
2. Use an external scheduler (cron on a server) that calculates the correct UTC time dynamically

## Secrets Management

### Rotating the Anthropic API Key

```bash
# Get a new key from console.anthropic.com
aws secretsmanager put-secret-value \
  --secret-id invoice-tracker/anthropic-api-key \
  --secret-string "sk-ant-api03-NEW_KEY" \
  --profile personal \
  --region us-east-1
```

The next Lambda invocation will automatically pick up the new key.

### Rotating the Telegram Token

```bash
# Revoke old token via @BotFather, then update the secret
aws secretsmanager get-secret-value \
  --secret-id daily-briefing \
  --profile personal \
  --query SecretString --output text | jq .
```

Then use `aws secretsmanager put-secret-value` with the updated token.

### Rotating the Tavily Key

Same process as Telegram — update the `tavily_api_key` field in the `daily-briefing` secret.

## Lambda Concurrency

By default, Lambda concurrency is shared across all functions in the account. To ensure the daily briefing always has capacity:

```bash
aws lambda put-function-concurrency \
  --function-name daily-briefing \
  --reserved-concurrent-executions 5 \
  --profile personal
```

This reserves 5 concurrent executions for the function, ensuring the daily run (which is a single invocation) always has capacity even if other functions in the account are throttling.

## Cost Management

### Lambda Cost

Each daily briefing run processes 9 topics in parallel. Estimated duration: **30–90 seconds**.

| Memory | Duration (avg) | Compute (GB-s) | Monthly cost (22 runs) |
|---|---|---|---|
| 1024 MB | 60s | 0.063 GB-s | ~$0.04/month |

Lambda costs are negligible for this use case.

### Tavily Cost

| Searches/run | Runs/month | Total searches | Free tier |
|---|---|---|---|
| ~27 | 22 | ~594 | 1,000/month |

**Cost: $0/month** on the free tier.

### SNS Cost

| Protocol | Size | Segments | Cost/run | Monthly (22 runs) |
|---|---|---|---|---|
| Email | ~4KB | N/A | $0 | ~$0 |
| SMS | ~600 chars | 3 | ~$0.006 | ~$0.13 |

### Total Monthly Cost

Rough estimate with 22 weekday runs: **~$0.20/month** (mostly SMS costs).

## Backup

Secrets stored in AWS Secrets Manager are automatically replicated within the region. For cross-region backup, consider enabling replication in the Secrets Manager console.

Lambda deployment packages are stored in the SAM-managed S3 bucket. CloudFormation stack backups can be exported as templates from the AWS Console.
