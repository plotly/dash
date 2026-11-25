import runpy
from pathlib import Path
from unittest import mock

import setuptools

ROOT = Path(__file__).resolve().parents[2]


def test_only_dash_is_packaged(monkeypatch):
    # A stray top-level package in the wheel (for example the repo's benchmarks
    # harness) shadows a directory of the same name in every project that
    # installs dash.
    monkeypatch.chdir(ROOT)
    with mock.patch.object(setuptools, "setup") as setup:
        runpy.run_path(str(ROOT / "setup.py"))

    packages = setup.call_args.kwargs["packages"]
    assert "dash" in packages
    assert "dash.testing" in packages
    assert [p for p in packages if p != "dash" and not p.startswith("dash.")] == []
