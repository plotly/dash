import dash
from dash.testing import wait

from utils import get_props, generate_markdown_mock_data

from dash.dash_table import DataTable
import pytest


def get_app(props=dict(), data_fn=generate_markdown_mock_data, assets_folder=None):
    app = (
        dash.Dash(__name__)
        if assets_folder is None
        else dash.Dash(__name__, assets_folder=assets_folder)
    )

    baseProps = get_props(data_fn=data_fn)

    baseProps.update(dict(filter_action="native", sort_action="native"))
    baseProps.update(props)

    app.layout = DataTable(**baseProps)

    return app


def test_mark001_header(test):
    test.start_server(get_app())

    target = test.table("table")

    target.column(0).sort(1)
    assert (
        target.cell(0, "markdown-headers")
        .find_inside(".dash-cell-value > p")
        .get_attribute("innerHTML")
        == "row 0"
    )

    target.column(0).sort(1)
    assert (
        target.cell(0, "markdown-headers")
        .find_inside(".dash-cell-value > h5")
        .get_attribute("innerHTML")
        == "row 95"
    )


def test_mark002_emphasized_text(test):
    test.start_server(get_app())

    target = test.table("table")

    target.column(1).sort(1)
    assert (
        target.cell(0, "markdown-italics")
        .find_inside(".dash-cell-value > p > em")
        .get_attribute("innerHTML")
        == "1"
    )

    target.column(1).sort(1)
    assert (
        target.cell(0, "markdown-italics")
        .find_inside(".dash-cell-value > p > em")
        .get_attribute("innerHTML")
        == "98"
    )


def test_mark003_link(test):
    test.start_server(get_app())

    target = test.table("table")

    target.column(2).sort(1)
    assert (
        target.cell(0, "markdown-links")
        .find_inside(".dash-cell-value > p > a")
        .get_attribute("innerHTML")
        == "Learn about 0"
    )

    target.column(2).sort(1)
    assert (
        target.cell(0, "markdown-links")
        .find_inside(".dash-cell-value > p > a")
        .get_attribute("innerHTML")
        == "Learn about 9"
    )


def test_mark004_image(test):
    test.start_server(get_app())

    target = test.table("table")

    target.column(8).sort(1)
    assert (
        target.cell(0, "markdown-images")
        .find_inside(".dash-cell-value > p > img")
        .get_attribute("alt")
        == "image 0 alt text"
    )

    target.column(8).sort(1)
    assert (
        target.cell(0, "markdown-images")
        .find_inside(".dash-cell-value > p > img")
        .get_attribute("alt")
        == "image 99 alt text"
    )


def test_mark005_table(test):
    test.start_server(get_app())

    target = test.table("table")

    target.column(4).sort(1)
    assert (
        target.cell(0, "markdown-tables")
        .find_inside(".dash-cell-value > table > tbody > tr > td")
        .get_attribute("innerHTML")
        == "0"
    )

    target.column(4).sort(1)
    assert (
        target.cell(0, "markdown-tables")
        .find_inside(".dash-cell-value > table > tbody > tr > td")
        .get_attribute("innerHTML")
        == "99"
    )


@pytest.mark.parametrize(
    "filter",
    ["Learn about 97", "/wiki/97"],
)
def test_mark006_filter_link_text(test, filter):
    test.start_server(get_app())

    target = test.table("table")
    target.column("markdown-links").filter_value(filter)

    assert (
        target.cell(0, "markdown-links")
        .find_inside(".dash-cell-value > p > a")
        .get_attribute("href")
        == "http://en.wikipedia.org/wiki/97"
    )
    assert not target.cell(1, "markdown-links").exists()


def test_mark007_filter_image_alt_text(test):
    test.start_server(get_app())

    target = test.table("table")
    target.column("markdown-images").filter_value("97")

    assert (
        target.cell(0, "markdown-images")
        .find_inside(".dash-cell-value > p > img")
        .get_attribute("alt")
        == "image 97 alt text"
    )
    assert not target.cell(1, "markdown-images").exists()


def test_mark008_loads_highlightjs(test):
    test.start_server(get_app())

    target = test.table("table")
    wait.until(
        lambda: len(
            target.cell(0, "markdown-code-blocks").find_all_inside(
                "code.language-python"
            )
        )
        == 1,
        3,
    )

    # table loads a private instance of hljs that isn't shared globally
    wait.until(lambda: not test.driver.execute_script("return !!window.hljs"), 3)
    assert test.get_log_errors() == []


def test_mark009_loads_custom_highlightjs(test):
    test.start_server(get_app(assets_folder="./test_markdown_assets"))

    target = test.table("table")
    wait.until(
        lambda: len(
            target.cell(0, "markdown-code-blocks").find_all_inside(
                "code.language-python"
            )
        )
        == 1,
        3,
    )

    wait.until(
        lambda: target.cell(0, "markdown-code-blocks")
        .find_inside("code.language-python")
        .get_attribute("innerHTML")
        == "hljs override",
        3,
    )

    wait.until(lambda: test.driver.execute_script("return !!window.hljs"), 3)
    assert test.get_log_errors() == []
