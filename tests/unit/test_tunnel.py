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
