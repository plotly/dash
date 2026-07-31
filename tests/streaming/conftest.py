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


@pytest.fixture(autouse=True)
def _isolate_shared_storage(monkeypatch):
    namespace = f"streamtest-{uuid.uuid4().hex[:12]}"
    monkeypatch.setattr(_local, "_default_namespace", lambda: namespace)
    yield
