"""Without msgspec, the in-memory backend still works over its socket
transport, and every backend that writes encoded bytes somewhere lasting
refuses to start with a pointer to the extra that brings it.

Each case runs in a fresh interpreter with msgspec blocked, so the codec picks
its fallback at import time just as it would in a real install.
"""
import subprocess
import sys
import textwrap
import uuid

import pytest

PRELUDE = "import sys\nsys.modules['msgspec'] = None\n"


def _run(code):
    proc = subprocess.run(
        [sys.executable, "-c", PRELUDE + textwrap.dedent(code)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def test_memory_mode_crosses_processes_as_json():
    out = _run(
        f"""
        from dash._shared_storage import LocalSharedStorage, _codec

        assert not _codec.HAS_MSGSPEC
        owner = LocalSharedStorage(namespace="nomsgspec-{uuid.uuid4().hex[:12]}")
        owner.start()
        client = LocalSharedStorage(namespace=owner._coord._namespace)
        client.start()
        assert owner._coord.is_owner() and not client._coord.is_owner()

        client.set("k", {{"a": [1, 2.5, None, True, "x"]}})
        assert owner.get("k") == {{"a": [1, 2.5, None, True, "x"]}}
        sub = client.subscribe("t")
        owner.publish("t", {{"n": 1}})
        print(sub.poll(timeout=5))
        sub.close()
        client.close()
        owner.close()
        """
    )
    assert out.strip() == "[(1, {'n': 1})]"


@pytest.mark.parametrize(
    "setup, what, extra",
    [
        (
            "from dash._shared_storage import LocalSharedStorage\n"
            "LocalSharedStorage(mode='persist', path='{tmp}')",
            "LocalSharedStorage(mode='persist')",
            "shared_storage",
        ),
        (
            "from dash._shared_storage import LocalSharedStorage\n"
            "LocalSharedStorage(mode='persist-reset', path='{tmp}')",
            "LocalSharedStorage(mode='persist-reset')",
            "shared_storage",
        ),
        (
            "from dash._shared_storage import DiskcacheSharedStorage\n"
            "DiskcacheSharedStorage(directory='{tmp}')",
            "DiskcacheSharedStorage",
            "diskcache",
        ),
        (
            "from dash._shared_storage import RedisSharedStorage\n"
            "RedisSharedStorage(url='redis://localhost:6399/0')",
            "RedisSharedStorage",
            "redis",
        ),
        (
            "import os\nos.environ['DASH_SHARED_STORAGE'] = 'redis://localhost:6399/0'\n"
            "from dash import Dash\nDash(__name__)",
            "RedisSharedStorage",
            "redis",
        ),
        (
            "import os\nos.environ['DASH_SHARED_STORAGE'] = 'diskcache://{tmp}'\n"
            "from dash import Dash\nDash(__name__)",
            "DiskcacheSharedStorage",
            "diskcache",
        ),
    ],
)
def test_lasting_backends_need_the_extra(tmp_path, setup, what, extra):
    out = _run(
        "try:\n"
        + textwrap.indent(setup.format(tmp=tmp_path), "    ")
        + "\nexcept ImportError as err:\n    print(err)\n"
    )
    assert f"{what} requires the {extra} extra" in out
    assert f'pip install "dash[{extra}]"' in out
