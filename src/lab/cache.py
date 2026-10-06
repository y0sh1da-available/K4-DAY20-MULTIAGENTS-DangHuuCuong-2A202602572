"""Bonus Challenge 6c: Task Result Caching module.

Caches agent execution results and intermediate subagent outputs using cryptographic
task-content hashing to prevent redundant LLM inference and avoid wasteful API consumption.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


class TaskResultCache:
    """Persistent and in-memory cache for task results and subagent calls."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path(".cache/agent_results")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.hits = 0
        self.misses = 0

    def compute_key(self, task_name: str, condition: str, content: str) -> str:
        """Compute SHA256 cache key based on task identity and input content."""
        hasher = hashlib.sha256()
        hasher.update(task_name.encode("utf-8"))
        hasher.update(condition.encode("utf-8"))
        hasher.update(content.encode("utf-8"))
        return hasher.hexdigest()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result by key."""
        if key in self.memory_cache:
            self.hits += 1
            return self.memory_cache[key]

        disk_path = self.cache_dir / f"{key}.json"
        if disk_path.exists():
            try:
                data = json.loads(disk_path.read_text(encoding="utf-8"))
                self.memory_cache[key] = data
                self.hits += 1
                return data
            except Exception:
                pass

        self.misses += 1
        return None

    def put(self, key: str, result: Dict[str, Any]) -> None:
        """Store result in memory and on disk."""
        self.memory_cache[key] = result
        disk_path = self.cache_dir / f"{key}.json"
        try:
            disk_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def stats(self) -> Dict[str, Any]:
        """Return cache hit/miss statistics and hit-ratio."""
        total = self.hits + self.misses
        hit_ratio = (self.hits / total) if total > 0 else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_ratio": round(hit_ratio, 4)
        }

