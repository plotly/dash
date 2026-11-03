"""DASH_SHARED_STORAGE picks the backend when the app does not pass one."""
# pylint: disable=protected-access
import sys

import pytest

from dash import Dash
from dash._shared_storage import (
    ClusterSharedStorage,
    DiskcacheSharedStorage,
    LocalSharedStorage,
    RedisSharedStorage,
)
from dash.exceptions import InvalidConfig


def _app(monkeypatch, value, **kwargs):
    monkeypatch.setenv("DASH_SHARED_STORAGE", value)
    return Dash(__name__, **kwargs)


def _built(app):
    # Build the backend without start(), so nothing connects.
    storage = app._shared_storage_arg
    return storage if storage is None else storage()


def test_unset_disables(monkeypatch):
    monkeypatch.delenv("DASH_SHARED_STORAGE", raising=False)
    app = Dash(__name__)
    assert not app.shared_storage_enabled


@pytest.mark.parametrize("value", ["local", "LOCAL", " local "])
def test_local(monkeypatch, value):
    app = _app(monkeypatch, value)
    assert app._shared_storage_arg is LocalSharedStorage


@pytest.mark.parametrize("value", ["none", "None", ""])
def test_none_disables(monkeypatch, value):
    app = _app(monkeypatch, value)
    assert not app.shared_storage_enabled


def test_diskcache_is_lazy(monkeypatch, tmp_path):
    pytest.importorskip("diskcache")
    directory = tmp_path / "ss"
    app = _app(monkeypatch, f"diskcache://{directory}")
    assert app.shared_storage_enabled
    assert not directory.exists()
    storage = app.shared_storage
    assert isinstance(storage, DiskcacheSharedStorage)
    assert directory.is_dir()
    storage.close()


@pytest.mark.parametrize("value", ["diskcache://relative/path", "diskcache:"])
def test_diskcache_needs_absolute_path(monkeypatch, value):
    pytest.importorskip("diskcache")
    with pytest.raises(InvalidConfig, match="DASH_SHARED_STORAGE"):
        _app(monkeypatch, value)


@pytest.mark.parametrize(
    "url", ["redis://localhost:6399/3", "rediss://user:pw@example.com:6380/0"]
)
def test_redis(monkeypatch, url):
    pytest.importorskip("redis")
    # A port nothing listens on: construction must not connect.
    storage = _built(_app(monkeypatch, url))
    assert isinstance(storage, RedisSharedStorage)
    kwargs = storage._redis.connection_pool.connection_kwargs
    assert kwargs["port"] == int(url.rsplit(":", 1)[1].split("/")[0])
    storage.close()


def _cluster(storage):
    coord = storage._coord
    return coord, coord._port, coord._data_port


def test_cluster_from_url(monkeypatch):
    monkeypatch.delenv("DASH_SECRET_KEY", raising=False)
    storage = _built(_app(monkeypatch, "cluster://:s%40cret@app-peers:7200"))
    assert isinstance(storage, ClusterSharedStorage)
    coord, port, data_port = _cluster(storage)
    assert (port, data_port) == (7200, 7201)
    assert coord._role is None  # nothing bound or probed yet
    storage.close()


def test_cluster_tls_files_from_url(monkeypatch, make_cert):
    cert, key = make_cert()
    url = f"cluster://:pw@app-peers?tls_cert={cert}&tls_key={key}&tls_ca={cert}"
    storage = _built(_app(monkeypatch, url))
    coord, _port, _data_port = _cluster(storage)
    assert coord.client_ssl is not None and coord._tls is not None
    storage.close()


def test_cluster_tls_path_keeps_plus(monkeypatch, make_cert, tmp_path):
    import shutil

    cert, key = make_cert()
    odd = tmp_path / "a+b"
    odd.mkdir()
    shutil.copy(cert, odd / "cert.pem")
    shutil.copy(key, odd / "key.pem")
    url = f"cluster://:pw@app-peers?tls_cert={odd}/cert.pem&tls_key={odd}/key.pem"
    storage = _built(_app(monkeypatch, url))
    assert storage._coord._tls is not None
    storage.close()


def test_cluster_secret_from_env_and_default_port(monkeypatch):
    monkeypatch.setenv("DASH_SECRET_KEY", "from-env")
    storage = _built(_app(monkeypatch, "cluster://app-peers"))
    _coord, port, _data_port = _cluster(storage)
    assert port == 7100
    storage.close()


@pytest.mark.parametrize(
    "value, reason",
    [
        ("cluster://app-peers", "needs a secret"),
        ("cluster://:pw@", "needs a host"),
        ("cluster://:pw@app-peers:notaport", "valid port"),
        ("cluster://:pw@app-peers:65535", "below 65535"),
        ("cluster://:pw@app-peers/path", "only a host"),
        ("cluster://:pw@app-peers?mode=persist", "only tls_cert"),
        ("cluster://:pw@app-peers?tls_cert=/a", "both tls_cert and tls_key"),
        ("cluster://:pw@app-peers?tls_cert=/a&tls_key=/b&tls_cert=/c", "once each"),
        ("cluster://:pw@app-peers:0", "valid port"),
        ("cluster://pw@app-peers", "after a colon"),
    ],
)
def test_cluster_rejects(monkeypatch, value, reason):
    monkeypatch.delenv("DASH_SECRET_KEY", raising=False)
    with pytest.raises(InvalidConfig, match=reason):
        _app(monkeypatch, value)


@pytest.mark.parametrize("value", ["memcached://x", "redis", "/tmp/cache", "true"])
def test_garbage_names_the_variable(monkeypatch, value):
    with pytest.raises(InvalidConfig, match="DASH_SHARED_STORAGE"):
        _app(monkeypatch, value)


@pytest.mark.parametrize(
    "value",
    [
        "valkey://:hunter2@host:6379",
        "valkey://default:Zx9/Qm+4kP@cache.internal:6379/0",
        "cluster://admin:hunter2@nodes:99999",
        "diskcache://user:hunter2@host/path",
        "redis://:hunter2@[::1/0",
    ],
)
def test_error_hides_the_value(monkeypatch, value):
    with pytest.raises(InvalidConfig) as err:
        _app(monkeypatch, value)
    for secret in ("hunter2", "Zx9", "Qm+4kP"):
        assert secret not in str(err.value)


def test_redis_key_prefix_from_url(monkeypatch):
    pytest.importorskip("redis")
    storage = _built(
        _app(monkeypatch, "redis://localhost:6399/3?key_prefix=myapp&socket_timeout=5")
    )
    assert storage._prefix == "myapp"
    kwargs = storage._redis.connection_pool.connection_kwargs
    assert kwargs["db"] == 3
    assert kwargs["socket_timeout"] == 5
    assert "key_prefix" not in kwargs
    storage.close()


def test_redis_default_key_prefix(monkeypatch):
    pytest.importorskip("redis")
    storage = _built(_app(monkeypatch, "redis://localhost:6399/3"))
    assert storage._prefix == "dash:ss"
    storage.close()


def test_redis_empty_key_prefix(monkeypatch):
    pytest.importorskip("redis")
    with pytest.raises(InvalidConfig, match="key_prefix"):
        _app(monkeypatch, "redis://localhost:6399/3?key_prefix=")


def test_redis_password_is_percent_decoded(monkeypatch):
    pytest.importorskip("redis")
    storage = _built(_app(monkeypatch, "redis://:p%40ss%2Fw@localhost:6399/0"))
    assert storage._redis.connection_pool.connection_kwargs["password"] == "p@ss/w"
    storage.close()


def test_diskcache_path_is_percent_decoded(monkeypatch, tmp_path):
    pytest.importorskip("diskcache")
    directory = tmp_path / "my cache"
    url = "diskcache://" + str(directory).replace(" ", "%20")
    storage = _built(_app(monkeypatch, url))
    assert directory.is_dir()
    storage.close()


def test_explicit_argument_beats_env(monkeypatch):
    storage = LocalSharedStorage()
    app = _app(monkeypatch, "none", shared_storage=storage)
    assert app._shared_storage_arg is storage


def test_explicit_none_beats_env(monkeypatch):
    assert not _app(monkeypatch, "local", shared_storage=None).shared_storage_enabled


def test_explicit_argument_skips_env_validation(monkeypatch):
    _app(monkeypatch, "garbage", shared_storage=LocalSharedStorage)


@pytest.mark.parametrize(
    "value, module, backend",
    [
        ("redis://localhost:6379", "redis", RedisSharedStorage),
        ("diskcache:///tmp/dash-ss", "diskcache", DiskcacheSharedStorage),
    ],
)
def test_missing_extra_matches_explicit_error(monkeypatch, value, module, backend):
    monkeypatch.setitem(sys.modules, module, None)
    with pytest.raises(ImportError) as explicit:
        backend()
    with pytest.raises(ImportError) as from_env:
        _app(monkeypatch, value)
    assert str(from_env.value) == str(explicit.value)
