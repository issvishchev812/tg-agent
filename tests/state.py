import json
from pathlib import Path
import hashlib

STATE_FILE = Path(__file__).parent / "state.json"
PROCESSED_FILE = Path(__file__).parent / "processed.json"


def load_state():
    if not STATE_FILE.exists():
        return {}

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=4)


def get_text_hash(text):
    normalized_text = " ".join(text.lower().split())
    return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()


def load_processed():
    if not PROCESSED_FILE.exists():
        return set()

    with open(PROCESSED_FILE, "r", encoding="utf-8") as file:
        return set(json.load(file))


def save_processed(processed):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as file:
        json.dump(list(processed), file, ensure_ascii=False, indent=4)


def mark_as_processed(text_hash):
    processed = load_processed()
    processed.add(text_hash)
    save_processed(processed)