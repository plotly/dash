import dash
from dash.testing import wait

from utils import (
    basic_modes,
    get_props,
    generate_mock_data,
    generate_markdown_mock_data,
    generate_mixed_markdown_data,
)

from dash.dash_table import DataTable

import pytest


def get_app(props, data_fn):
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
def test_mnav001_navigate_to_self(test, props, data_fn):
    test.start_server(get_app(props, data_fn))

    target = test.table("table")
    cell = target.cell(3, 1)

    cell.click()
    wait.until(lambda: cell.is_focused(), 3)

    cell.click()
    wait.until(lambda: cell.is_focused(), 3)

    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", basic_modes)
@pytest.mark.parametrize(
    "data_fn",
    [generate_mock_data, generate_markdown_mock_data, generate_mixed_markdown_data],
)
def test_mnav002_navigate_to_other(test, props, data_fn):
    test.start_server(get_app(props, data_fn))

    target = test.table("table")
    cell1 = target.cell(3, 1)
    cell2 = target.cell(4, 2)

    cell1.click()
    wait.until(lambda: cell1.is_focused(), 3)

    cell2.click()
    wait.until(lambda: cell2.is_focused(), 3)
    wait.until(lambda: not cell1.is_focused(), 3)

    assert test.get_log_errors() == []
