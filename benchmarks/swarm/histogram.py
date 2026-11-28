"""Log-bucketed latency histograms that merge exactly across agents.

Bucket ``i`` covers ``[GROWTH**i, GROWTH**(i+1))`` milliseconds, so every
recorded value is known to within 2%. Agents ship bucket counts instead of
raw samples: fifty machines' results stay small and add up bucket by bucket.
"""
import math

GROWTH = 1.02
_LOG = math.log(GROWTH)


class Histogram:
    def __init__(self):
        self.buckets = {}
        self.count = 0
        self.total = 0.0
        self.min = math.inf
        self.max = 0.0

    def add(self, ms):
        ms = max(ms, 0.001)
        i = math.floor(math.log(ms) / _LOG)
        self.buckets[i] = self.buckets.get(i, 0) + 1
        self.count += 1
        self.total += ms
        self.min = min(self.min, ms)
        self.max = max(self.max, ms)

    def merge(self, other):
        for i, n in other.buckets.items():
            self.buckets[i] = self.buckets.get(i, 0) + n
        self.count += other.count
        self.total += other.total
        self.min = min(self.min, other.min)
        self.max = max(self.max, other.max)
        return self

    def quantile(self, q):
        if not self.count:
            return None
        rank = max(1, math.ceil(q * self.count))
        seen = 0
        for i in sorted(self.buckets):
            seen += self.buckets[i]
            if seen >= rank:
                # Middle of the bucket, clamped to what was actually seen.
                mid = GROWTH ** (i + 0.5)
                return round(min(max(mid, self.min), self.max), 1)
        return round(self.max, 1)

    def summary(self):
        return {
            "count": self.count,
            "mean": round(self.total / self.count, 1) if self.count else None,
            "p50": self.quantile(0.5),
            "p95": self.quantile(0.95),
            "p99": self.quantile(0.99),
            "max": round(self.max, 1) if self.count else None,
        }

    def to_json(self):
        return {
            "buckets": {str(i): n for i, n in sorted(self.buckets.items())},
            "count": self.count,
            "total": self.total,
            "min": self.min if self.count else None,
            "max": self.max,
        }

    @classmethod
    def from_json(cls, data):
        h = cls()
        h.buckets = {int(i): n for i, n in data["buckets"].items()}
        h.count = data["count"]
        h.total = data["total"]
        h.min = data["min"] if data["min"] is not None else math.inf
        h.max = data["max"]
        return h
