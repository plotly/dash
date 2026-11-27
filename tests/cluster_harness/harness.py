"""Run ClusterSharedStorage replicas as real containers, with docker or podman.

Every replica is a container on one user network, reachable by the others
under the alias ``dash`` (one DNS name, one A record per replica), running
``gunicorn -w 2`` on the repo source mounted read only. The harness talks to
replicas with ``exec`` on loopback, so it works with rootless podman where
container IPs are not reachable from the host.

    python harness.py up 3 [--quorum] [--tls] [--publish]
    python harness.py scale 5
    python harness.py status
    python harness.py kill|pause|unpause|cut|heal|logs|rm <index>
    python harness.py down

Environment: CLUSTER_ENGINE=docker|podman (default: whichever is installed),
HARNESS_IMAGE to use an existing image instead of building one.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
NET = "dash-cluster-harness"
ALIAS = "dash"
LABEL = "dash-cluster-harness"
IMAGE = "dash-cluster-harness:latest"
LOCK_PORT = 7100
SECRET = "harness-secret"
STATE = HERE / ".state.json"

DOCKERFILE = """\
FROM docker.io/library/python:3.12-slim
COPY install.txt shared_storage.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/install.txt -r /tmp/shared_storage.txt gunicorn
"""


class EngineError(RuntimeError):
    pass


def engine_name():
    name = os.environ.get("CLUSTER_ENGINE")
    if name:
        return name
    for name in ("docker", "podman"):
        if shutil.which(name):
            return name
    raise EngineError("neither docker nor podman is on PATH")


class Cluster:
    def __init__(self, quorum=None, tls=False, workers=2, publish=False):
        self.engine = engine_name()
        self.quorum = quorum
        self.tls = tls
        self.workers = workers
        self.publish = publish
        self.image = os.environ.get("HARNESS_IMAGE", IMAGE)

    @classmethod
    def load(cls):
        """The cluster the last ``up`` started, so scaling keeps its options."""
        try:
            return cls(**json.loads(STATE.read_text()))
        except FileNotFoundError:
            return cls()

    def save(self):
        STATE.write_text(
            json.dumps(
                {
                    "quorum": self.quorum,
                    "tls": self.tls,
                    "workers": self.workers,
                    "publish": self.publish,
                }
            )
        )

    # engine plumbing

    def run(self, *args, check=True, timeout=120):
        res = subprocess.run(
            [self.engine, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if check and res.returncode != 0:
            raise EngineError(
                f"{self.engine} {' '.join(args)} failed:\n{res.stderr.strip()}"
            )
        return res.stdout.strip()

    def preflight(self):
        built = ("dash/dcc/_imports_.py", "dash/dash-renderer/build")
        if not all((REPO / path).exists() for path in built):
            raise EngineError(
                f"{REPO} has no built components ({', '.join(built)}). "
                "Run `npm run build` or copy the built files in first."
            )
        self.run("info", timeout=30)

    def build(self):
        if "HARNESS_IMAGE" in os.environ:
            return
        if self.run("images", "-q", self.image, check=False):
            return
        ctx = HERE / ".build"
        ctx.mkdir(exist_ok=True)
        (ctx / "Dockerfile").write_text(DOCKERFILE)
        for req in ("install.txt", "shared_storage.txt"):
            shutil.copy(REPO / "requirements" / req, ctx / req)
        print(f"building {self.image} with {self.engine}...", file=sys.stderr)
        self.run("build", "-t", self.image, str(ctx), timeout=900)

    def make_tls(self):
        out = HERE / ".tls"
        if (out / "cert.pem").exists():
            return
        out.mkdir(exist_ok=True)
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "ec",
                "-pkeyopt",
                "ec_paramgen_curve:prime256v1",
                "-nodes",
                "-days",
                "365",
                "-subj",
                "/CN=dash-cluster",
                "-keyout",
                str(out / "key.pem"),
                "-out",
                str(out / "cert.pem"),
            ],
            check=True,
            capture_output=True,
        )
        # Containers may run as another uid (rootless podman, other images).
        os.chmod(out / "key.pem", 0o644)

    def url(self):
        opts = []
        if self.tls:
            opts += ["tls_cert=/harness/.tls/cert.pem", "tls_key=/harness/.tls/key.pem"]
        if self.quorum:
            opts.append(f"replicas={self.quorum}")
        query = "?" + "&".join(opts) if opts else ""
        return f"cluster://:{SECRET}@{ALIAS}:{LOCK_PORT}{query}"

    # replicas

    def names(self, stopped=False):
        """Running (or paused) replicas, and with ``stopped`` killed ones too."""
        out = self.run(
            "ps",
            *(["-a"] if stopped else []),
            "--filter",
            f"label={LABEL}",
            "--format",
            "{{.Names}}",
        )
        return sorted(out.split(), key=lambda n: int(n.rsplit("-", 1)[1]))

    @staticmethod
    def name(index):
        return f"dch-{index}"

    def indexes(self):
        return [int(n.rsplit("-", 1)[1]) for n in self.names()]

    def start(self, index):
        self.remove(index)  # a killed replica keeps its name until removed
        args = [
            "run",
            "-d",
            "--name",
            self.name(index),
            "--label",
            LABEL,
            # SELinux hosts would refuse the bind mounts.
            "--security-opt",
            "label=disable",
            "--network",
            NET,
            "--network-alias",
            ALIAS,
            "-e",
            f"POD={index}",
            "-e",
            f"DASH_SHARED_STORAGE={self.url()}",
            "-e",
            "DASH_SECRET_KEY=harness",
            "-e",
            "PYTHONPATH=/src",
            "-e",
            "PYTHONUNBUFFERED=1",
            "-v",
            f"{REPO}:/src:ro",
            "-v",
            f"{HERE}:/harness:ro",
            "-w",
            "/harness",
        ]
        if self.publish:
            args += ["-p", f"{8050 + index}:8050"]
        args += [
            "--entrypoint",
            "python3",
            self.image,
            "-m",
            "gunicorn",
            "-w",
            str(self.workers),
            "-b",
            "0.0.0.0:8050",
            "--timeout",
            "120",
            "app:server",
        ]
        self.run(*args)

    def up(self, count):
        """Start ``count`` replicas at once, as when waking from zero."""
        self.preflight()
        self.build()
        if self.tls:
            self.make_tls()
        self.run("network", "create", NET, check=False)
        self.down(network=False)
        self.save()
        for index in range(1, count + 1):
            self.start(index)
        self.wait_up(range(1, count + 1))

    def scale(self, count):
        alive = self.indexes()
        if count > len(alive):
            start = max(alive, default=0) + 1
            new = range(start, start + count - len(alive))
            for index in new:
                self.start(index)
            self.wait_up(new)
        else:
            # Like a scale down: drop the newest replicas first.
            for index in sorted(alive, reverse=True)[: len(alive) - count]:
                self.remove(index)

    def remove(self, index):
        self.run("rm", "-f", self.name(index), check=False)

    def kill(self, index):
        self.run("kill", self.name(index))

    def pause(self, index):
        self.run("pause", self.name(index))

    def unpause(self, index):
        self.run("unpause", self.name(index))

    def cut(self, index):
        """Take a replica off the network. ``exec`` still reaches it."""
        self.run("network", "disconnect", NET, self.name(index))

    def heal(self, index):
        self.run("network", "connect", "--alias", ALIAS, NET, self.name(index))

    def logs(self, index):
        return self.run("logs", "--tail", "200", self.name(index), check=False)

    def down(self, network=True):
        for name in self.names(stopped=True):
            self.run("rm", "-f", name, check=False)
        if network:
            self.run("network", "rm", NET, check=False)
            STATE.unlink(missing_ok=True)

    # talking to the app inside a replica

    def probe(self, index, *args, timeout=60):
        out = self.run(
            "exec",
            self.name(index),
            "python3",
            "/harness/probe.py",
            *args,
            timeout=timeout,
        )
        return json.loads(out)

    def get(self, index, path):
        return self.probe(index, "get", path)

    def post(self, index, path, body, timeout=20):
        return self.probe(
            index, "post", path, json.dumps(body), str(timeout), timeout=timeout + 30
        )

    def every_worker(self, index, path, seconds=40):
        """One answer per gunicorn worker of a replica, keyed by pid."""
        out = self.probe(
            index,
            "workers",
            path,
            str(self.workers),
            str(seconds),
            timeout=seconds + 30,
        )
        if "error" in out or len(out) < self.workers:
            raise EngineError(f"replica {index} {path}: {out}")
        return out

    def wait_up(self, indexes, timeout=90):
        deadline = time.monotonic() + timeout
        for index in indexes:
            while True:
                try:
                    self.every_worker(index, "/whoami")
                    break
                except (EngineError, subprocess.TimeoutExpired, ValueError):
                    if time.monotonic() > deadline:
                        print(self.logs(index), file=sys.stderr)
                        raise
                    time.sleep(0.5)

    def roles(self, indexes=None):
        """{(replica, pid): whoami} for every worker of the given replicas."""
        out = {}
        for index in indexes or self.indexes():
            for pid, res in self.every_worker(index, "/whoami").items():
                out[(index, int(pid))] = res
        return out

    def settled(self, indexes=None, timeout=60):
        """Wait until the replicas agree on one owner, and return it."""
        deadline = time.monotonic() + timeout
        while True:
            try:
                roles = self.roles(indexes)
                tokens = {r["token"] for r in roles.values()}
                owners = [k for k, r in roles.items() if r["role"] == "owner"]
                if len(tokens) == 1 and None not in tokens and len(owners) == 1:
                    return owners[0][0], tokens.pop(), roles
            except (EngineError, subprocess.TimeoutExpired, ValueError) as err:
                roles = f"unreachable: {err}"
            if time.monotonic() > deadline:
                raise AssertionError(f"no single owner after {timeout}s: {roles}")
            time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(
        description="ClusterSharedStorage container harness"
    )
    parser.add_argument("command")
    parser.add_argument("arg", nargs="?", type=int)
    parser.add_argument("--quorum", type=int, help="replicas=N (majority mode)")
    parser.add_argument("--tls", action="store_true")
    parser.add_argument("--publish", action="store_true", help="replica i on 8050+i")
    opts = parser.parse_args()
    cmd = opts.command
    if cmd == "up":
        cluster = Cluster(quorum=opts.quorum, tls=opts.tls, publish=opts.publish)
    else:
        cluster = Cluster.load()
    needs_arg = ("scale", "logs", "kill", "pause", "unpause", "cut", "heal", "rm")
    if cmd in needs_arg and opts.arg is None:
        parser.error(f"{cmd} takes a number")
    if cmd == "up":
        cluster.up(opts.arg or 3)
        cmd = "status"
    elif cmd == "scale":
        cluster.scale(opts.arg)
        cmd = "status"
    elif cmd == "down":
        cluster.down()
    elif cmd == "logs":
        print(cluster.logs(opts.arg))
    elif cmd in ("kill", "pause", "unpause", "cut", "heal"):
        getattr(cluster, cmd)(opts.arg)
    elif cmd == "rm":
        cluster.remove(opts.arg)
    elif cmd != "status":
        parser.error(f"unknown command {cmd}")
    if cmd == "status":
        print(f"{cluster.engine}, {cluster.url()}")
        for index in cluster.indexes():
            try:
                for pid, res in cluster.every_worker(index, "/whoami", 5).items():
                    print(
                        f"replica {index} pid {pid}: {res['role']} token {res['token']}"
                    )
            except (EngineError, subprocess.TimeoutExpired, ValueError) as err:
                print(f"replica {index}: {str(err).splitlines()[0]}")


if __name__ == "__main__":
    main()
