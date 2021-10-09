import dash
from dash.testing import wait
from selenium.webdriver.common.keys import Keys

from utils import (
    basic_modes,
    get_props,
    generate_mock_data,
    generate_markdown_mock_data,
    generate_mixed_markdown_data,
)

from dash.dash_table import DataTable

import pytest


def scroll_table_by(test, value):
    test.driver.execute_script(
        "document.querySelector('#table .dt-table-container__row-1').scrollBy(0, {});".format(
            value
        )
    )


def scroll_window_by(test, value):
    test.driver.execute_script("window.scrollBy(0, {});".format(value))


def get_app(props, data_fn=generate_mock_data):
    app = dash.Dash(__name__)

    baseProps = get_props(data_fn=data_fn)

    baseProps.update(props)

    app.layout = DataTable(**baseProps)

    return app


@pytest.mark.parametrize("props", basic_modes)
@pytest.mark.parametrize(
    "data_fn",
    [generate_mock_data, generate_markdown_mock_data, generate_mixed_markdown_data],
)
def test_scrv001_select_on_scroll(test, props, data_fn):
    test.start_server(get_app(props, data_fn))

    target = test.table("table")
    target.cell(2, 2).click()

    assert target.cell(2, 2).is_focused()

    scroll_window_by(test, 2000)

    assert not target.cell(2, 2).exists() or target.cell(2, 2).is_focused()
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "props",
    [
        dict(virtualization=True, fixed_columns=True),
        dict(virtualization=True, fixed_rows=True),
        dict(virtualization=True, fixed_columns=True, fixed_rows=True),
    ],
)
def test_scrv002_virtualization_keeps_focused(test, props):
    test.start_server(get_app(props))

    target = test.table("table")
    target.cell(0, "rows").click()

    assert target.cell(0, "rows").is_focused()

    scroll_table_by(test, 2000)
    wait.until(lambda: not target.cell(0, "rows").exists(), 3)

    scroll_table_by(test, -2000)
    wait.until(lambda: target.cell(0, "rows").is_focused(), 3)

    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "props",
    [
        dict(virtualization=True, fixed_columns=True),
        dict(virtualization=True, fixed_rows=True),
        dict(virtualization=True, fixed_columns=True, fixed_rows=True),
    ],
)
def test_scrv003_virtualization_keeps_selection(test, props):
    test.start_server(get_app(props))

    target = test.table("table")
    target.cell(0, 0).click()

    with test.hold(Keys.SHIFT):
        target.cell(2, 2).click()

    for row in range(3):
        for col in range(3):
            assert target.cell(row, col).is_selected()

    scroll_table_by(test, 2000)
    for row in range(3):
        for col in range(3):
            wait.until(lambda: not target.cell(row, col).exists(), 3)

    scroll_table_by(test, -2000)
    for row in range(3):
        for col in range(3):
            assert target.cell(row, col).is_selected()

    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "props",
    [
        dict(virtualization=True, fixed_columns=True),
        dict(virtualization=True, fixed_rows=True),
        dict(virtualization=True, fixed_columns=True, fixed_rows=True),
    ],
)
def test_scrv004_virtualization_can_edit(test, props):
    test.start_server(get_app(props))

    target = test.table("table")
    target.cell(1, 1).click()

    test.send_keys("abc" + Keys.ENTER)
    wait.until(lambda: target.cell(1, 1).get_text() == "abc", 3)

    scroll_table_by(test, 2500)
    target.cell(80, 1).click()

    test.send_keys("def" + Keys.ENTER)
    wait.until(lambda: target.cell(80, 1).get_text() == "def", 3)

    assert test.get_log_errors() == []
