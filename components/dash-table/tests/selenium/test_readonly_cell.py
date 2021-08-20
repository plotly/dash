import dash

from utils import get_props, generate_mock_data

from dash.dash_table import DataTable

import pytest


def get_app(props=dict(), data_fn=generate_mock_data):
    app = dash.Dash(__name__)

    baseProps = get_props(data_fn=data_fn)

    baseProps.update(props)

    app.layout = DataTable(**baseProps)

    return app


@pytest.mark.parametrize(
    "props", [dict(virtualization=False), dict(virtualization=True)]
)
def test_tbed001_readonly_text(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    readonly_cell = target.cell(0, "aaa-readonly")
    cell = target.cell(0, "aaa")

    readonly_cell.click()
    assert not readonly_cell.is_input() and not readonly_cell.is_dropdown()

    cell.click()
    assert cell.is_input()

    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "props", [dict(virtualization=False), dict(virtualization=True)]
)
def test_tbed002_readonly_dropdown(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    readonly_cell = target.cell(0, "bbb-readonly")
    cell = target.cell(0, "bbb")

    readonly_cell.click()
    assert not readonly_cell.is_input() and not readonly_cell.is_dropdown()

    cell.click()
    assert cell.is_dropdown()
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "props", [dict(virtualization=False), dict(virtualization=True)]
)
def test_tbed003_readonly_copy_paste(test, props):
    test.start_server(get_app(props))

    target = test.table("table")
    initial_text = target.cell(1, "aaa-readonly").get_text()

    cell_source = target.cell(0, "aaa")
    cell_target = target.cell(1, "aaa-readonly")

    cell_source.click()
    test.copy()

    cell_target.click()
    test.paste()

    assert cell_target.get_text() == initial_text
    assert test.get_log_errors() == []
