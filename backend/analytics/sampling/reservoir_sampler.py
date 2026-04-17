"""
DeepTrace — ReservoirSampler: Algorithm R.
O(reservoir_size) memory regardless of total input size.
"""
from __future__ import annotations

import random
from typing import List


class ReservoirSampler:
    def __init__(self, size: int = 1000) -> None:
        self.size:    int        = size
        self.samples: List[dict] = []
        self.count:   int        = 0

    def add(self, item: dict) -> None:
        self.count += 1
        if len(self.samples) < self.size:
            self.samples.append(item)
        else:
            idx = random.randint(0, self.count - 1)
            if idx < self.size:
                self.samples[idx] = item
