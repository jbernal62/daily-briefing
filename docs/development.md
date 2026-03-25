# Development

## Project Structure

```
daily-briefing/
├── src/                          # Lambda function source code
│   ├── handler.py               # Lambda entry point, orchestrator
│   ├── topics.py                # Topic definitions (queries + context)
│   ├── searcher.py              # Tavily API client
│   ├── synthesizer.py           # Claude API client
│   ├── telegram_sender.py      # Telegram Bot API client
│   ├── sns_publisher.py         # SNS publisher (email + SMS)
│   └── requirements.txt        # Python dependencies
├── docs/                         # Project documentation
├── template.yaml                 # AWS SAM template (IaC)
├── samconfig.toml               # SAM CLI configuration
├── Makefile                     # Build, deploy, invoke, logs
└── README.md                    # Quick-start README
```

## Local Development

### Setup

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt
```

Note: `boto3` and `anthropic` are installed but require AWS credentials and API keys to use beyond basic imports.

### Environment Variables (Local Testing)

Create a `.env` file for local testing:

```bash
export AWS_REGION_NAME="us-east-1"
export SNS_TOPIC_ARN="arn:aws:sns:us-east-1:ACCOUNT:daily-briefing"
export TELEGRAM_TOKEN="YOUR_TOKEN"
export TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
export TAVILY_API_KEY="tvly-..."
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

Then source it:
```bash
source .env
```

### Local Invocation

The Lambda function can be invoked locally using the AWS SAM CLI:

```bash
# Start a local API endpoint (not useful for scheduled functions)
sam local start-lambda

# Or invoke with a mock event
sam local invoke DailyBriefingFunction -e events/event.json
```

However, scheduled functions are easiest to test by deploying and using `make invoke-aws`.

### Testing Individual Modules

```python
# Test the searcher
from searcher import TavilySearcher
s = TavilySearcher("tvly-YOUR_KEY")
results = s.search("test query", max_results=2)
print(results)

# Test the synthesizer
from synthesizer import ClaudeSynthesizer
c = ClaudeSynthesizer("sk-ant-api03-YOUR_KEY")
msg = c.format_topic({"emoji": "🧬", "title": "Test", "context": "test"}, [], "March 25, 2026")
print(msg)

# Test the Telegram sender
from telegram_sender import TelegramBot
bot = TelegramBot("YOUR_TOKEN", "YOUR_CHAT_ID")
bot.send("<b>Test message</b>")
```

## Code Conventions

### Python Style

- No enforced linter — follow the existing code style
- No type annotations (absent from current codebase)
- No inline comments (minimal, module-level only)
- Logging via `logging.getLogger(__name__)` — `logger.info` / `logger.warning` / `logger.error`

### Error Handling Strategy

- **Search failures:** Return empty results, log warning, continue processing
- **Synthesis failures:** Return error tuple, log error, send fallback message to Telegram
- **Delivery failures:** Log error, continue with remaining messages
- **Secrets failures:** Raise exception (unrecoverable)

### Concurrency

- `ThreadPoolExecutor(max_workers=4)` for parallel topic processing
- `requests.Session` is not used — each API call creates a new session
- Telegram sends are sequential with 1-second delays

### Dependencies

Keep dependencies minimal. Current dependencies:

| Package | Purpose | Rationale |
|---|---|---|
| `anthropic>=0.49.0` | Claude API client | Official Anthropic SDK |
| `requests>=2.32.0` | HTTP client | Tavily + Telegram APIs |
| `boto3>=1.34.0` | AWS SDK | Secrets Manager + SNS |

## Making Changes

### Adding a New Module

1. Create the module in `src/`
2. Import it in `handler.py`
3. Add any new secret requirements to `template.yaml` IAM policy
4. Update `docs/api-reference.md` if it's an external integration
5. Deploy with `make deploy`

### Modifying the SAM Template

When editing `template.yaml`:
- Changes to `CodeUri` or `Handler` trigger a Lambda code update on next deploy
- Changes to `MemorySize` or `Timeout` trigger a Lambda configuration update
- New IAM resources require `CAPABILITY_IAM` (already configured in samconfig.toml)
- Run `make deploy` to apply changes

### Adding New Secrets

1. Create the secret in AWS Secrets Manager
2. Add the ARN pattern to the IAM policy in `template.yaml`
3. Add secret retrieval in `handler.py`'s `get_secrets()` function
4. Update `docs/configuration.md`

## Code Review Checklist

Before deploying changes:

- [ ] Code changes tested locally or via `make invoke-aws`
- [ ] New dependencies added to `src/requirements.txt`
- [ ] New secrets documented in `docs/configuration.md`
- [ ] SAM template updated if IAM permissions changed
- [ ] CloudWatch logs checked for errors after deploy
- [ ] Telegram receives the briefing correctly
- [ ] SNS subscribers receive messages (if configured)

## Performance Considerations

- **Lambda cold starts:** First run after deployment takes ~2–5 seconds (importing `anthropic`, `boto3`)
- **Parallel processing:** 4 workers process topics concurrently; 9 topics = ~3 batches
- **Tavily latency:** Each search takes ~1–3 seconds; 3 queries × 9 topics = ~27 seconds (serial), ~7 seconds (parallel with 4 workers)
- **Claude latency:** Each synthesis takes ~3–8 seconds; 9 topics in parallel ≈ ~8 seconds
- **Telegram delivery:** 10 messages × 1 second delay = ~10 seconds

Estimated total runtime: **30–90 seconds** depending on API responsiveness.

## Release Process

1. Make code changes in a feature branch
2. Test with `make invoke-aws`
3. Review CloudWatch logs
4. Merge to main
5. Run `make deploy`
6. Verify in Telegram

No formal versioning system is currently in place. SAM deployments are tracked via CloudFormation stack history in the AWS Console.
