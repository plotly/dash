"""On-disk persistence for the local shared-storage engine.

Only the elected owner persists; clients proxy to it. The store is *chunked* --
keys are sharded across fixed-size chunk files via a key->chunk index, so a
single mutation rewrites only the affected chunk rather than the whole store
(the design is adapted from raposa's ``BinaryStorage``). Serialization is
msgspec msgpack via :mod:`._codec`; each chunk write is atomic (temp file +
``os.replace``).

Two modes drive *when* the store is written:

- ``persist``: write-through -- every set/delete flushes the changed key's chunk
  before returning, so a crash loses nothing already acknowledged.
- ``persist-reset``: in-memory speed; a background thread flushes dirty keys on a
  timer, plus a final flush on close. Up to one interval of writes can be lost on
  an unclean crash.

Both recover the whole store on start (and on owner re-election). TTL is stored
on disk as an absolute wall-clock deadline (``time.time()``); the engine's
in-memory ``time.monotonic()`` deadlines are not comparable across a restart, so
they are converted on the way in and out.
"""

import logging
import os
import sys
import threading
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import _codec

logger = logging.getLogger(__name__)

# Keys per chunk file before a new chunk is opened. Chunked writes keep the
# per-mutation cost bounded to one chunk instead of the whole store.
_CHUNK_SIZE = 1000
_INDEX_VERSION = 1


def _user_cache_dir() -> str:
    """Best-effort per-user cache directory, without any extra dependency."""
    if sys.platform == "win32":
        return os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Caches")
    return os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")


def default_store_dir(namespace: str) -> str:
    """Default on-disk location for a persistent store in ``namespace``."""
    return os.path.join(_user_cache_dir(), "dash", "shared_storage", namespace)


def _atomic_write_bytes(path: str, data: bytes) -> None:
    """Write ``data`` to ``path`` atomically (temp file in the same dir + rename)."""
    tmp = f"{path}.{os.getpid()}.tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    os.replace(tmp, path)


class ChunkedStore:
    """A key/value store sharded across msgpack chunk files on disk.

    Layout under ``directory``::

        index.msgpack    {"v": 1, "keys": {key: chunk_num}}
        chunk_0.msgpack  {"records": {key: [value, expire_at | None]}}
        chunk_1.msgpack
        ...

    ``expire_at`` is an absolute wall-clock deadline in epoch seconds, or
    ``None`` for no expiry. Thread-safe via a single re-entrant lock -- the store
    is small enough that per-chunk locking would not pay off. A missing or
    corrupt file is treated as empty rather than an error.

    Single-writer: an instance caches the index/chunks in memory and each write
    serializes its own view, so exactly one instance may be active per directory
    at a time. The owner-election design guarantees this (one owner per
    namespace); a caller that points two live backends at the same explicit
    ``path`` can lose writes.
    """

    def __init__(self, directory: str, chunk_size: int = _CHUNK_SIZE):
        self._dir = directory
        self._chunk_size = chunk_size
        self._lock = threading.RLock()
        self._keys: Dict[str, int] = {}  # key -> chunk_num
        self._chunks: Dict[
            int, Dict[str, Any]
        ] = {}  # chunk_num -> {key: [value, expire_at]}
        self._loaded = False
        os.makedirs(self._dir, exist_ok=True)

    # --- paths -------------------------------------------------------------
    def _index_path(self) -> str:
        return os.path.join(self._dir, "index.msgpack")

    def _chunk_path(self, chunk_num: int) -> str:
        return os.path.join(self._dir, f"chunk_{chunk_num}.msgpack")

    # --- disk io -----------------------------------------------------------
    @staticmethod
    def _read(path: str) -> Optional[Any]:
        """Decode ``path``; return None if it is absent or unreadable/corrupt."""
        try:
            with open(path, "rb") as f:
                return _codec.decode(f.read())
        except (OSError, ValueError):
            # OSError -> missing/unreadable; ValueError -> msgspec DecodeError.
            return None

    def _write_chunk(self, chunk_num: int) -> None:
        data = _codec.encode({"records": self._chunks.get(chunk_num, {})})
        _atomic_write_bytes(self._chunk_path(chunk_num), data)

    def _write_index(self) -> None:
        data = _codec.encode({"v": _INDEX_VERSION, "keys": self._keys})
        _atomic_write_bytes(self._index_path(), data)

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        index = self._read(self._index_path())
        keys: Dict[str, int] = {}
        if isinstance(index, dict) and index.get("v") == _INDEX_VERSION:
            raw_keys = index.get("keys")
            if isinstance(raw_keys, dict):
                keys = raw_keys
        for chunk_num in set(keys.values()):
            chunk = self._read(self._chunk_path(chunk_num))
            records = chunk.get("records") if isinstance(chunk, dict) else None
            self._chunks[chunk_num] = records if isinstance(records, dict) else {}
        # Keep only keys whose chunk actually holds the record; a partial write
        # (index ahead of chunk) should not surface a phantom key.
        self._keys = {
            key: cn
            for key, cn in keys.items()
            if cn in self._chunks and key in self._chunks[cn]
        }
        self._loaded = True

    def _find_chunk_with_space(self) -> int:
        counts: Dict[int, int] = {}
        for chunk_num in self._keys.values():
            counts[chunk_num] = counts.get(chunk_num, 0) + 1
        chunk_num = 0
        while counts.get(chunk_num, 0) >= self._chunk_size:
            chunk_num += 1
        return chunk_num

    # --- public api --------------------------------------------------------
    def load_all(self) -> Dict[str, Tuple[Any, Optional[float]]]:
        """Return every stored ``key -> (value, expire_at)``."""
        with self._lock:
            self._ensure_loaded()
            out: Dict[str, Tuple[Any, Optional[float]]] = {}
            for key, chunk_num in self._keys.items():
                record = self._chunks[chunk_num].get(key)
                if record is not None:
                    out[key] = (record[0], record[1])
            return out

    def put_batch(self, items: Dict[str, Tuple[Any, Optional[float]]]) -> None:
        """Insert/update many records, writing each touched chunk only once."""
        if not items:
            return
        with self._lock:
            self._ensure_loaded()
            touched: set = set()
            new_keys = False
            for key, (value, expire_at) in items.items():
                chunk_num = self._keys.get(key)
                if chunk_num is None:
                    chunk_num = self._find_chunk_with_space()
                    self._chunks.setdefault(chunk_num, {})
                    self._keys[key] = chunk_num
                    new_keys = True
                self._chunks[chunk_num][key] = [value, expire_at]
                touched.add(chunk_num)
            for chunk_num in touched:
                self._write_chunk(chunk_num)
            if new_keys:
                self._write_index()

    def delete(self, key: str) -> None:
        with self._lock:
            self._ensure_loaded()
            chunk_num = self._keys.pop(key, None)
            if chunk_num is None:
                return
            chunk = self._chunks.get(chunk_num)
            if chunk is not None:
                chunk.pop(key, None)
                self._write_chunk(chunk_num)
            self._write_index()


class _Persistence:
    """Policy layer wiring a :class:`ChunkedStore` to a ``StoreEngine``.

    The engine reports each mutation via :meth:`mark`; ``persist`` flushes it
    through immediately while ``persist-reset`` defers to a background timer. All
    file IO runs outside the engine's data lock -- :meth:`_flush` pulls the
    current value/expiry back from the engine via ``snapshot_keys``.
    """

    def __init__(self, directory: str, mode: str, flush_interval: float, engine):
        self._store = ChunkedStore(directory)
        self._mode = mode
        self._flush_interval = flush_interval
        self._engine = engine
        self._dirty: set = set()
        self._dirty_lock = threading.Lock()
        # Serializes the snapshot->write pair in _flush so two concurrent
        # write-through flushers (persist mode) cannot reorder their disk writes
        # and clobber a newer value with an older one.
        self._flush_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._closed = False

    def recover(self) -> None:
        """Load the on-disk store into the engine (start / owner re-election)."""
        self._engine.restore(self._store.load_all())

    def start(self) -> None:
        if self._mode == "persist-reset":
            self._thread = threading.Thread(
                target=self._run, name="dash-shared-persist", daemon=True
            )
            self._thread.start()

    def mark(self, key: str) -> None:
        if self._mode == "persist":
            self._flush([key])
        else:
            with self._dirty_lock:
                self._dirty.add(key)

    def _drain(self) -> List[str]:
        with self._dirty_lock:
            keys = list(self._dirty)
            self._dirty.clear()
        return keys

    def _flush(self, keys: Iterable[str]) -> None:
        keys = list(keys)
        if not keys:
            return
        # Hold _flush_lock across the read-from-engine + write-to-disk so a
        # slower flush cannot land a stale snapshot after a newer one. Because
        # snapshot_keys reads the *current* engine state, a flush that waits
        # here re-reads the latest value once it acquires the lock.
        with self._flush_lock:
            state = self._engine.snapshot_keys(keys)  # {key: (value, expire_at)}
            puts = {key: state[key] for key in keys if key in state}
            for key in keys:
                if key not in state:
                    self._store.delete(key)
            if puts:
                self._store.put_batch(puts)

    def _run(self) -> None:
        while not self._stop.wait(self._flush_interval):
            try:
                self._flush(self._drain())
            except Exception:  # pylint: disable=broad-except
                # A single bad cycle (e.g. disk full, unserializable value) must
                # not silently kill the flush thread and stop all persistence.
                logger.exception("shared-storage persist-reset flush failed")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self._flush_interval + 5)
        # Final flush of anything still dirty (persist-reset); persist has none.
        self._flush(self._drain())
