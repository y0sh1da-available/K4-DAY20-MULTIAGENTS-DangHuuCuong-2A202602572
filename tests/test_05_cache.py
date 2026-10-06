"""Unit tests for Bonus 6c TaskResultCache."""

from lab.cache import TaskResultCache


def test_cache_put_get(tmp_path):
    cache = TaskResultCache(cache_dir=tmp_path)
    key = cache.compute_key("code-learn", "baseline", "sample content")
    
    assert cache.get(key) is None
    assert cache.stats()["misses"] == 1
    
    data = {"passed": 6, "total": 10, "score": 0.6}
    cache.put(key, data)
    
    cached = cache.get(key)
    assert cached == data
    assert cache.stats()["hits"] == 1
    assert cache.stats()["hit_ratio"] == 0.5


def test_cache_disk_persistence(tmp_path):
    cache1 = TaskResultCache(cache_dir=tmp_path)
    key = cache1.compute_key("data-eval", "subagents", "query")
    cache1.put(key, {"answer": 42})
    
    # Reload fresh cache pointing to same directory
    cache2 = TaskResultCache(cache_dir=tmp_path)
    res = cache2.get(key)
    assert res == {"answer": 42}
    assert cache2.stats()["hits"] == 1

