import hashlib
import io
import logging
import os
import tarfile

import pytest

from dash import _tunnel


@pytest.mark.parametrize(
    "protocol,host,expected",
    [
        ("http", "127.0.0.1", "http://127.0.0.1:8050"),
        ("http", "0.0.0.0", "http://127.0.0.1:8050"),
        ("http", "::", "http://[::1]:8050"),
        ("http", "::1", "http://[::1]:8050"),
        ("https", "localhost", "https://localhost:8050"),
    ],
)
def test_local_url(protocol, host, expected):
    assert _tunnel.local_url(protocol, host, 8050) == expected


@pytest.mark.parametrize(
    "system,machine,expected",
    [
        ("darwin", "arm64", "cloudflared-darwin-arm64.tgz"),
        ("darwin", "x86_64", "cloudflared-darwin-amd64.tgz"),
        ("linux", "x86_64", "cloudflared-linux-amd64"),
        ("linux", "aarch64", "cloudflared-linux-arm64"),
        ("linux", "i686", None),
        ("win32", "AMD64", "cloudflared-windows-amd64.exe"),
    ],
)
def test_release_asset(monkeypatch, system, machine, expected):
    monkeypatch.setattr(_tunnel.sys, "platform", system)
    monkeypatch.setattr(_tunnel.platform, "machine", lambda: machine)
    if expected:
        assert _tunnel._release_asset() == expected
    else:
        with pytest.raises(RuntimeError, match="Install cloudflared"):
            _tunnel._release_asset()


def test_url_regex():
    line = "2026-09-30T12:00:00Z INF |  https://a-b-c-1.trycloudflare.com  |"
    assert _tunnel.TUNNEL_URL_RE.search(line).group(0) == (
        "https://a-b-c-1.trycloudflare.com"
    )


def test_url_regex_skips_api_host():
    line = 'ERR failed to request quick Tunnel: Post "https://api.trycloudflare.com/tunnel"'
    assert _tunnel.TUNNEL_URL_RE.search(line) is None


class FakeStdin:
    def __init__(self, tty):
        self.tty = tty

    def isatty(self):
        return self.tty


@pytest.fixture
def fake_release(monkeypatch, tmp_path):
    """Serve ``payload`` as the release asset and count the requests."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr(_tunnel.sys, "platform", "linux")
    monkeypatch.setattr(_tunnel.platform, "machine", lambda: "x86_64")
    release = {"payload": b"fake cloudflared binary", "requests": 0}

    def urlopen(url, timeout):
        release["requests"] += 1
        return io.BytesIO(release["payload"])

    monkeypatch.setattr(_tunnel.urllib.request, "urlopen", urlopen)
    monkeypatch.setitem(
        _tunnel.CLOUDFLARED_SHA256,
        "cloudflared-linux-amd64",
        hashlib.sha256(release["payload"]).hexdigest(),
    )
    return release


def answer(monkeypatch, reply, tty=True):
    def fake_input(_):
        if reply is EOFError:
            raise EOFError
        return reply

    monkeypatch.setattr(_tunnel.sys, "stdin", FakeStdin(tty))
    monkeypatch.setattr("builtins.input", fake_input)


def test_download_after_yes_then_cached(monkeypatch, fake_release):
    answer(monkeypatch, "y")
    path = _tunnel._download_cloudflared(logging.getLogger())
    with open(path, "rb") as f:
        assert f.read() == fake_release["payload"]
    assert os.access(path, os.X_OK)
    assert _tunnel.CLOUDFLARED_VERSION in path

    answer(monkeypatch, "n")
    assert _tunnel._download_cloudflared(logging.getLogger()) == path
    assert fake_release["requests"] == 1


@pytest.mark.parametrize(
    "reply,tty", [("n", True), ("", True), (EOFError, True), ("y", False)]
)
def test_no_download_without_consent(monkeypatch, fake_release, reply, tty):
    answer(monkeypatch, reply, tty)
    logger = logging.getLogger()
    with pytest.raises(RuntimeError, match="Install cloudflared"):
        _tunnel._download_cloudflared(logger)
    assert fake_release["requests"] == 0


def test_checksum_mismatch(monkeypatch, fake_release, tmp_path):
    answer(monkeypatch, "y")
    fake_release["payload"] = b"tampered"
    logger = logging.getLogger()
    with pytest.raises(RuntimeError, match="checksum"):
        _tunnel._download_cloudflared(logger)
    assert not list(tmp_path.glob(".cache/dash/cloudflared/*/cloudflared"))


def test_download_extracts_macos_archive(monkeypatch, fake_release):
    binary = b"fake mac binary"
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as tgz:
        info = tarfile.TarInfo("cloudflared")
        info.size = len(binary)
        tgz.addfile(info, io.BytesIO(binary))
    fake_release["payload"] = archive.getvalue()
    monkeypatch.setattr(_tunnel.sys, "platform", "darwin")
    monkeypatch.setattr(_tunnel.platform, "machine", lambda: "arm64")
    monkeypatch.setitem(
        _tunnel.CLOUDFLARED_SHA256,
        "cloudflared-darwin-arm64.tgz",
        hashlib.sha256(binary).hexdigest(),
    )
    answer(monkeypatch, "yes")
    with open(_tunnel._download_cloudflared(logging.getLogger()), "rb") as f:
        assert f.read() == binary
