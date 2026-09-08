from datetime import datetime
from typing import Callable


def log_stage(logs: list[str], message: str, callback: Callable[[str], None] | None = None) -> None:
    line = f"{datetime.now().strftime('%H:%M:%S')}  ✓ {message}"
    logs.append(line)
    if callback:
        callback(line)