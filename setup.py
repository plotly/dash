"""
Deprecated setup.py - use pyproject.toml instead.

This file is kept for backward compatibility only.
Modern installations should use:
    pip install .
    uv pip install .
    uv sync

For development:
    uv sync --extra dev --extra testing
"""

import warnings
from setuptools import setup

warnings.warn(
    "setup.py is deprecated. Use pyproject.toml for modern Python packaging. "
    "This setup.py is provided for backward compatibility only.",
    DeprecationWarning,
    stacklevel=2,
)

# Minimal setup() call - all configuration is now in pyproject.toml
setup()
