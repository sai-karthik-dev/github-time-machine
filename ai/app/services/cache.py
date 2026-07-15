"""
Simple in-memory LRU cache with TTL for AI response caching.
Avoids calling OpenAI repeatedly for the same demo-repo queries.
"""

from __future__ import annotations

import hashlib
import time
from collections import OrderedDict
from typing import Any, Optional


class ResponseCache:
    """Thread-safe-ish LRU cache with time-based expiration."""

    def __init__(self, max_size: int = 256, ttl_seconds: int = 3600):
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    @staticmethod
    def _make_key(*parts: str) -> str:
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, *key_parts: str) -> Optional[Any]:
        """Retrieve a cached value if it exists and hasn't expired."""
        key = self._make_key(*key_parts)
        entry = self._store.get(key)
        if entry is None:
            return None
        timestamp, value = entry
        if time.time() - timestamp > self._ttl:
            del self._store[key]
            return None
        # Move to end (most recently used)
        self._store.move_to_end(key)
        return value

    def set(self, *key_parts: str, value: Any) -> None:
        """Store a value, evicting the oldest entry if full."""
        key = self._make_key(*key_parts)
        self._store[key] = (time.time(), value)
        self._store.move_to_end(key)
        while len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)
