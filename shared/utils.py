from dataclasses import asdict
from datetime import datetime
import json


def now_iso() -> str:
    """Return current timestamp in ISO 8601 format."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def to_json(obj) -> str:
    """Serialize a dataclass object to pretty JSON."""
    return json.dumps(asdict(obj), ensure_ascii=False, indent=2)


def load_json(path: str) -> dict:
    """Read a JSON file and return dictionary data."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, path: str) -> None:
    """Write dictionary data to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)