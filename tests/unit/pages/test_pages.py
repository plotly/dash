from pathlib import Path

import pytest
from dash._pages import _infer_path, CONFIG
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
    with patch.dict(CONFIG, {"pages_folder": pages_folder}, clear=True):
        result = _infer_path(filename, template)
        assert result == expected
