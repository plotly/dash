import sys
from pathlib import Path

import pytest
from setuptools.config.pyprojecttoml import read_configuration

from dash._plotly_cli import cli


def test_plotly_cli_hints_cloud_extra_when_missing(monkeypatch, capsys):
    # A None entry in sys.modules makes the import raise ImportError.
    monkeypatch.setitem(sys.modules, "plotly_cloud", None)
    monkeypatch.setitem(sys.modules, "plotly_cloud.cli", None)

    with pytest.raises(SystemExit) as exc:
        cli()

    assert exc.value.code == -1
    assert "pip install dash[cloud]" in capsys.readouterr().err


def test_plotly_cloud_is_not_an_install_requirement():
    pyproject = Path(__file__).parents[2] / "pyproject.toml"
    dependencies = read_configuration(pyproject)["project"]["dependencies"]
    assert not [d for d in dependencies if d.lower().startswith("plotly-cloud")]
