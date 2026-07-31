# litecache

[English](README.md) | [简体中文](README.zh-CN.md)

[![CI](https://github.com/xuehaoweng/litecache/actions/workflows/ci.yml/badge.svg)](https://github.com/xuehaoweng/litecache/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

`litecache` 是一个小巧、线程安全的 Python 进程内缓存组件，支持 TTL
过期和 LRU 淘汰。它提供类似 Redis 或 Memcached 的简洁 API，但无需启动服务器，
也没有任何运行时依赖。

> **注意：** litecache 是进程内缓存。数据不会在多个进程之间共享，并会在进程退出后
> 消失。

## 功能特性

- 线程安全操作
- 支持单个键的 TTL 和全局默认 TTL
- 可配置容量上限，超限时按 LRU 策略淘汰
- 原子整数递增和递减
- 支持 `set(..., nx=True)` 条件写入
- 批量读取和写入
- 提供命中、未命中、淘汰和过期统计
- 无运行时依赖，公共 API 包含完整类型标注

## 安装

```bash
pip install litecache
```

本地开发安装：

```bash
git clone https://github.com/xuehaoweng/litecache.git
cd litecache
python -m pip install -e ".[dev]"
```

## 快速开始

```python
from litecache import LiteCache

cache = LiteCache(max_items=10_000, default_ttl=60)

# 默认在 60 秒后过期
cache.set("user:42", {"name": "Ada"})
user = cache.get("user:42")

# 仅在键不存在时写入，并在 5 秒后过期
created = cache.set("lock:job", True, ttl=5, nx=True)

# 原子计数
cache.incr("page:views")

# 批量写入
cache.mset({"feature:a": True, "feature:b": False}, ttl=300)

print(cache.stats())
```

## API

```python
cache.set(key, value, ttl=None, nx=False)  # 写入值
cache.get(key, default=None)               # 读取值
cache.delete(*keys)                        # 删除键，返回成功删除的数量
cache.exists(key)                          # 判断键是否存在
cache.touch(key, ttl=None)                 # 刷新过期时间
cache.ttl(key)                             # 获取剩余存活秒数
cache.mget(keys)                           # 批量读取
cache.mset(mapping, ttl=None)              # 批量写入
cache.incr(key, amount=1)                  # 原子递增
cache.decr(key, amount=1)                  # 原子递减
cache.cleanup()                            # 主动清理所有过期项
cache.clear()                              # 清空缓存
cache.stats()                              # 获取统计快照
```

`ttl=None` 表示使用 `default_ttl`。如果二者均为 `None`，缓存项不会自动过期。
`ttl=0` 表示立即过期。对已有计数器执行递增或递减时，会保留其当前的过期时间。

## 开发

运行测试：

```bash
python -m pytest
```

检查代码风格和类型：

```bash
ruff check .
mypy
```

贡献流程请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 不适用的场景

如果需要跨进程共享、持久化、网络协议、分布式协调，或者缓存容量超过单个应用进程
能够轻松承载的范围，请使用 Redis 或 Memcached。

## 开源协议

MIT
