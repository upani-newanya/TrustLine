"""Simple file-based complaint case handler for the agent pipeline.

Stores cases as JSON files in a `complaints/` directory.
"""
import json
import os
import random
from datetime import datetime


COMPLAINTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "complaints")


def _ensure_dir():
    os.makedirs(COMPLAINTS_DIR, exist_ok=True)


def _generate_case_id() -> str:
    now = datetime.now().strftime("%Y%m%d")
    rand = random.randint(1000, 9999)
    return f"TL-{now}-{rand}"


def _case_path(case_id: str) -> str:
    return os.path.join(COMPLAINTS_DIR, f"{case_id}.json")


def create_case(record: dict) -> str:
    """Create a new complaint case file. Returns the case ID."""
    _ensure_dir()
    case_id = _generate_case_id()
    data = {
        "case_id": case_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "records": [record],
        "metadata": record.get("metadata", {}),
        "status": "open",
    }
    with open(_case_path(case_id), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return case_id


def load_case(case_id: str) -> dict | None:
    """Load a case by ID. Returns None if not found."""
    path = _case_path(case_id)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_case(case_id: str, update: dict) -> None:
    """Merge new data into an existing case file."""
    data = load_case(case_id)
    if data is None:
        return
    data["updated_at"] = datetime.now().isoformat()
    if "records" not in data:
        data["records"] = []
    data["records"].append(update)
    # Merge metadata
    if "metadata" in update:
        existing_meta = data.get("metadata", {})
        existing_meta.update(update["metadata"])
        data["metadata"] = existing_meta
    # Merge top-level status/flags
    for key in ("status", "support_requested"):
        if key in update:
            data[key] = update[key]
    with open(_case_path(case_id), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def find_duplicate(record: dict) -> str | None:
    """Check existing cases for a likely duplicate based on user_input similarity.

    Returns the case ID of the duplicate if found, else None.
    """
    _ensure_dir()
    user_input = (record.get("user_input") or "").lower().strip()
    if not user_input:
        return None
    for fname in os.listdir(COMPLAINTS_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(COMPLAINTS_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for rec in data.get("records", []):
                existing = (rec.get("user_input") or "").lower().strip()
                if existing and existing == user_input:
                    return data.get("case_id", fname.replace(".json", ""))
        except Exception:
            continue
    return None
