"""Expose a locally running Dash app through a Cloudflare quick tunnel.

Quick tunnels need no Cloudflare account. ``cloudflared`` is used from the
PATH when present, otherwise the official release is downloaded once and
cached.
"""

import atexit
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import threading
import urllib.request

RELEASE_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/"
# api.trycloudflare.com shows up in cloudflared's own error messages.
TUNNEL_URL_RE = re.compile(r"https://(?!api\.)[-a-z0-9]+\.trycloudflare\.com")


def _release_asset():
    machine = platform.machine().lower()
    arch = {"x86_64": "amd64", "amd64": "amd64", "arm64": "arm64", "aarch64": "arm64"}
    if machine in arch:
        name = {"darwin": "darwin", "linux": "linux", "win32": "windows"}.get(
            sys.platform
        )
        suffix = {"darwin": ".tgz", "windows": ".exe"}.get(name, "")
        if name:
            return f"cloudflared-{name}-{arch[machine]}{suffix}"
    raise RuntimeError(
        f"No cloudflared build for {sys.platform}/{machine}. Install cloudflared "
        "yourself and make sure it is on your PATH: "
        "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
    )


def _download_cloudflared(logger):
    asset = _release_asset()
    exe_name = "cloudflared.exe" if sys.platform == "win32" else "cloudflared"
    target_dir = os.path.expanduser(os.path.join("~", ".cache", "dash", "cloudflared"))
    target = os.path.join(target_dir, exe_name)
    if os.path.isfile(target):
        return target

    os.makedirs(target_dir, exist_ok=True)
    logger.info("Downloading cloudflared from %s%s", RELEASE_URL, asset)
    with tempfile.TemporaryDirectory(dir=target_dir) as tmp:
        download = os.path.join(tmp, asset)
        with urllib.request.urlopen(RELEASE_URL + asset, timeout=60) as resp, open(
            download, "wb"
        ) as out:
            shutil.copyfileobj(resp, out)
        if asset.endswith(".tgz"):
            with tarfile.open(download) as tgz:
                tgz.extract("cloudflared", tmp, filter="data")
            download = os.path.join(tmp, exe_name)
        os.chmod(download, 0o700)
        # Rename last so a failed download never leaves a broken binary behind.
        os.replace(download, target)
    return target


def find_cloudflared(logger):
    return shutil.which("cloudflared") or _download_cloudflared(logger)


def local_url(protocol, host, port):
    if host in ("0.0.0.0", ""):
        host = "127.0.0.1"
    elif host == "::":
        host = "::1"
    if ":" in host:
        host = f"[{host}]"
    return f"{protocol}://{host}:{port}"


class Tunnel:
    def __init__(self, process):
        self.process = process
        self.public_url = None

    def stop(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()


def _stop_on_sigterm(tunnel):
    # atexit does not run on SIGTERM, which would leave cloudflared
    # exposing the port after Dash is gone.
    if threading.current_thread() is not threading.main_thread():
        return
    original = signal.getsignal(signal.SIGTERM)

    def handler(sig, frame):
        tunnel.stop()
        if callable(original):
            original(sig, frame)
        elif original == signal.SIG_DFL:
            signal.signal(sig, signal.SIG_DFL)
            signal.raise_signal(sig)

    signal.signal(signal.SIGTERM, handler)


def start_tunnel(target_url, logger, path="/"):
    cmd = [
        find_cloudflared(logger),
        "tunnel",
        "--no-autoupdate",
        "--url",
        target_url,
    ]
    if target_url.startswith("https"):
        # The local server usually has a self signed or adhoc certificate.
        cmd.append("--no-tls-verify")

    process = subprocess.Popen(  # pylint: disable=consider-using-with
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
    )
    tunnel = Tunnel(process)
    atexit.register(tunnel.stop)
    _stop_on_sigterm(tunnel)

    def watch():
        output = []
        # cloudflared keeps logging for its whole life, so the pipe must be
        # drained even after the URL is found or it will block.
        for line in process.stderr:  # type: ignore
            if tunnel.public_url:
                continue
            output.append(line)
            match = TUNNEL_URL_RE.search(line)
            if match:
                tunnel.public_url = match.group(0)
                logger.info(
                    "Dash is publicly available at %s%s\n", tunnel.public_url, path
                )
        if not tunnel.public_url:
            logger.error(
                "The cloudflared tunnel exited before it was ready:\n%s",
                "".join(output[-20:]),
            )

    threading.Thread(target=watch, daemon=True).start()
    return tunnel
