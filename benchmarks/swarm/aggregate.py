"""Merge a swarm's agent reports into one result.

    python -m benchmarks.swarm.aggregate results/*.json --out swarm.json

Histograms add up bucket by bucket, so the percentiles are those of every
click in the swarm, not an average of per-agent percentiles. Agents whose
machine ran past 85% CPU (p90 of the window's samples) are flagged: their
browsers were the bottleneck. Agents that got their browsers up after the
shared start are flagged too: their ramp was squeezed and the swarm did not
start together.
"""
import argparse
import json
import os
import sys

try:
    from .histogram import Histogram
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from histogram import Histogram  # type: ignore[no-redef]

COUNTS = ("actions", "errors", "page_errors", "users_failed", "reloads")
AGENT_BOUND_PCT = 85
LATE_S = 1.0


def aggregate(reports):
    hists = {}
    counts = dict.fromkeys(COUNTS, 0)
    errors_by_kind = {}
    for r in reports:
        for k in COUNTS:
            counts[k] += r.get(k, 0)
        for k, n in r.get("errors_by_kind", {}).items():
            errors_by_kind[k] = errors_by_kind.get(k, 0) + n
        for name, data in r.get("histograms", {}).items():
            hists.setdefault(name, Histogram()).merge(Histogram.from_json(data))
    durations = {r["duration"] for r in reports}
    duration = max(durations) if durations else 0
    attempts = counts["actions"] + counts["errors"]
    bound = [
        r["agent"] for r in reports if (r.get("cpu_p90_pct") or 0) > AGENT_BOUND_PCT
    ]
    late = [r["agent"] for r in reports if (r.get("late_s") or 0) > LATE_S]
    return {
        "agents": len(reports),
        "users": sum(r["users"] for r in reports),
        "duration": duration,
        **counts,
        "error_rate": round(counts["errors"] / attempts, 4) if attempts else None,
        "actions_per_s": round(counts["actions"] / duration, 1) if duration else None,
        "errors_by_kind": errors_by_kind,
        "agent_bound": bound,
        "late_agents": late,
        "metrics": {k: h.summary() for k, h in sorted(hists.items())},
        "histograms": {k: h.to_json() for k, h in sorted(hists.items())},
    }


def table(result):
    lines = [
        f"{result['agents']} agents, {result['users']} users, "
        f"{result['actions_per_s']} actions/s, errors {result['error_rate']:.2%}"
        if result["error_rate"] is not None
        else f"{result['agents']} agents, no actions",
        f"{'metric':14} {'count':>8} {'p50':>9} {'p95':>9} {'p99':>9} {'max':>9}",
    ]
    for name, s in result["metrics"].items():
        lines.append(
            f"{name:14} {s['count']:>8} {s['p50']:>7}ms {s['p95']:>7}ms "
            f"{s['p99']:>7}ms {s['max']:>7}ms"
        )
    if result["errors_by_kind"]:
        lines.append(f"errors: {result['errors_by_kind']}")
    if result["users_failed"]:
        lines.append(f"USERS FAILED: {result['users_failed']} never got going")
    if result["agent_bound"]:
        lines.append(
            f"AGENT-BOUND (>{AGENT_BOUND_PCT}% CPU): {', '.join(result['agent_bound'])}"
        )
    if result["late_agents"]:
        lines.append(
            f"LATE (>{LATE_S:.0f}s after the shared start): "
            + ", ".join(result["late_agents"])
        )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("reports", nargs="+")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    reports = []
    for path in args.reports:
        with open(path, encoding="utf-8") as f:
            reports.append(json.load(f))
    result = aggregate(reports)
    print(table(result))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
