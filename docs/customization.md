# Customization

## Topics Overview

Topics are defined in `src/topics.py` as a list of dictionaries. Each topic has:

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `str` | Yes | Unique identifier (used in logging) |
| `emoji` | `str` | Yes | Telegram emoji header |
| `title` | `str` | Yes | Display title |
| `queries` | `List[str]` | Yes | 3–4 Tavily search queries |
| `context` | `str` | Yes | Instructions for Claude on what to prioritize |

## Adding a New Topic

Edit `src/topics.py` and append to the `TOPICS` list:

```python
{
    "id": "mental_performance",
    "emoji": "🧠",
    "title": "Mental Performance",
    "queries": [
        "nootropics supplements cognitive function 2026 research",
        "focus productivity attention training techniques 2026",
        "brain health neuroplasticity optimization 2026",
    ],
    "context": (
        "Jeff wants to optimize cognitive performance. "
        "Include: evidence-based nootropics (L-theanine, alpha-GPC, bacopa, modafinil), "
        "focus techniques (deep work, time blocking, pomodoro variations), "
        "recent neuroscience findings, and practical protocols. "
        "Prioritize human studies over animal models."
    ),
},
```

The briefing will automatically include the new topic on the next run.

## Modifying an Existing Topic

Edit the topic's fields directly in `TOPICS`. Common changes:

### Change Queries

```python
"queries": [
    "new GPU benchmark 2026 RTX 5000",       # Replace outdated query
    "best laptop developer 2026 MacBook Pro",
    "ARM laptop Windows performance 2026",
    "e-ink tablet productivity 2026",         # New query added
],
```

**Limit:** Only the first 3 queries are used (`topic["queries"][:3]` in `searcher.py`). A 4th query is ignored, so only define 3–4 queries per topic.

### Refine Context

The `context` string is passed to Claude as additional instructions. Make it specific:

**Too vague:**
```python
"context": "Include news about technology."
```

**Good:**
```python
"context": (
    "Focus on: AWS Lambda cold start improvements, "
    "new CDK constructs released this month, "
    "serverless architecture patterns for data pipelines, "
    "and cost optimization case studies with specific dollar amounts."
)
```

## Topic Processing Details

Each topic goes through:

1. **Search** — First 3 queries from `queries` list, max 4 results each
2. **Deduplication** — Results filtered by unique URL
3. **Limit** — Capped at 10 results total
4. **Synthesis** — Passed to Claude with `context` instructions
5. **Delivery** — Sent to Telegram as an HTML section

## Message Format

Claude generates messages in Telegram HTML format:

```html
<b>🧬 GUT HEALTH & MICROBIOME — March 25, 2026</b>

1. <a href="https://example.com/article">Study Finds L. reuteri Reduces Inflammation</a>
   Research from Stanford showed a 40% reduction in inflammatory markers after 8 weeks
   of supplementation with 10 billion CFU daily.

2. <a href="https://example.com/foods">Top Fermented Foods for Microbiome Diversity</a>
   Kimchi, kefir, and miso ranked highest in a 2026 microbiome diversity study of 2,000 participants.
```

**Rules enforced by the system prompt:**
- Header: `<b>EMOJI TITLE — DATE</b>`
- Items numbered 1–8 per section
- Links as `<a href="URL">Title</a>`
- `&` escaped as `&amp;`
- Max 1,400 tokens per section response from Claude

## Removing a Topic

To disable a topic without deleting it, comment out its entry in `TOPICS`:

```python
# {
#     "id": "hardware",
#     "emoji": "💻",
#     "title": "Hardware & Gadgets",
#     ...
# },
```

The handler references `len(TOPICS)` for the opening message count, so the count will automatically update.

## Topic Priority and Order

Topics are processed in the order they appear in the `TOPICS` list. Delivery to Telegram follows the same order. To reorder:

1. Cut the topic entry from its current position
2. Paste it at the desired position in the list

The opening message and SNS delivery both respect the same order.

## Testing Topic Changes

After modifying topics:

```bash
make deploy    # Deploy changes
make invoke-aws # Trigger a test run
make logs      # Monitor execution
```

Check your Telegram for the updated briefing.

## Suggested Additional Topics

The original `topics.py` includes commented suggestions:

```python
# - 🧠 Mental Performance (nootropics, focus, cognitive enhancement)
# - 💰 Side Income & Freelance (passive income, consulting rates)
# - 🔐 Cybersecurity (cloud security, new CVEs, tools)
# - 🌿 Nutrition Science (specific foods, meal timing, macros research)
# - 🏋️ Exercise & Recovery (training science, HRV-guided recovery)
# - 🌍 Macro & Geopolitics (market-moving global events)
```

## Tuning Search Queries

Effective queries follow these patterns:

| Pattern | Example |
|---|---|
| Include the year | `L reuteri probiotic research 2026` |
| Include action word | `best laptop developer buy 2026` |
| Be specific | `Oura ring Gen 4 vs Ultrahuman 2026` vs `wearables 2026` |
| Include region for local topics | `organic food delivery Netherlands 2026` |
| Ask for comparison | `MSCI World IWDA vs VWCE performance 2026` |

Avoid:
- Very broad queries (`technology news 2026`)
- Questions that require opinion (`should I buy a laptop`)
- Queries with no recent activity (old events won't have fresh results)
