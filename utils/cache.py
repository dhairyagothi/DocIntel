import hashlib
import json
from pathlib import Path
from typing import Any


def cache_key(payload: Any, model: str = "", prompt_version: str = "1") -> str:
    encoded = json.dumps({"payload": payload, "model": model, "prompt_version": prompt_version}, sort_keys=True, default=str)
    return hashlib.sha256(encoded.encode()).hexdigest()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None