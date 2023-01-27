from pathlib import Path

import pytest
import dash
from dash import Dash, _pages
from mock import patch


THIS_DIR = Path(__file__).parent


@pytest.mark.parametrize(
    "module_name, template, pages_folder, expected",
    [
        ("pages.page1", None, str(THIS_DIR / "pages"), "/page1"),
        ("Pages.page1", None, str(THIS_DIR / "Pages"), "/page1"),
        ("custom_pages.page1", None, str(THIS_DIR / "custom_pages"), "/page1"),
        ("custom.pages.page1", None, str(THIS_DIR / "custom.pages"), "/page1"),
        ("custom.pages.page1", None, str(THIS_DIR / "custom" / "pages"), "/page1"),
        (
            "custom_pages.chapter_1.page_1",
            None,
            str(THIS_DIR / "custom_pages"),
            "/chapter-1/page-1",
        ),
        # can this even be called with  CONFIG.pages_folder set to None?
        ("dir.my_page", None, None, "/dir/my-page"),
        # is this behaviour right? why is filename ignored when template has a value?
        ("pages.page1", "/items/<item_id>", str(THIS_DIR / "pages"), "/items/none"),
    ],
)
def test_infer_path(clear_pages_state, module_name, template, pages_folder, expected):
    with patch.dict(_pages.CONFIG, {"pages_folder": pages_folder}, clear=True):
        result = _pages._infer_path(module_name, template)
        assert result == expected


@pytest.mark.parametrize(
    "module_name, expected",
    [
        (__name__, False),
        (__package__, True),
    ],
)
def test_module_name_is_package(module_name, expected):
    assert _pages._module_name_is_package(module_name) == expected


@pytest.mark.parametrize(
    "path, expected",
    [
        ("/page.py", "page"),
        ("/pages/page.py", "pages.page"),
        ("/pages", "pages"),
        ("/sub_dir/pages", "sub_dir.pages"),
    ],
)
def test_path_to_module_name(path, expected):
    assert _pages._path_to_module_name(path) == expected


@pytest.mark.parametrize(
    "name, pages_folder, expected_module_name",
    [
        (__name__, "custom_pages", "custom_pages.page"),
        (__name__, "sub_dir/custom_pages", "sub_dir.custom_pages.page"),
        (__name__, str(THIS_DIR / "custom_pages"), "custom_pages.page"),
        (__package__, "custom_pages", "pages.custom_pages.page"),
    ],
)
def test_import_layouts_from_pages(
    clear_pages_state, name, pages_folder, expected_module_name
):
    _ = Dash(name, use_pages=True, pages_folder=pages_folder)
    assert len(dash.page_registry) == 1

    page_entry = list(dash.page_registry.values())[0]
    assert page_entry["module"] == expected_module_name
