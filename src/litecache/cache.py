"""Thread-safe in-memory cache with TTL and LRU eviction."""

from __future__ import annotations

import math
import threading
import time
from collections import OrderedDict
from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar, cast

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


@dataclass(frozen=True)
class CacheStats:
    """A snapshot of cache counters."""

    hits: int
    misses: int
    sets: int
    deletes: int
    evictions: int
    expirations: int
    size: int
    max_items: Optional[int]

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


@dataclass
class _Entry(Generic[V]):
    value: V
    expires_at: Optional[float]


class LiteCache(Generic[K, V]):
    """A small Redis/Memcached-like cache that runs inside one Python process.

    Args:
        max_items: Maximum live entries. The least recently used entry is
            evicted when the limit is exceeded. ``None`` means unlimited.
        default_ttl: Default lifetime in seconds. ``None`` means no expiration.
        timer: Monotonic clock injection point, primarily useful for tests.
    """

    def __init__(
        self,
        max_items: Optional[int] = 1024,
        default_ttl: Optional[float] = None,
        *,
        timer: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_items is not None and max_items <= 0:
            raise ValueError("max_items must be positive or None")
        self._validate_ttl(default_ttl)
        self.max_items = max_items
        self.default_ttl = default_ttl
        self._timer = timer
        self._data: OrderedDict[K, _Entry[V]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._deletes = 0
        self._evictions = 0
        self._expirations = 0

    @staticmethod
    def _validate_ttl(ttl: Optional[float]) -> None:
        if ttl is not None and (not math.isfinite(ttl) or ttl < 0):
            raise ValueError("ttl must be a finite non-negative number or None")

    def _deadline(self, ttl: Optional[float]) -> Optional[float]:
        return None if ttl is None else self._timer() + ttl

    def _is_expired(self, entry: _Entry[V], now: Optional[float] = None) -> bool:
        return entry.expires_at is not None and entry.expires_at <= (
            self._timer() if now is None else now
        )

    def _remove_expired_key(self, key: K, now: Optional[float] = None) -> bool:
        entry = self._data.get(key)
        if entry is not None and self._is_expired(entry, now):
            del self._data[key]
            self._expirations += 1
            return True
        return False

    def set(
        self, key: K, value: V, ttl: Optional[float] = None, *, nx: bool = False
    ) -> bool:
        """Store a value.

        ``ttl=None`` uses ``default_ttl``. Use ``nx=True`` to store only when
        the key does not already exist.
        """
        effective_ttl = self.default_ttl if ttl is None else ttl
        self._validate_ttl(effective_ttl)
        with self._lock:
            self._remove_expired_key(key)
            if nx and key in self._data:
                return False
            self._data[key] = _Entry(value, self._deadline(effective_ttl))
            self._data.move_to_end(key)
            self._sets += 1
            self._evict_if_needed()
            return True

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Return a value, or ``default`` when missing or expired."""
        with self._lock:
            if self._remove_expired_key(key):
                self._misses += 1
                return default
            entry = self._data.get(key)
            if entry is None:
                self._misses += 1
                return default
            self._data.move_to_end(key)
            self._hits += 1
            return entry.value

    def delete(self, *keys: K) -> int:
        """Delete keys and return the number that existed."""
        removed = 0
        with self._lock:
            for key in keys:
                if self._remove_expired_key(key):
                    continue
                if key in self._data:
                    del self._data[key]
                    removed += 1
            self._deletes += removed
        return removed

    def exists(self, key: K) -> bool:
        with self._lock:
            return not self._remove_expired_key(key) and key in self._data

    def touch(self, key: K, ttl: Optional[float] = None) -> bool:
        """Refresh a key's lifetime and mark it as recently used."""
        effective_ttl = self.default_ttl if ttl is None else ttl
        self._validate_ttl(effective_ttl)
        with self._lock:
            if self._remove_expired_key(key) or key not in self._data:
                return False
            self._data[key].expires_at = self._deadline(effective_ttl)
            self._data.move_to_end(key)
            return True

    def ttl(self, key: K) -> Optional[float]:
        """Return seconds remaining, or ``None`` for missing/non-expiring keys."""
        with self._lock:
            if self._remove_expired_key(key):
                return None
            entry = self._data.get(key)
            if entry is None or entry.expires_at is None:
                return None
            return max(0.0, entry.expires_at - self._timer())

    def mget(self, keys: Iterable[K]) -> dict[K, Optional[V]]:
        return {key: self.get(key) for key in keys}

    def mset(self, values: Mapping[K, V], ttl: Optional[float] = None) -> None:
        with self._lock:
            for key, value in values.items():
                self.set(key, value, ttl=ttl)

    def incr(self, key: K, amount: int = 1, ttl: Optional[float] = None) -> int:
        """Atomically increment an integer value, creating it from zero.

        An existing key keeps its original expiration deadline. ``ttl`` is only
        applied when the key is created.
        """
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise TypeError("amount must be an integer")
        with self._lock:
            self._remove_expired_key(key)
            entry = self._data.get(key)
            if entry is None:
                self.set(key, cast(V, amount), ttl=ttl)
                return amount
            if not isinstance(entry.value, int) or isinstance(entry.value, bool):
                raise TypeError("cached value must be an integer")
            value = entry.value + amount
            entry.value = value  # type: ignore[assignment]
            self._data.move_to_end(key)
            return value

    def decr(self, key: K, amount: int = 1, ttl: Optional[float] = None) -> int:
        return self.incr(key, -amount, ttl=ttl)

    def cleanup(self) -> int:
        """Remove all expired entries and return the removal count."""
        with self._lock:
            now = self._timer()
            expired = [
                key for key, entry in self._data.items() if self._is_expired(entry, now)
            ]
            for key in expired:
                del self._data[key]
            self._expirations += len(expired)
            return len(expired)

    def clear(self) -> int:
        with self._lock:
            count = len(self._data)
            self._data.clear()
            self._deletes += count
            return count

    def stats(self) -> CacheStats:
        with self._lock:
            self.cleanup()
            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                sets=self._sets,
                deletes=self._deletes,
                evictions=self._evictions,
                expirations=self._expirations,
                size=len(self._data),
                max_items=self.max_items,
            )

    def _evict_if_needed(self) -> None:
        if self.max_items is None:
            return
        while len(self._data) > self.max_items:
            self._data.popitem(last=False)
            self._evictions += 1

    def __contains__(self, key: object) -> bool:
        return self.exists(key)  # type: ignore[arg-type]

    def __len__(self) -> int:
        with self._lock:
            self.cleanup()
            return len(self._data)
