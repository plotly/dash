"""Give each streaming test its own shared-storage namespace.

The default namespace is derived from cwd + argv so that every worker process of
one app shares an owner. In the test suite, though, many apps run in a single
process; without isolation they would contend for one owner and reset each
other's connections at teardown. Patching the default namespace per test keeps
each app its own owner.
"""
import uuid

import pytest

import dash._shared_storage.local as _local
from dash._streaming import _shutdown as _streaming_shutdown


@pytest.fixture(autouse=True)
def _isolate_shared_storage(monkeypatch):
    namespace = f"streamtest-{uuid.uuid4().hex[:12]}"
    monkeypatch.setattr(_local, "_default_namespace", lambda: namespace)
    yield


@pytest.fixture(autouse=True)
def _clear_stream_shutdown_flag():
    """A server shutting down in an earlier test (a dash_duo teardown, a
    TestClient lifespan exit) sets the streaming shutdown flag, and only a
    server start clears it. Unit tests that drive the frame generators directly
    would otherwise exit them immediately."""
    _streaming_shutdown.clear()
    yield
    _streaming_shutdown.clear()
