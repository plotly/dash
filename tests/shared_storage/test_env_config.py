"""DASH_SHARED_STORAGE picks the backend when the app does not pass one."""
# pylint: disable=protected-access
import sys

import pytest

from dash import Dash
from dash._shared_storage import (
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


def test_unset_defaults_to_local(monkeypatch):
    monkeypatch.delenv("DASH_SHARED_STORAGE", raising=False)
    app = Dash(__name__)
    assert app._shared_storage_arg is LocalSharedStorage


@pytest.mark.parametrize("value", ["local", "LOCAL", " local ", ""])
def test_local(monkeypatch, value):
    app = _app(monkeypatch, value)
    assert app._shared_storage_arg is LocalSharedStorage


@pytest.mark.parametrize("value", ["none", "None"])
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


def test_cluster_is_reserved(monkeypatch):
    with pytest.raises(InvalidConfig, match="not supported in this version"):
        _app(monkeypatch, "cluster://nodes")


@pytest.mark.parametrize("value", ["memcached://x", "redis", "/tmp/cache", "true"])
def test_garbage_names_the_variable_and_value(monkeypatch, value):
    with pytest.raises(InvalidConfig) as err:
        _app(monkeypatch, value)
    assert "DASH_SHARED_STORAGE" in str(err.value)
    assert repr(value) in str(err.value)


@pytest.mark.parametrize(
    "value", ["valkey://:hunter2@host:6379", "cluster://admin:hunter2@nodes"]
)
def test_error_hides_url_credentials(monkeypatch, value):
    with pytest.raises(InvalidConfig) as err:
        _app(monkeypatch, value)
    assert "hunter2" not in str(err.value)
    assert "***@" in str(err.value)


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
