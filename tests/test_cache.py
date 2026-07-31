import threading
import unittest

from litecache import LiteCache


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class LiteCacheTests(unittest.TestCase):
    def test_set_get_delete(self):
        cache = LiteCache()
        self.assertTrue(cache.set("name", "litecache"))
        self.assertEqual(cache.get("name"), "litecache")
        self.assertTrue(cache.exists("name"))
        self.assertEqual(cache.delete("name", "missing"), 1)
        self.assertIsNone(cache.get("name"))

    def test_ttl_expiration(self):
        clock = Clock()
        cache = LiteCache(timer=clock)
        cache.set("token", "abc", ttl=10)
        clock.now = 9
        self.assertEqual(cache.get("token"), "abc")
        clock.now = 10
        self.assertIsNone(cache.get("token"))
        self.assertEqual(cache.stats().expirations, 1)

    def test_lru_eviction(self):
        cache = LiteCache(max_items=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.get("a")
        cache.set("c", 3)
        self.assertNotIn("b", cache)
        self.assertEqual(cache.get("a"), 1)
        self.assertEqual(cache.stats().evictions, 1)

    def test_nx_and_touch(self):
        clock = Clock()
        cache = LiteCache(timer=clock)
        self.assertTrue(cache.set("a", 1, nx=True))
        self.assertFalse(cache.set("a", 2, nx=True))
        self.assertTrue(cache.touch("a", ttl=5))
        clock.now = 6
        self.assertIsNone(cache.get("a"))

    def test_multi_and_counter_operations(self):
        cache = LiteCache()
        cache.mset({"a": 1, "b": 2})
        self.assertEqual(cache.mget(["a", "b", "c"]), {"a": 1, "b": 2, "c": None})
        self.assertEqual(cache.incr("counter"), 1)
        self.assertEqual(cache.incr("counter", 4), 5)
        self.assertEqual(cache.decr("counter", 2), 3)

    def test_increment_preserves_existing_ttl(self):
        clock = Clock()
        cache = LiteCache(default_ttl=10, timer=clock)
        cache.set("counter", 1)
        clock.now = 8
        self.assertEqual(cache.incr("counter"), 2)
        clock.now = 10
        self.assertIsNone(cache.get("counter"))

    def test_concurrent_increments_are_atomic(self):
        cache = LiteCache()

        def add():
            for _ in range(1000):
                cache.incr("counter")

        threads = [threading.Thread(target=add) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(cache.get("counter"), 4000)

    def test_validation_and_type_errors(self):
        with self.assertRaises(ValueError):
            LiteCache(max_items=0)
        cache = LiteCache()
        with self.assertRaises(ValueError):
            cache.set("a", 1, ttl=-1)
        cache.set("text", "hello")
        with self.assertRaises(TypeError):
            cache.incr("text")


if __name__ == "__main__":
    unittest.main()
