"""Callback load test: plain HTTP callbacks vs websocket callbacks, by backend.

For each server setup (backend x server x workers x transport) and each
browser count, start the server, run simulated browsers that click and wait
for the callback (``client.py``), and record the round trip, throughput,
errors and CPU. Flask only has HTTP; FastAPI and Quart run both transports.
A setup stops climbing once it saturates (p95 over ``--max-p95`` ms or errors
over 1%).

    python -m benchmarks.callbacks.load --out benchmarks/callbacks/results.json
    python -m benchmarks.callbacks.load --setup fastapi-uvicorn-w1-ws --browsers 100 500
    python -m benchmarks.callbacks.load --kind async --work-ms 50

Plain callbacks keep no state between requests, so multi-worker setups need
no shared storage.
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


def _setups():
    servers = [
        ("flask", "gunicorn", "Flask, gunicorn", " x 8 threads", ["http"]),
        ("fastapi", "uvicorn", "FastAPI, uvicorn", "", ["http", "ws"]),
        ("quart", "uvicorn", "Quart, uvicorn", "", ["http", "ws"]),
    ]
    setups = []
    for backend, server, label, threads, transports in servers:
        for workers in (1, 4):
            for transport in transports:
                plural = "s" if workers > 1 else ""
                setups.append(
                    Setup(
                        f"{backend}-{server}-w{workers}-{transport}",
                        backend,
                        server,
                        workers,
                        f"{label} {workers} worker{plural}{threads}, "
                        + ("websocket" if transport == "ws" else "HTTP"),
                        env={"LOAD_TRANSPORT": transport},
                    )
                )
    return setups


SETUPS = _setups()
SETUPS_BY_NAME = {s.name: s for s in SETUPS}
COUNTS = ("calls", "errors", "failed_browsers")


def _failed(report, share):
    report.update(errors=share, failed_browsers=share)


def run_point(setup, browsers, args):
    env = {
        "LOAD_BACKEND": setup.backend,
        "LOAD_KIND": args.kind,
        "LOAD_WORK_MS": str(args.work_ms),
    }
    with loadkit.serve(setup, HERE, "load_app", env, args.server_cpus) as (
        url,
        server,
    ):
        reports, resources = loadkit.run_clients(
            url,
            server,
            browsers,
            "benchmarks.callbacks.client",
            [
                "--transport",
                setup.env["LOAD_TRANSPORT"],
                "--think",
                str(args.think),
            ],
            args,
            _failed,
            # The last click may hit the client's timeout, its 1 s backoff,
            # then a full think.
            grace=30 + 1 + 2 * args.think + 10,
        )
    rtt = [x for r in reports for x in r.get("rtt_ms", [])]
    counts = {k: sum(r.get(k, 0) for r in reports) for k in COUNTS}
    attempts = counts["calls"] + counts["errors"]
    error_rate = counts["errors"] / attempts if attempts else 1.0
    point = {
        "browsers": browsers,
        "rtt_p50_ms": pct(rtt, 0.5),
        "rtt_p95_ms": pct(rtt, 0.95),
        "rtt_p99_ms": pct(rtt, 0.99),
        "calls_per_s": round(counts["calls"] / args.duration, 1),
        **counts,
        "error_rate": round(error_rate, 4),
        **resources,
    }
    # Browsers that never loaded took their load away from the point.
    point["saturated"] = bool(
        error_rate > 0.01
        or (point["rtt_p95_ms"] or math.inf) > args.max_p95
        or counts["failed_browsers"]
    )
    return point


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--setup", nargs="*", choices=list(SETUPS_BY_NAME))
    loadkit.add_common_args(parser, [25, 50, 100, 250, 500, 1000, 2000, 4000])
    parser.add_argument("--kind", choices=["sync", "async"], default="sync")
    parser.add_argument("--work-ms", type=float, default=0.0, help="work per callback")
    parser.add_argument("--out", default=os.path.join(HERE, "results.json"))
    args = parser.parse_args(argv)
    loadkit.configure(args)

    setups = [SETUPS_BY_NAME[n] for n in args.setup] if args.setup else SETUPS
    results = {
        "kind": "callback_load",
        "meta": loadkit.machine_info(args),
        "params": {
            k: getattr(args, k)
            for k in ("kind", "work_ms", "think", "ramp", "duration", "max_p95")
        },
        "setups": [],
    }
    for setup in setups:
        entry = {
            **{k: v for k, v in asdict(setup).items() if k != "env"},
            "transport": setup.env["LOAD_TRANSPORT"],
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
                f"{setup.name:24} {browsers:5} browsers  p50 {point['rtt_p50_ms']}ms"
                f"  p95 {point['rtt_p95_ms']}ms  {point['calls_per_s']} calls/s"
                f"  err {point['error_rate']:.2%}  server {point['server_cpu_cores']} cores"
                f"  client peak {point['client_cpu_peak_pct']}%"
                + ("  SATURATED" if point["saturated"] else "")
                + ("  CLIENT-BOUND" if point["client_bound"] else ""),
                flush=True,
            )
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=1)
            if point["saturated"] or point["client_bound"]:
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
