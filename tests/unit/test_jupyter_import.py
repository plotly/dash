import subprocess
import sys

import pytest

pytest.importorskip("IPython")


def _run(*args):
    result = subprocess.run(
        [sys.executable, *args], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr


def test_import_dash_does_not_load_ipython():
    _run("-c", "import dash, sys; assert 'IPython' not in sys.modules")


def test_jupyter_support_loads_inside_ipython():
    _run(
        "-m",
        "IPython",
        "-c",
        "from dash import _jupyter; "
        "assert _jupyter._dep_installed and _jupyter.jupyter_dash.in_ipython",
    )
