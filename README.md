# litecache

[English](README.md) | [简体中文](README.zh-CN.md)

[Website](https://xuehaoweng.github.io/litecache/) · [Landing page source](docs/index.html)

[![CI](https://github.com/xuehaoweng/litecache/actions/workflows/ci.yml/badge.svg)](https://github.com/xuehaoweng/litecache/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A tiny, thread-safe, in-process cache for Python with TTL expiration and LRU
eviction. Its deliberately small API feels familiar if you have used Redis or
Memcached, while requiring no server and no runtime dependencies.

> **Note:** litecache is an in-process cache. Data is not shared between
> processes and disappears when the process exits.

## Features

- Thread-safe operations
- Per-key TTL and configurable default TTL
- LRU eviction with a configurable item limit
- Atomic integer increment/decrement
- Conditional `set(..., nx=True)`
- Batch reads and writes
- Hit, miss, eviction, and expiration statistics
- Zero runtime dependencies and a fully typed public API

## Installation

```bash
pip install litecache
```

For local development:

```bash
git clone https://github.com/xuehaoweng/litecache.git
cd litecache
python -m pip install -e ".[dev]"
```

## Quick start

```python
from litecache import LiteCache

cache = LiteCache(max_items=10_000, default_ttl=60)

cache.set("user:42", {"name": "Ada"})
user = cache.get("user:42")

cache.set("lock:job", True, ttl=5, nx=True)
cache.incr("page:views")
cache.mset({"feature:a": True, "feature:b": False}, ttl=300)

print(cache.stats())
```

## API

```python
cache.set(key, value, ttl=None, nx=False)
cache.get(key, default=None)
cache.delete(*keys)
cache.exists(key)
cache.touch(key, ttl=None)
cache.ttl(key)
cache.mget(keys)
cache.mset(mapping, ttl=None)
cache.incr(key, amount=1)
cache.decr(key, amount=1)
cache.cleanup()
cache.clear()
cache.stats()
```

`ttl=None` uses `default_ttl`. If both are `None`, the entry does not expire.
`ttl=0` expires immediately. Incrementing an existing counter preserves its
current expiration deadline.

## Development

Run the test suite:

```bash
python -m pytest
```

Lint and type-check:

```bash
ruff check .
mypy
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow.

## When not to use litecache

Use Redis or Memcached when you need cross-process sharing, persistence, a
network protocol, distributed coordination, or cache capacity larger than a
single application process can comfortably hold.

## License

MIT
