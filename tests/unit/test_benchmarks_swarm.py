"""The swarm's histograms must merge to the same percentiles as the raw data."""
import math
import random

from benchmarks.swarm.aggregate import aggregate
from benchmarks.swarm.histogram import GROWTH, Histogram


def _exact(values, q):
    return sorted(values)[math.ceil(q * len(values)) - 1]


def test_quantiles_within_bucket_resolution():
    rng = random.Random(1)
    values = [rng.lognormvariate(3, 1) for _ in range(5000)]
    h = Histogram()
    for v in values:
        h.add(v)
    for q in (0.5, 0.95, 0.99):
        assert abs(h.quantile(q) / _exact(values, q) - 1) <= GROWTH - 1
    assert h.count == 5000


def test_merged_agents_match_one_histogram():
    rng = random.Random(2)
    parts = [[rng.uniform(1, 500) for _ in range(300)] for _ in range(4)]
    whole = Histogram()
    reports = []
    for i, part in enumerate(parts):
        h = Histogram()
        for v in part:
            h.add(v)
            whole.add(v)
        reports.append(
            {
                "agent": f"a{i}",
                "users": 10,
                "duration": 60,
                "actions": len(part),
                "errors": i,
                "cpu_p90_pct": 90 if i == 3 else 40,
                "late_s": 3 if i == 2 else 0,
                "histograms": {"http": h.to_json()},
            }
        )
    result = aggregate(reports)
    assert result["metrics"]["http"] == whole.summary()
    assert result["actions"] == 1200
    assert result["errors"] == 6
    assert result["users"] == 40
    assert result["agent_bound"] == ["a3"]
    assert result["late_agents"] == ["a2"]


def test_empty_histogram():
    assert Histogram().quantile(0.5) is None
    assert Histogram.from_json(Histogram().to_json()).summary()["count"] == 0


def test_quantile_edges():
    one = Histogram()
    one.add(7.3)
    assert one.summary()["p50"] == one.summary()["p99"] == 7.3
    same = Histogram()
    for _ in range(10):
        same.add(42.0)
    assert same.quantile(0.5) == same.quantile(0.99) == 42.0
    tiny = Histogram()
    tiny.add(0)
    assert tiny.quantile(0.5) == 0.0
