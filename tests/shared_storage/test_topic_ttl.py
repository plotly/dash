"""Topic ttl contract, run against every backend so they expire topics the
same way: a topic goes as a whole once nobody publishes to or reads it, never
message by message while it is in use."""
import os
import time
import uuid

import pytest

from dash._shared_storage import (
    DiskcacheSharedStorage,
    LocalSharedStorage,
    RedisSharedStorage,
    SharedStorageError,
    _engine,
    base,
)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
TTL = 0.5


def _redis_available():
    try:
        import redis  # pylint: disable=import-outside-toplevel

        client = redis.Redis.from_url(REDIS_URL)
        client.ping()
        client.close()
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def _make(kind, tmp_path):
    tag = uuid.uuid4().hex[:12]
    if kind == "local":
        return LocalSharedStorage(namespace=f"ttl-{tag}")
    if kind == "diskcache":
        return DiskcacheSharedStorage(directory=str(tmp_path / "cache"))
    if not _redis_available():
        pytest.skip("no Redis reachable at REDIS_URL")
    return RedisSharedStorage(url=REDIS_URL, key_prefix=f"dash:sstest:{tag}")


BACKENDS = ["local", "diskcache", "redis"]


@pytest.fixture(params=BACKENDS)
def store(request, tmp_path, monkeypatch):
    monkeypatch.setattr(base, "MIN_TOPIC_TTL", 0.1)
    monkeypatch.setattr(_engine, "_SWEEP_INTERVAL", 0.05)
    s = _make(request.param, tmp_path)
    s.start()
    try:
        yield s
    finally:
        s.close()


def _idle(store):
    time.sleep(TTL * 1.25 + 0.2)
    # Local sweeps on the next pub/sub call.
    store.publish("other", "x")


def test_idle_topic_is_released(store):
    for i in range(3):
        store.publish("t", f"m{i}", ttl=TTL)
    _idle(store)
    assert store.subscribe("t", replay_from=0).poll(0.0) == []
    store.publish("t", "again", ttl=TTL)
    assert store.subscribe("t", replay_from=0).poll(0.0) == [(1, "again")]


def test_a_read_topic_keeps_every_buffered_message(store):
    store.publish("t", "m1", ttl=TTL)
    reader = store.subscribe("t", replay_from=1)
    deadline = time.monotonic() + TTL * 3
    while time.monotonic() < deadline:
        assert reader.poll(0.0) == []
        time.sleep(TTL / 5)
    # Older than the ttl, but the topic was in use all along.
    assert store.subscribe("t", replay_from=0).poll(0.0) == [(1, "m1")]


def test_without_ttl_a_topic_is_kept(store):
    store.publish("t", "m1")
    _idle(store)
    assert store.subscribe("t", replay_from=0).poll(0.0) == [(1, "m1")]


def test_a_publish_without_ttl_keeps_the_topic(store):
    store.publish("t", "m1", ttl=TTL)
    store.publish("t", "m2")
    _idle(store)
    assert store.subscribe("t", replay_from=0).poll(0.0) == [(1, "m1"), (2, "m2")]


def test_a_shorter_ttl_applies_at_once(store):
    store.publish("t", "m1", ttl=60)
    store.publish("t", "m2", ttl=TTL)
    _idle(store)
    assert store.subscribe("t", replay_from=0).poll(0.0) == []


@pytest.mark.parametrize("kind", BACKENDS)
@pytest.mark.parametrize("ttl", [0, -1, 0.5, float("nan"), float("inf")])
def test_a_ttl_under_the_floor_is_rejected(kind, ttl, tmp_path):
    s = _make(kind, tmp_path)
    try:
        with pytest.raises(SharedStorageError):
            s.publish("t", "m", ttl=ttl)
    finally:
        s.close()
