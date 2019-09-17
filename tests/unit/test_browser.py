import pytest
from dash.testing.browser import Browser
from dash.testing.consts import SELENIUM_GRID_DEFAULT


@pytest.mark.parametrize("browser_type", ("Chrome", "Firefox"))
def test_browser_smoke(browser_type, tmpdir):

    browser = Browser(
        browser=browser_type,
        remote=False,
        remote_url=SELENIUM_GRID_DEFAULT,
        headless=True,
        options=None,
        download_path=tmpdir.mkdir("download").strpath,
        percy_finalize=True,
    )
    assert browser.driver.name == browser_type.lower()


def test_browser_use_remote_webdriver(tmpdir):
    # test creation with remote=True
    with pytest.raises(Exception):
        Browser(
            browser="Chrome",
            remote=True,
            remote_url=SELENIUM_GRID_DEFAULT,
            headless=True,
            options=None,
            download_path=tmpdir.mkdir("download").strpath,
            percy_finalize=True,
        )

    # test creation with remote_url other than default
    with pytest.raises(Exception):
        Browser(
            browser="Chrome",
            remote=False,
            remote_url="http://token@any.selenium.grid:3333",
            headless=True,
            options=None,
            download_path=tmpdir.mkdir("download").strpath,
            percy_finalize=True,
        )
