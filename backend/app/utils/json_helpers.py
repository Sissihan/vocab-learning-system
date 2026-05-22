"""JSON serialization helpers for SQLite text columns."""
import json
from typing import Any


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def loads(text: str | None, default: Any = None) -> Any:
    if not text:
        return default if default is not None else {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default if default is not None else {}
