"""
Configuration for build tests.
"""

import shutil
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_build_environment():
    """Ensure we're in the right directory and have required tools."""
    # Ensure we're in the project root
    current_dir = Path.cwd()

    required_files = [
        "pyproject.toml",
        "dash/__init__.py",
    ]

    for required_file in required_files:
        file_path = current_dir / required_file
        if not file_path.exists():
            pytest.skip(
                f"Required file {required_file} not found. Tests must be run from project root."
            )

    # Check for uv
    if not shutil.which("uv"):
        pytest.skip("uv command not found. Install uv to run build tests.")


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    return Path.cwd()


@pytest.fixture
def clean_dist_dir():
    """Ensure dist directory is clean before tests."""
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    yield

    # Cleanup after test
    if dist_dir.exists():
        shutil.rmtree(dist_dir)


# Mark all tests in this module as slow since they involve building packages
def pytest_collection_modifyitems(config, items):  # pylint: disable=unused-argument
    """Add slow marker to all build tests."""
    for item in items:
        if "test_build" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
