"""Unit tests for on-disk persistence of the local shared-storage engine.

Covers the chunked store directly and the two persistence modes wired to a
StoreEngine. Every test writes to a ``tmp_path`` so the real user cache dir is
never touched.
"""
import threading
import time
import uuid

from dash._shared_storage._engine import StoreEngine
from dash._shared_storage._persistence import ChunkedStore, _Persistence
from dash._shared_storage.local import LocalSharedStorage


def _persistent_engine(directory, mode, flush_interval=60.0):
    """Build an engine wired to a fresh persistence layer that has recovered."""
    engine = StoreEngine()
    persistence = _Persistence(str(directory), mode, flush_interval, engine)
    persistence.recover()
    engine.attach_persistence(persistence)
    persistence.start()
    return engine, persistence


# --- ChunkedStore ----------------------------------------------------------
def test_chunked_store_round_trip_across_chunk_boundary(tmp_path):
    store = ChunkedStore(str(tmp_path), chunk_size=2)
    for i in range(5):
        store.put_batch({f"k{i}": (i, None)})

    # 5 keys / 2 per chunk -> 3 chunk files.
    chunk_files = sorted(p.name for p in tmp_path.glob("chunk_*.msgpack"))
    assert len(chunk_files) == 3

    reopened = ChunkedStore(str(tmp_path), chunk_size=2)
    loaded = reopened.load_all()
    assert {k: v[0] for k, v in loaded.items()} == {f"k{i}": i for i in range(5)}


def test_chunked_store_delete(tmp_path):
    store = ChunkedStore(str(tmp_path))
    store.put_batch({"a": (1, None), "b": (2, None)})
    store.delete("a")
    store.delete("missing")  # idempotent / no-op

    reopened = ChunkedStore(str(tmp_path))
    loaded = reopened.load_all()
    assert set(loaded) == {"b"}


def test_chunked_store_missing_dir_is_empty(tmp_path):
    store = ChunkedStore(str(tmp_path / "does-not-exist-yet"))
    assert store.load_all() == {}


def test_chunked_store_corrupt_files_are_empty(tmp_path):
    (tmp_path / "index.msgpack").write_bytes(b"\xff\xff not msgpack")
    (tmp_path / "chunk_0.msgpack").write_bytes(b"garbage")
    store = ChunkedStore(str(tmp_path))
    assert store.load_all() == {}  # graceful, no exception


# --- persist mode (write-through) ------------------------------------------
def test_persist_recovers_in_new_engine(tmp_path):
    engine, persistence = _persistent_engine(tmp_path, "persist")
    engine.set("a", {"n": 1})
    engine.set("b", [1, 2, 3])
    engine.delete("b")
    persistence.close()

    engine2, _ = _persistent_engine(tmp_path, "persist")
    assert engine2.get("a") == {"n": 1}
    assert engine2.get("b") is None  # deletion was persisted


def test_persist_writes_through_without_close(tmp_path):
    engine, _ = _persistent_engine(tmp_path, "persist")
    engine.set("x", 42)  # write-through: on disk immediately, no close needed

    engine2, _ = _persistent_engine(tmp_path, "persist")
    assert engine2.get("x") == 42


# --- persist-reset mode (periodic + on-close) ------------------------------
def test_persist_reset_flushes_on_close(tmp_path):
    engine, persistence = _persistent_engine(
        tmp_path, "persist-reset", flush_interval=3600
    )
    engine.set("k", "v")  # deferred; the long interval will not fire in the test
    persistence.close()  # final flush

    engine2, _ = _persistent_engine(tmp_path, "persist-reset")
    assert engine2.get("k") == "v"


def test_persist_reset_flushes_on_interval(tmp_path):
    engine, persistence = _persistent_engine(
        tmp_path, "persist-reset", flush_interval=0.1
    )
    try:
        engine.set("k", "v")
        # The timer thread flushes within an interval. Poll a fresh reader until
        # the value is fully visible (chunk + index are written in two steps, so
        # asserting on chunk-file existence alone would be racy).
        _wait_until(
            lambda: ChunkedStore(str(tmp_path)).load_all().get("k") == ("v", None),
            timeout=5,
        )
    finally:
        persistence.close()


def test_persist_reset_final_flush_on_backend_close(tmp_path):
    """persist-reset must flush pending writes through the real backend close
    path (LocalSharedStorage.close -> _Coordinator.close -> StoreEngine.close),
    not only when _Persistence.close is called directly."""
    ns = f"reset-close-{uuid.uuid4().hex[:8]}"
    path = str(tmp_path / "store")

    s1 = LocalSharedStorage(
        namespace=ns, mode="persist-reset", path=path, flush_interval=3600
    )
    s1.start()
    s1.set("k", "v")  # deferred; the long interval will not fire
    s1.close()  # must trigger the final flush

    s2 = LocalSharedStorage(
        namespace=ns, mode="persist-reset", path=path, flush_interval=3600
    )
    s2.start()
    try:
        assert s2.get("k") == "v"
    finally:
        s2.close()


def test_persist_concurrent_writes_to_same_key_stay_consistent(tmp_path):
    """Under write-through, once all set() calls return the on-disk value must
    match the engine's final value -- no stale snapshot may win the race."""
    engine, persistence = _persistent_engine(tmp_path, "persist")
    try:
        barrier = threading.Barrier(8)

        def writer(i):
            barrier.wait()
            for _ in range(50):
                engine.set("k", i)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        final = engine.get("k")
        on_disk = ChunkedStore(str(tmp_path)).load_all()["k"][0]
        assert on_disk == final
    finally:
        persistence.close()


# --- TTL across a restart --------------------------------------------------
def test_ttl_expiry_survives_restart(monkeypatch):
    # Uses a real tmp dir via monkeypatched clocks so expiry is deterministic.
    import tempfile

    from dash._shared_storage import _engine

    directory = tempfile.mkdtemp()
    wall = {"t": 1_000_000.0}
    mono = {"t": 5_000.0}
    monkeypatch.setattr(_engine.time, "time", lambda: wall["t"])
    monkeypatch.setattr(_engine.time, "monotonic", lambda: mono["t"])

    engine, persistence = _persistent_engine(directory, "persist")
    engine.set("gone", "v", ttl=10)
    engine.set("stay", "v", ttl=10_000)
    persistence.close()

    # Time advances past the short ttl but not the long one, then a new process
    # (fresh monotonic base) recovers.
    wall["t"] += 100
    mono["t"] = 0.0  # monotonic resets across a "restart"
    engine2, _ = _persistent_engine(directory, "persist")
    assert engine2.get("gone", "expired") == "expired"
    assert engine2.get("stay") == "v"


def _wait_until(pred, timeout):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if pred():
            return
        time.sleep(0.02)
    raise AssertionError("condition not met in time")
