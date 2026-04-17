"""
DeepTrace — CountMinSketch: approximate heavy-hitter detection.
Uses deterministic MD5-based hashing (not Python hash()) for reproducibility.
"""
from __future__ import annotations

import hashlib
import random
from typing import List


class CountMinSketch:
    """
    Count-Min Sketch for approximate heavy-hitter (Top-K) detection.
    Memory: depth × width × 4 bytes = 4 × 2048 × 4 = 32 KB (default).
    """

    def __init__(self, width: int = 2048, depth: int = 4) -> None:
        self.width  = width
        self.depth  = depth
        self.table: List[List[int]] = [[0] * width for _ in range(depth)]
        self._seeds = [random.randint(1, 2 ** 31) for _ in range(depth)]

    @staticmethod
    def _stable_hash(key: str) -> int:
        # MD5 used for stable distribution only — NOT for cryptographic security.
        return int(hashlib.md5(key.encode("utf-8", errors="replace")).hexdigest(), 16)

    def _hashes(self, key: str) -> List[int]:
        h = self._stable_hash(key)
        return [(h ^ (self._seeds[i] * (i + 1))) % self.width for i in range(self.depth)]

    def add(self, key: str, count: int = 1) -> None:
        for row, col in enumerate(self._hashes(key)):
            self.table[row][col] += count

    def estimate(self, key: str) -> int:
        """Minimum counter across all rows — standard CMS point query."""
        return min(self.table[row][col] for row, col in enumerate(self._hashes(key)))
