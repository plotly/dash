from contextlib import contextmanager
import os
from pathlib import Path

import pytest

from dash import Dash, exceptions as _exc
from dash._configs import pages_folder_config


THIS_DIR = Path(__file__).parent


@contextmanager
def does_not_raise():
    """Context manager for testing no exception is raised"""
    yield


@pytest.mark.parametrize(
    "pages_folder, use_pages, expected_pages_folder_path",
    [
        ("", False, None),
        (None, False, None),
        ("pages", False, str(THIS_DIR / "pages")),
        (Path("pages"), False, str(THIS_DIR / "pages")),
        ("custom_pages", True, str(THIS_DIR / "custom_pages")),
        ("custom_pages", False, str(THIS_DIR / "custom_pages")),
        (
            str(THIS_DIR / "custom_pages"),
            True,
            str(THIS_DIR / "custom_pages"),
        ),
        (
            str(THIS_DIR / "custom_pages"),
            False,
            str(THIS_DIR / "custom_pages"),
        ),
        (
            THIS_DIR / "custom_pages",
            False,
            str(THIS_DIR / "custom_pages"),
        ),
    ],
)
def test_pages_folder_path_config(
    empty_environ, pages_folder, use_pages, expected_pages_folder_path
):
    pages_folder_path = pages_folder_config(__name__, pages_folder, use_pages)
    assert pages_folder_path == expected_pages_folder_path


@pytest.mark.parametrize(
    "pages_folder, use_pages, expectation",
    [
        ("pages", False, does_not_raise()),
        ("pages", True, pytest.raises(_exc.InvalidConfig)),
        ("does_not_exist", True, pytest.raises(_exc.InvalidConfig)),
        ("does_not_exist", False, pytest.raises(_exc.InvalidConfig)),
    ],
)
def test_pages_missing_path_config(empty_environ, pages_folder, use_pages, expectation):
    with expectation:
        _ = pages_folder_config(__name__, pages_folder, use_pages)


def test_pages_custom_path_config(empty_environ, clear_page_registry):
    app = Dash(__name__, pages_folder="custom_pages")
    assert app.use_pages


def test_pages_pathlib_config(empty_environ, clear_page_registry):
    app = Dash(__name__, pages_folder=Path("custom_pages"))
    assert app.use_pages
    assert app.pages_folder == "custom_pages"


def test_pages_absolute_path_config(empty_environ, clear_page_registry):
    pages_path = str(THIS_DIR / "custom_pages")
    app = Dash(__name__, pages_folder=pages_path)
    assert app.use_pages
    assert app.pages_folder == pages_path
