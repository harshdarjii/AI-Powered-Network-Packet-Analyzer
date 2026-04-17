"""
DeepTrace — FixedSketch: reservoir-based percentile / threshold estimation.
"""
from __future__ import annotations

import math
import random
from typing import List, Optional


class FixedSketch:
    """
    Reservoir-based sketch for percentile estimation.
    Keeps exactly `size` random samples via reservoir sampling.
    Memory: ~80 KB at default size of 10 000.
    """
    __slots__ = ("size", "samples", "count", "_sorted_cache")

    def __init__(self, size: int = 10_000) -> None:
        self.size:          int                    = size
        self.samples:       List[float]            = []
        self.count:         int                    = 0
        self._sorted_cache: Optional[List[float]]  = None

    def update(self, value: float) -> None:
        self.count        += 1
        self._sorted_cache = None
        if len(self.samples) < self.size:
            self.samples.append(value)
        else:
            idx = random.randint(0, self.count - 1)
            if idx < self.size:
                self.samples[idx] = value

    def percentile(self, pct: float) -> float:
        if not self.samples:
            return 0.0
        if self._sorted_cache is None:
            self._sorted_cache = sorted(self.samples)
        s   = self._sorted_cache
        idx = (pct / 100.0) * (len(s) - 1)
        lo  = int(idx)
        hi  = min(lo + 1, len(s) - 1)
        return s[lo] + (s[hi] - s[lo]) * (idx - lo)

    def iqr_threshold(self, multiplier: float = 1.5) -> float:
        q1  = self.percentile(25)
        q3  = self.percentile(75)
        return q3 + multiplier * (q3 - q1)

    def zscore_threshold(self, z: float = 2.5) -> float:
        s = self.samples
        if len(s) < 2:
            return self.percentile(90)
        m  = sum(s) / len(s)
        sd = math.sqrt(sum((x - m) ** 2 for x in s) / len(s))
        return m + z * sd

    def median_of_means(self, buckets: int = 7) -> float:
        """
        Split samples into `buckets` groups, compute each mean, return the median.
        More outlier-resistant than a plain mean.
        """
        s = self.samples
        if len(s) < buckets:
            return sum(s) / len(s) if s else 0.0
        size  = len(s) // buckets
        means = sorted(
            sum(s[i * size: (i + 1) * size]) / size for i in range(buckets)
        )
        return means[buckets // 2]

    def dynamic(
        self,
        iqr_mult:    float = 1.5,
        z:           float = 2.5,
        floor:       float = 0.0,
        min_samples: int   = 50,
    ) -> float:
        """
        Returns the lower of IQR fence and Z-score threshold (anchored on
        median-of-means for outlier resistance).

        If fewer than min_samples have been collected the sketch does not yet
        have enough data to compute meaningful statistics, so the floor value
        is returned directly. This replaces the old warmup phase: thresholds
        start conservative (floor) and become progressively accurate as more
        data arrives — detection fires from the very first flow.
        """
        if len(self.samples) < min_samples:
            return floor

        iqr_t = self.iqr_threshold(iqr_mult)
        mom   = self.median_of_means()
        s     = self.samples
        if len(s) >= 2:
            sd  = math.sqrt(sum((x - mom) ** 2 for x in s) / len(s))
            z_t = mom + z * sd
        else:
            z_t = self.zscore_threshold(z)
        return max(floor, min(iqr_t, z_t))
