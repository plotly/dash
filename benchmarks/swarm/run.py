"""Run a browser swarm: agents on many machines, one shared start.

Each step runs every agent with ``--users`` headless browser users against
``--target`` (all agents start at the same wall-clock time and ramp
together), then merges their reports. Steps climb until the swarm sees
errors over 1% or a p95 over ``--max-p95`` ms.

Agents run either here (``--local N``: N agent processes, for trying it out)
or on remote hosts over SSH (``--hosts hosts.txt``, one ``user@host`` per
line), each in the agent image, which every host must have pulled::

    python -m benchmarks.swarm.run --target http://10.0.0.5:8050 \\
        --hosts hosts.txt --image ghcr.io/you/dash-swarm-agent \\
        --users 25 50 100 --out swarm-results.json

Agent reports come back over the SSH session's stdout, so no copying is
needed. Hosts need NTP-synced clocks (the default on cloud VMs) and Docker.
"""
import argparse
import concurrent.futures
import json
import math
import os
import shlex
import subprocess
import sys
import time

try:
    from .aggregate import aggregate, table
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from aggregate import aggregate, table  # type: ignore[no-redef]

HERE = os.path.dirname(os.path.abspath(__file__))
CONTAINER = "dash-swarm-agent"


def _agent_args(args, users, start_at, agent_id):
    return [
        "--target",
        args.target,
        "--users",
        str(users),
        "--scenario",
        ",".join(args.scenario),
        "--think",
        str(args.think),
        "--start-at",
        str(start_at),
        "--ramp",
        str(args.ramp),
        "--duration",
        str(args.duration),
        "--agent-id",
        agent_id,
        "--out",
        "-",
    ]


def _commands(args, users, start_at):
    if args.local:
        return [
            (
                f"local-{i}",
                [
                    sys.executable,
                    os.path.join(HERE, "agent.py"),
                    *_agent_args(args, users, start_at, f"local-{i}"),
                ],
            )
            for i in range(args.local)
        ]
    commands = []
    for host in _hosts(args.hosts):
        docker = [
            "docker",
            "run",
            "--rm",
            "--init",
            "--name",
            CONTAINER,
            "--ipc=host",
            "--network=host",
            args.image,
            *_agent_args(args, users, start_at, host),
        ]
        commands.append((host, _ssh(host, docker)))
    return commands


def _hosts(path):
    with open(path, encoding="utf-8") as f:
        hosts = [h.strip() for h in f if h.strip() and not h.startswith("#")]
    if not hosts:
        raise SystemExit(f"no hosts in {path}")
    return hosts


def _ssh(host, command):
    return [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=15",
        "-o",
        "ServerAliveInterval=15",
        host,
        " ".join(shlex.quote(a) for a in command),
    ]


def _run(command, timeout):
    host, cmd = command
    try:
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        if cmd[0] == "ssh":
            # Killing ssh leaves the container (and its browsers) running,
            # adding load to the next step.
            subprocess.run(
                _ssh(host, ["docker", "rm", "-f", CONTAINER]),
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=60,
                check=False,
            )
        return host, None, "timed out"
    lines = [line for line in proc.stdout.splitlines() if line.startswith("{")]
    if proc.returncode != 0 or not lines:
        return host, None, (proc.stderr.strip().splitlines() or ["no output"])[-1]
    return host, json.loads(lines[-1]), None


def run_step(args, users):
    # Long enough for ssh + docker start on every host before anyone begins.
    start_at = time.time() + args.lead
    commands = _commands(args, users, start_at)
    timeout = args.lead + args.ramp + args.duration + 120
    reports, failed = [], []
    with concurrent.futures.ThreadPoolExecutor(len(commands)) as pool:
        for host, report, error in pool.map(lambda c: _run(c, timeout), commands):
            if report is None:
                print(f"  {host}: {error}", flush=True)
                failed.append(host)
            else:
                reports.append(report)
    result = aggregate(reports)
    result["users_per_agent"] = users
    result["failed_agents"] = failed
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--target", required=True)
    where = parser.add_mutually_exclusive_group(required=True)
    where.add_argument("--local", type=int, help="agent processes on this machine")
    where.add_argument("--hosts", help="file with one ssh host per line")
    parser.add_argument("--image", default="dash-swarm-agent")
    parser.add_argument(
        "--users", nargs="+", type=int, default=[10], help="users per agent, per step"
    )
    parser.add_argument(
        "--scenario",
        default="http,ws,stream",
        type=lambda s: [x for x in s.split(",") if x],
    )
    parser.add_argument("--think", type=float, default=1.0)
    parser.add_argument("--ramp", type=float, default=30.0)
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--lead", type=float, default=20.0)
    parser.add_argument("--max-p95", type=float, default=1000.0)
    parser.add_argument("--out")
    args = parser.parse_args(argv)

    steps = []
    for users in args.users:
        print(f"--- {users} users per agent", flush=True)
        result = run_step(args, users)
        steps.append(result)
        print(table(result), flush=True)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "kind": "browser_swarm",
                        "target": args.target,
                        "params": {
                            k: getattr(args, k)
                            for k in ("scenario", "think", "ramp", "duration")
                        },
                        "steps": steps,
                    },
                    f,
                    indent=1,
                )
        # A whole stream takes frames x interval by design; judge its first
        # frame and the plain callbacks.
        p95 = max(
            (
                m["p95"] or 0
                for name, m in result["metrics"].items()
                if name in ("http", "ws", "stream_first")
            ),
            default=math.inf,
        )
        if (
            result["error_rate"] is None
            or result["error_rate"] > 0.01
            or p95 > args.max_p95
        ):
            print("saturated: stopping", flush=True)
            break
        # Past these the swarm is not delivering the load it reports, so a
        # bigger step would only measure the load generators.
        invalid = [
            label
            for label, bad in (
                ("failed agents", result["failed_agents"]),
                ("failed users", result["users_failed"] > 0.01 * result["users"]),
                ("agent-bound", result["agent_bound"]),
                ("late agents", result["late_agents"]),
            )
            if bad
        ]
        if invalid:
            print(f"load not delivered ({', '.join(invalid)}): stopping", flush=True)
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
