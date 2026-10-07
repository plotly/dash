"""Streaming-callback load test: how many browsers each backend serves.

For each server setup (backend x server x workers) and each browser count,
start the server, run simulated browsers against it (``client.py``, spread
over several processes) and record frame latency, time to first frame,
errors and CPU. A setup stops climbing once it saturates (p95 latency over
``--max-p95`` ms or errors over 1%), since higher counts only add noise.

    python -m benchmarks.streaming.load --out benchmarks/streaming/results.json
    python -m benchmarks.streaming.load --setup fastapi-uvicorn-w1 --browsers 100 500

Multi-worker setups need shared storage across processes; pass
``--redis-url`` (they are skipped without it). The server and the clients
are pinned to separate CPUs (``--server-cpus``) so the clients' own load
does not show up as server latency, and each point records the clients'
peak CPU so a client-bound point can be spotted.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import asdict

from benchmarks import loadkit
from benchmarks.loadkit import Setup, pct

HERE = os.path.dirname(os.path.abspath(__file__))

SETUPS = [
    Setup(
        "flask-gunicorn-w1",
        "flask",
        "gunicorn",
        1,
        "Flask, gunicorn 1 worker x 8 threads",
    ),
    Setup(
        "flask-gunicorn-w4",
        "flask",
        "gunicorn",
        4,
        "Flask, gunicorn 4 workers x 8 threads",
    ),
    Setup("fastapi-uvicorn-w1", "fastapi", "uvicorn", 1, "FastAPI, uvicorn 1 worker"),
    Setup("fastapi-uvicorn-w4", "fastapi", "uvicorn", 4, "FastAPI, uvicorn 4 workers"),
    Setup("quart-uvicorn-w1", "quart", "uvicorn", 1, "Quart, uvicorn 1 worker"),
    Setup("quart-uvicorn-w4", "quart", "uvicorn", 4, "Quart, uvicorn 4 workers"),
]
SETUPS_BY_NAME = {s.name: s for s in SETUPS}
COUNTS = ("streams", "frames", "errors", "incomplete", "failed_browsers")


def _failed(report, share):
    report.update(errors=share, failed_browsers=share)


def run_point(setup, browsers, args):
    env = {
        "LOAD_BACKEND": setup.backend,
        "LOAD_FRAMES": str(args.frames),
        "LOAD_INTERVAL": str(args.interval),
        "LOAD_SECRET": "load-test",
        "LOAD_REDIS_URL": args.redis_url if setup.needs_redis else "",
    }
    with loadkit.serve(setup, HERE, "load_app", env, args.server_cpus) as (
        url,
        server,
    ):
        # Streams started in the window may run up to the client's 60 s
        # stream timeout past it.
        reports, resources = loadkit.run_clients(
            url,
            server,
            browsers,
            "benchmarks.streaming.client",
            ["--frames", str(args.frames), "--think", str(args.think)],
            args,
            _failed,
        )
    lat = [x for r in reports for x in r.get("latency_ms", [])]
    first = [x for r in reports for x in r.get("first_frame_ms", [])]
    counts = {k: sum(r.get(k, 0) for r in reports) for k in COUNTS}
    attempts = counts["streams"] + counts["errors"]
    error_rate = (
        (counts["errors"] + counts["incomplete"]) / attempts if attempts else 1.0
    )
    point = {
        "browsers": browsers,
        "latency_p50_ms": pct(lat, 0.5),
        "latency_p95_ms": pct(lat, 0.95),
        "latency_p99_ms": pct(lat, 0.99),
        "first_frame_p50_ms": pct(first, 0.5),
        "first_frame_p95_ms": pct(first, 0.95),
        "frames_per_s": round(counts["frames"] / args.duration, 1),
        "streams_per_s": round(counts["streams"] / args.duration, 2),
        **counts,
        "error_rate": round(error_rate, 4),
        **resources,
    }
    point["saturated"] = bool(
        error_rate > 0.01 or (point["latency_p95_ms"] or math.inf) > args.max_p95
    )
    return point


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--setup", nargs="*", choices=list(SETUPS_BY_NAME))
    loadkit.add_common_args(parser, [25, 50, 100, 250, 500, 1000, 2000, 4000])
    parser.add_argument("--frames", type=int, default=20)
    parser.add_argument(
        "--interval", type=float, default=0.1, help="seconds between frames"
    )
    parser.add_argument("--out", default=os.path.join(HERE, "results.json"))
    args = parser.parse_args(argv)
    loadkit.configure(args)

    setups = [SETUPS_BY_NAME[n] for n in args.setup] if args.setup else SETUPS
    results = {
        "kind": "streaming_load",
        "meta": loadkit.machine_info(args),
        "params": {
            k: getattr(args, k)
            for k in ("frames", "interval", "think", "ramp", "duration", "max_p95")
        },
        "setups": [],
    }
    for setup in setups:
        if setup.needs_redis and not args.redis_url:
            print(f"skip {setup.name}: multi-worker needs --redis-url", flush=True)
            continue
        entry = {
            **{k: v for k, v in asdict(setup).items() if k != "env"},
            "storage": "redis" if setup.needs_redis else "local",
            "points": [],
        }
        results["setups"].append(entry)
        for browsers in sorted(args.browsers):
            try:
                point = run_point(setup, browsers, args)
            except RuntimeError as err:
                print(f"{setup.name} @ {browsers}: {err}", flush=True)
                break
            entry["points"].append(point)
            print(
                f"{setup.name:20} {browsers:5} browsers  p50 {point['latency_p50_ms']}ms"
                f"  p95 {point['latency_p95_ms']}ms  first {point['first_frame_p50_ms']}ms"
                f"  err {point['error_rate']:.2%}  server {point['server_cpu_cores']} cores"
                f"  client peak {point['client_cpu_peak_pct']}%"
                + ("  SATURATED" if point["saturated"] else "")
                + ("  CLIENT-BOUND" if point["client_bound"] else ""),
                flush=True,
            )
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=1)
            # Past either limit the next counts measure nothing useful: a
            # saturated server only gets worse, and client-bound numbers are
            # the load generator's, not the server's.
            if point["saturated"] or point["client_bound"]:
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
