from pathlib import Path

import pytest
import dash
from dash import Dash, _pages
from mock import patch


THIS_DIR = Path(__file__).parent


@pytest.mark.parametrize(
    "filename, template, pages_folder, expected",
    [
        ("pages.page1", None, str(THIS_DIR / "pages"), "/page1"),
        ("Pages.page1", None, str(THIS_DIR / "Pages"), "/page1"),
        ("custom_pages.page1", None, str(THIS_DIR / "custom_pages"), "/page1"),
        ("custom.pages.page1", None, str(THIS_DIR / "custom.pages"), "/page1"),
        ("custom.pages.page1", None, str(THIS_DIR / "custom" / "pages"), "/page1"),
        # can this even be called with  CONFIG.pages_folder set to None?
        ("dir.my_page", None, None, "/dir/my-page"),
        # is this behaviour right? why is filename ignored when template has a value?
        ("pages.page1", "/items/<item_id>", str(THIS_DIR / "pages"), "/items/none"),
    ],
)
def test_infer_path(mocker, filename, template, pages_folder, expected):
    with patch.dict(_pages.CONFIG, {"pages_folder": pages_folder}, clear=True):
        result = _pages._infer_path(filename, template)
        assert result == expected


@pytest.mark.parametrize(
    "pages_folder, expected_module_name",
    [
        ("custom_pages", "custom_pages.page"),
        ("sub_dir/custom_pages", "sub_dir.custom_pages.page"),
        (str(THIS_DIR / "custom_pages"), "custom_pages.page"),
    ],
)
def test_import_layouts_from_pages(
    clear_pages_state, pages_folder, expected_module_name
):
    _ = Dash(__name__, use_pages=True, pages_folder=pages_folder)
    assert len(dash.page_registry) == 1

    page_entry = list(dash.page_registry.values())[0]
    assert page_entry["module"] == expected_module_name
