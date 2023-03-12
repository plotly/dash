from contextlib import contextmanager
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
        ("sub_dir/custom_pages", True, str(THIS_DIR / "sub_dir" / "custom_pages")),
    ],
)
def test_pages_folder_config(
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


@pytest.mark.parametrize(
    "use_pages, pages_folder",
    [
        (True, "custom_pages"),
        (True, Path("custom_pages")),
        (True, str(THIS_DIR / "custom_pages")),
        (True, THIS_DIR / "custom_pages"),
        (True, str(THIS_DIR / "sub_dir" / "custom_pages")),
        (True, THIS_DIR / "sub_dir" / "custom_pages"),
        (None, "custom_pages"),
        (None, "pages"),
        (False, "custom_pages"),
    ],
)
def test_pages_folder_app_config(
    empty_environ, clear_pages_state, use_pages, pages_folder
):
    app = Dash(__name__, use_pages=use_pages, pages_folder=pages_folder)
    if use_pages is None:
        expected_use_pages = bool(pages_folder != "pages")
    elif use_pages in (True, False):
        expected_use_pages = use_pages
    assert app.use_pages == expected_use_pages
    assert app.pages_folder == str(pages_folder)
