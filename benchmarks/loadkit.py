"""Shared plumbing for the load tests (``streaming/``, ``callbacks/``).

Starts a server setup on its own CPUs, runs simulated-browser client
processes against it on the other CPUs, samples CPU and memory during the
measure window, and collects what the clients report. Each load test brings
its own app, client and metrics.
"""
from __future__ import annotations

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
from dataclasses import dataclass, field
from typing import Callable, Dict, List

import psutil
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# One Python client process saturates its own CPU at a few hundred browsers.
BROWSERS_PER_CLIENT = 100


@dataclass
class Setup:
    name: str
    backend: str
    server: str
    workers: int
    label: str
    env: Dict[str, str] = field(default_factory=dict)

    @property
    def needs_redis(self):
        return self.workers > 1


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def parse_cpus(spec):
    cpus = set()
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        cpus.update(range(int(lo), int(hi or lo) + 1))
    return sorted(cpus)


def configure(args):
    """Split the machine between server and clients, raise the fd limit."""
    # Every browser holds sockets in both the server and its client process.
    _soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
    cores = psutil.cpu_count()
    args.server_cpus = (
        parse_cpus(args.server_cpus) if args.server_cpus else list(range(cores // 2))
    )
    args.client_cpus = [
        c for c in range(cores) if c not in args.server_cpus
    ] or args.server_cpus


def server_cmd(setup, app, port):
    py = sys.executable
    if setup.server == "gunicorn":
        return [
            py,
            "-m",
            "gunicorn",
            f"{app}:server",
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
        f"{app}:server",
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
def serve(setup, app_dir, app, env, server_cpus):
    """Run ``app_dir/app.py``'s ``server`` under the setup's server and yield
    ``(url, process)`` once every worker is up."""
    port = free_port()
    env = {
        **os.environ,
        **setup.env,
        **env,
        # The server runs from app_dir: without this it would import whichever
        # dash is installed, not the checkout under test.
        "PYTHONPATH": os.pathsep.join(
            p for p in (REPO_ROOT, os.environ.get("PYTHONPATH")) if p
        ),
    }
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        server_cmd(setup, app, port),
        cwd=app_dir,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    with contextlib.suppress(AttributeError):
        psutil.Process(proc.pid).cpu_affinity(server_cpus)
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
                child.cpu_affinity(server_cpus)
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


def pct(values, q):
    if not values:
        return None
    values = sorted(values)
    return round(values[min(len(values) - 1, math.ceil(q * len(values)) - 1)], 1)


def _tree(pid):
    proc = psutil.Process(pid)
    return [proc] + proc.children(recursive=True)


def _start_clients(module, url, browsers, client_args, client_cpus):
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
                module,
                "--url",
                url,
                "--browsers",
                str(share),
                *client_args,
            ],
            cwd=REPO_ROOT,
            stdout=out,
            stderr=err,
        )
        with contextlib.suppress(psutil.Error, AttributeError):
            psutil.Process(proc.pid).cpu_affinity(client_cpus)
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
            cpu = p.cpu_percent(None)
            peak = max(peak, cpu)
            total += cpu
    # Many client processes sharing few CPUs each look idle on their own;
    # what matters is how busy the client CPUs are as a whole.
    return server / 100, mem, max(peak, total / n_client_cpus)


def _collect(clients, on_failure: Callable[[dict, int], None]):
    results = []
    for proc, share, out, err in clients:
        out.seek(0)
        try:
            result = json.loads(out.read())
        except ValueError:
            result = None
        if proc.returncode != 0 or result is None:
            err.seek(0)
            tail = err.read().decode(errors="replace").strip().splitlines()[-1:]
            print(f"  client exited {proc.returncode}: {' '.join(tail)}", flush=True)
            failed: dict = {}
            on_failure(failed, share)
            results.append(failed)
        else:
            results.append(result)
        out.close()
        err.close()
    return results


def run_clients(
    url,
    server,
    browsers,
    module,
    client_args,
    args,
    on_failure,
    grace=90,
):
    """Run ``browsers`` simulated browsers (``module``) against ``url``.

    The clients start together, ramp up over ``args.ramp`` seconds, then
    measure for ``args.duration``. Returns the clients' JSON reports and the
    server/client resource figures sampled inside the measure window. A
    crashed client is reported through ``on_failure(report, its_browsers)``
    so its whole share counts as failed and a point can't look healthy with
    part of its load missing.
    """
    start = time.time() + 2
    measure_from = start + args.ramp
    measure_to = measure_from + args.duration
    clients = _start_clients(
        module,
        url,
        browsers,
        [
            *client_args,
            "--start",
            str(start),
            "--ramp",
            str(args.ramp),
            "--duration",
            str(args.duration),
        ],
        args.client_cpus,
    )
    try:
        server_procs = _tree(server.pid)
        client_procs = [psutil.Process(c[0].pid) for c in clients]
        for p in server_procs + client_procs:
            with contextlib.suppress(psutil.Error):
                p.cpu_percent(None)
        server_cpu: List[float] = []
        client_cpu: List[float] = []
        rss: List[int] = []
        # Work started in the window may run up to the client's own timeout
        # past it; anything later is hung.
        hard_deadline = measure_to + grace
        while any(c[0].poll() is None for c in clients):
            if time.time() > hard_deadline:
                raise RuntimeError(f"clients still running {grace}s after the window")
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
    resources = {
        "server_cpu_cores": round(statistics.mean(server_cpu), 2)
        if server_cpu
        else None,
        "server_rss_mb": round(max(rss) / 2**20) if rss else None,
        "client_cpu_peak_pct": round(max(client_cpu)) if client_cpu else None,
    }
    # Clients near 100% CPU were the bottleneck, not the server.
    resources["client_bound"] = (resources["client_cpu_peak_pct"] or 0) > 85
    return _collect(clients, on_failure), resources


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


def add_common_args(parser, browsers):
    parser.add_argument("--browsers", nargs="*", type=int, default=browsers)
    parser.add_argument(
        "--think", type=float, default=1.0, help="mean seconds between actions"
    )
    parser.add_argument("--ramp", type=float, default=10.0)
    parser.add_argument("--duration", type=float, default=20.0)
    parser.add_argument("--max-p95", type=float, default=1000.0)
    parser.add_argument("--redis-url")
    parser.add_argument("--server-cpus", help="e.g. 0-3 (default: half the machine)")
