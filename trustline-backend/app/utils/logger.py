"""Simple JSON-lines logger for agent pipeline interactions."""
import json
import os
from datetime import datetime


LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs")
LOG_FILE = os.path.join(LOGS_DIR, "agent_conversations.log")


def log_interaction(record: dict) -> None:
    """Append a single interaction record as a JSON line."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    entry = {"timestamp": datetime.now().isoformat(), **record}
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")
