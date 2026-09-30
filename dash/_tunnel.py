"""Expose a locally running Dash app through a Cloudflare quick tunnel.

Quick tunnels need no Cloudflare account. ``cloudflared`` is used from the
PATH when present, otherwise a pinned release is downloaded once, after the
user agrees, and checked against its published checksum.
"""

import atexit
import hashlib
import io
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

CLOUDFLARED_VERSION = "2026.9.3"
RELEASE_URL = (
    "https://github.com/cloudflare/cloudflared/releases/download/"
    f"{CLOUDFLARED_VERSION}/"
)
# SHA-256 of the cloudflared binary (inside the .tgz on macOS), from the
# release notes.
CLOUDFLARED_SHA256 = {
    "cloudflared-darwin-amd64.tgz": "ab588b3b4db9cdb4476c30a3db2a72635b1d8327d44741fee6799a0f37b0ec07",
    "cloudflared-darwin-arm64.tgz": "5472c1a01c84bc31b3021056a73b4e5774ddddefc572124ea8fdf6c340639f32",
    "cloudflared-linux-amd64": "77e26d8d900e0b8469f416239d14b5f296525fdf79fee6f511ef55609e3fbac2",
    "cloudflared-linux-arm64": "aaeb2d7d0da3614634c7e03ab13487a1522c2e79165ed2929cfe23d5e95b326d",
    "cloudflared-windows-amd64.exe": "f096265ec2fcbe9bb6e2d64268db167ced3fcbb83d894bdb9e2fcdb26f2ea7e2",
}
INSTALL_HINT = (
    "Install cloudflared and make sure it is on your PATH: "
    "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
)
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
        f"No cloudflared build for {sys.platform}/{machine}. {INSTALL_HINT}"
    )


def _confirm_download():
    if not (sys.stdin and sys.stdin.isatty()):
        raise RuntimeError(f"cloudflared was not found. {INSTALL_HINT}")
    try:
        answer = input(
            f"cloudflared was not found. Download cloudflared {CLOUDFLARED_VERSION} "
            "from github.com/cloudflare/cloudflared (about 40 MB)? [y/N] "
        )
    except EOFError:
        answer = ""
    if answer.strip().lower() not in ("y", "yes"):
        raise RuntimeError(f"Download declined. {INSTALL_HINT}")


def _download_cloudflared(logger):
    asset = _release_asset()
    exe_name = "cloudflared.exe" if sys.platform == "win32" else "cloudflared"
    target_dir = os.path.expanduser(
        os.path.join("~", ".cache", "dash", "cloudflared", CLOUDFLARED_VERSION)
    )
    target = os.path.join(target_dir, exe_name)
    if os.path.isfile(target):
        return target

    _confirm_download()
    os.makedirs(target_dir, exist_ok=True)
    logger.info("Downloading cloudflared from %s%s", RELEASE_URL, asset)
    with tempfile.TemporaryDirectory(dir=target_dir) as tmp:
        binary = os.path.join(tmp, exe_name)
        with urllib.request.urlopen(RELEASE_URL + asset, timeout=60) as resp:
            data = resp.read()
        if asset.endswith(".tgz"):
            with tarfile.open(fileobj=io.BytesIO(data)) as tgz:
                member = tgz.extractfile("cloudflared")
                data = member.read() if member else b""
        if hashlib.sha256(data).hexdigest() != CLOUDFLARED_SHA256[asset]:
            raise RuntimeError(
                f"The downloaded {asset} does not match its published checksum."
            )
        with open(binary, "wb") as out:
            out.write(data)
        os.chmod(binary, 0o700)
        # Rename last so a failed download never leaves a broken binary behind.
        os.replace(binary, target)
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


def _stop_on_signals(tunnel):
    # atexit does not run on SIGTERM, or on SIGHUP when the terminal closes,
    # which would leave cloudflared exposing the port after Dash is gone.
    if threading.current_thread() is not threading.main_thread():
        return
    for signum in (signal.SIGTERM, getattr(signal, "SIGHUP", None)):
        if signum is None:
            continue
        original = signal.getsignal(signum)

        def handler(sig, frame, original=original):
            tunnel.stop()
            if callable(original):
                original(sig, frame)
            elif original == signal.SIG_DFL:
                signal.signal(sig, signal.SIG_DFL)
                signal.raise_signal(sig)

        signal.signal(signum, handler)


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
    _stop_on_signals(tunnel)

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
