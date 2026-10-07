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
import contextlib
import json
import math
import os
import platform
import resource
import socket
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass

import psutil
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
BROWSERS_PER_CLIENT = 100


@dataclass
class Setup:
    name: str
    backend: str
    server: str
    workers: int
    label: str

    @property
    def needs_redis(self):
        return self.workers > 1


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


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _cpus(spec):
    cpus = set()
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        cpus.update(range(int(lo), int(hi or lo) + 1))
    return sorted(cpus)


def _server_cmd(setup, port):
    py = sys.executable
    if setup.server == "gunicorn":
        return [
            py,
            "-m",
            "gunicorn",
            "load_app:server",
            "--bind",
            f"127.0.0.1:{port}",
            "--workers",
            str(setup.workers),
            "--worker-class",
            "gthread",
            "--threads",
            "8",
            "--timeout",
            "120",
            "--backlog",
            "4096",
        ]
    return [
        py,
        "-m",
        "uvicorn",
        "load_app:server",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--workers",
        str(setup.workers),
        "--log-level",
        "warning",
        "--backlog",
        "4096",
    ]


@contextlib.contextmanager
def serve(setup, args):
    port = _free_port()
    env = dict(os.environ)
    env.update(
        LOAD_BACKEND=setup.backend,
        LOAD_FRAMES=str(args.frames),
        LOAD_INTERVAL=str(args.interval),
        LOAD_SECRET="load-test",
        LOAD_REDIS_URL=args.redis_url if setup.needs_redis else "",
        # The server runs from this directory: without this it would import
        # whichever dash is installed, not the checkout under test.
        PYTHONPATH=os.pathsep.join(
            p for p in (REPO_ROOT, os.environ.get("PYTHONPATH")) if p
        ),
    )
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        _server_cmd(setup, port),
        cwd=HERE,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    with contextlib.suppress(AttributeError):
        psutil.Process(proc.pid).cpu_affinity(args.server_cpus)
    url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"{setup.name} exited with {proc.returncode}")
            with contextlib.suppress(requests.RequestException):
                if requests.get(url, timeout=1).ok:
                    break
            time.sleep(0.3)
        else:
            raise RuntimeError(f"{setup.name} never came up")
        # The first worker answering does not mean the others are up yet;
        # wait for all of them so CPU, memory and pinning cover every worker.
        # uvicorn runs a single worker in the main process, without forking.
        forks = setup.workers if setup.server == "gunicorn" or setup.workers > 1 else 0
        while (
            len(psutil.Process(proc.pid).children(recursive=True)) < forks
            and time.monotonic() < deadline
        ):
            time.sleep(0.3)
        time.sleep(1)
        for child in psutil.Process(proc.pid).children(recursive=True):
            with contextlib.suppress(psutil.Error, AttributeError):
                child.cpu_affinity(args.server_cpus)
        yield url, proc
    finally:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, 15)
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(proc.pid, 9)
            proc.wait()


def _tree(pid):
    proc = psutil.Process(pid)
    return [proc] + proc.children(recursive=True)


def _pct(values, q):
    if not values:
        return None
    values = sorted(values)
    return round(values[min(len(values) - 1, math.ceil(q * len(values)) - 1)], 1)


def _start_clients(url, browsers, start, args):
    n_clients = max(1, math.ceil(browsers / BROWSERS_PER_CLIENT))
    clients = []
    for i in range(n_clients):
        share = browsers // n_clients + (1 if i < browsers % n_clients else 0)
        # Files, not pipes: nothing reads a pipe until the clients exit, and a
        # full pipe would block them forever.
        out = tempfile.TemporaryFile()  # pylint: disable=consider-using-with
        err = tempfile.TemporaryFile()  # pylint: disable=consider-using-with
        proc = subprocess.Popen(  # pylint: disable=consider-using-with
            [
                sys.executable,
                "-m",
                "benchmarks.streaming.client",
                "--url",
                url,
                "--browsers",
                str(share),
                "--frames",
                str(args.frames),
                "--think",
                str(args.think),
                "--start",
                str(start),
                "--ramp",
                str(args.ramp),
                "--duration",
                str(args.duration),
            ],
            cwd=REPO_ROOT,
            stdout=out,
            stderr=err,
        )
        with contextlib.suppress(psutil.Error, AttributeError):
            psutil.Process(proc.pid).cpu_affinity(args.client_cpus)
        clients.append((proc, share, out, err))
    return clients


def _sample(server_procs, client_procs, n_client_cpus):
    server, mem = 0.0, 0
    for p in server_procs:
        with contextlib.suppress(psutil.Error):
            server += p.cpu_percent(None)
            mem += p.memory_info().rss
    peak, total = 0.0, 0.0
    for p in client_procs:
        with contextlib.suppress(psutil.Error):
            pct = p.cpu_percent(None)
            peak = max(peak, pct)
            total += pct
    # Many client processes sharing few CPUs each look idle on their own;
    # what matters is how busy the client CPUs are as a whole.
    return server / 100, mem, max(peak, total / n_client_cpus)


def _collect(clients):
    merged = {"latency_ms": [], "first_frame_ms": []}
    counts = {
        "streams": 0,
        "frames": 0,
        "errors": 0,
        "incomplete": 0,
        "failed_browsers": 0,
    }
    for proc, share, out, err in clients:
        out.seek(0)
        try:
            result = json.loads(out.read())
        except ValueError:
            result = None
        if proc.returncode != 0 or result is None:
            # A crashed client's browsers all count as failed, so the point
            # can't look healthy with part of its load missing.
            err.seek(0)
            tail = err.read().decode(errors="replace").strip().splitlines()[-1:]
            print(f"  client exited {proc.returncode}: {' '.join(tail)}", flush=True)
            counts["errors"] += share
            counts["failed_browsers"] += share
        else:
            for key in merged:
                merged[key] += result.get(key, [])
            for key in counts:
                counts[key] += result.get(key, 0)
        out.close()
        err.close()
    return merged, counts


def run_point(setup, browsers, args):
    with serve(setup, args) as (url, server):
        start = time.time() + 2
        measure_from = start + args.ramp
        measure_to = measure_from + args.duration
        clients = _start_clients(url, browsers, start, args)
        try:
            server_procs = _tree(server.pid)
            client_procs = [psutil.Process(c[0].pid) for c in clients]
            for p in server_procs + client_procs:
                with contextlib.suppress(psutil.Error):
                    p.cpu_percent(None)
            server_cpu, client_cpu, rss = [], [], []
            # Streams started in the window may run up to the client's 60 s
            # stream timeout past it; anything later is hung.
            hard_deadline = measure_to + 90
            while any(c[0].poll() is None for c in clients):
                if time.time() > hard_deadline:
                    raise RuntimeError(
                        f"clients still running {hard_deadline - measure_to:.0f}s after the window"
                    )
                time.sleep(1)
                if not measure_from <= time.time() <= measure_to:
                    continue
                cores, mem, client = _sample(
                    server_procs, client_procs, len(args.client_cpus)
                )
                server_cpu.append(cores)
                rss.append(mem)
                client_cpu.append(client)
        finally:
            for proc, *_ in clients:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()

    merged, counts = _collect(clients)
    attempts = counts["streams"] + counts["errors"]
    error_rate = (
        (counts["errors"] + counts["incomplete"]) / attempts if attempts else 1.0
    )
    lat = merged["latency_ms"]
    point = {
        "browsers": browsers,
        "latency_p50_ms": _pct(lat, 0.5),
        "latency_p95_ms": _pct(lat, 0.95),
        "latency_p99_ms": _pct(lat, 0.99),
        "first_frame_p50_ms": _pct(merged["first_frame_ms"], 0.5),
        "first_frame_p95_ms": _pct(merged["first_frame_ms"], 0.95),
        "frames_per_s": round(counts["frames"] / args.duration, 1),
        "streams_per_s": round(counts["streams"] / args.duration, 2),
        **counts,
        "error_rate": round(error_rate, 4),
        "server_cpu_cores": round(statistics.mean(server_cpu), 2)
        if server_cpu
        else None,
        "server_rss_mb": round(max(rss) / 2**20) if rss else None,
        "client_cpu_peak_pct": round(max(client_cpu)) if client_cpu else None,
    }
    point["saturated"] = bool(
        error_rate > 0.01 or (point["latency_p95_ms"] or math.inf) > args.max_p95
    )
    # Clients near 100% CPU were the bottleneck, not the server.
    point["client_bound"] = (point["client_cpu_peak_pct"] or 0) > 85
    return point


def machine_info(args):
    cpu = platform.processor()
    with contextlib.suppress(OSError):
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("model name"):
                    cpu = line.split(":", 1)[1].strip()
                    break
    sha = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    import dash  # pylint: disable=import-outside-toplevel

    return {
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "commit": sha,
        "dash_version": dash.__version__,
        "python": platform.python_version(),
        "cpu": cpu,
        "cores": psutil.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total / 2**30),
        "server_cpus": len(args.server_cpus),
        "client_cpus": len(args.client_cpus),
        "runner": os.environ.get("BENCH_RUNNER", "local"),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--setup", nargs="*", choices=list(SETUPS_BY_NAME))
    parser.add_argument(
        "--browsers",
        nargs="*",
        type=int,
        default=[25, 50, 100, 250, 500, 1000, 2000, 4000],
    )
    parser.add_argument("--frames", type=int, default=20)
    parser.add_argument(
        "--interval", type=float, default=0.1, help="seconds between frames"
    )
    parser.add_argument(
        "--think", type=float, default=1.0, help="mean seconds between streams"
    )
    parser.add_argument("--ramp", type=float, default=10.0)
    parser.add_argument("--duration", type=float, default=20.0)
    parser.add_argument("--max-p95", type=float, default=1000.0)
    parser.add_argument("--redis-url")
    parser.add_argument("--server-cpus", help="e.g. 0-3 (default: half the machine)")
    parser.add_argument("--out", default=os.path.join(HERE, "results.json"))
    args = parser.parse_args(argv)

    # Every browser holds sockets in both the server and its client process.
    _soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))

    cores = psutil.cpu_count()
    args.server_cpus = (
        _cpus(args.server_cpus) if args.server_cpus else list(range(cores // 2))
    )
    args.client_cpus = [
        c for c in range(cores) if c not in args.server_cpus
    ] or args.server_cpus

    setups = [SETUPS_BY_NAME[n] for n in args.setup] if args.setup else SETUPS
    results = {
        "kind": "streaming_load",
        "meta": machine_info(args),
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
            **asdict(setup),
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
