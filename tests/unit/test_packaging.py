from pathlib import Path

from setuptools.config.pyprojecttoml import apply_configuration
from setuptools.dist import Distribution

ROOT = Path(__file__).resolve().parents[2]


def test_only_dash_is_packaged(monkeypatch):
    # A stray top-level package in the wheel (for example the repo's benchmarks
    # harness) shadows a directory of the same name in every project that
    # installs dash.
    monkeypatch.chdir(ROOT)
    dist = apply_configuration(Distribution(), ROOT / "pyproject.toml")

    packages = dist.packages
    assert "dash" in packages
    assert "dash.testing" in packages
    assert [p for p in packages if p != "dash" and not p.startswith("dash.")] == []
