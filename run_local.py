"""Local test runner — loads .env and runs the pipeline."""

import os
import sys
from pathlib import Path

# Fix Windows console encoding for emoji output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()

import asyncio
from src.handler import run_pipeline, load_config

config = load_config()
result = asyncio.run(run_pipeline(config))
# Print the formatted message
print("\n" + "=" * 60)
print(result.get("message", "No message"))
print("=" * 60)
print(f"\nStats: {result['items_fetched']} fetched -> {result['items_selected']} selected -> {result['message_length']} chars")
