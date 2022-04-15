import dash
from dash import Input, Output, html, dcc
from dash.exceptions import PreventUpdate
from dash.dash_table import DataTable

import pytest
from selenium.webdriver.common.keys import Keys

import math
import pandas as pd

url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
rawDf = pd.read_csv(url)
df = rawDf.to_dict("records")

PAGE_SIZE = 5
pages = math.ceil(len(df) / PAGE_SIZE)


def get_app(mode, data=df, page_count=None):
    app = dash.Dash(__name__)

    if page_count is None:
        page_count = math.ceil(len(data) / PAGE_SIZE)

    app.layout = DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in rawDf.columns],
        data=data if mode == "native" else data[0:PAGE_SIZE],
        editable=True,
        fixed_columns={"headers": True},
        fixed_rows={"headers": True},
        page_action=mode,
        page_count=page_count,
        page_size=PAGE_SIZE,
        row_deletable=True,
        row_selectable=True,
    )

    if mode == "custom":

        @app.callback(
            [Output("table", "data")],
            [Input("table", "page_current"), Input("table", "page_size")],
        )
        def update_table(page_current, page_size):
            if page_current is None or page_size is None:
                raise PreventUpdate

            return (data[page_current * page_size : (page_current + 1) * page_size],)

    return app


@pytest.mark.parametrize("mode", ["custom", "native"])
def test_tpag001_next_previous(test, mode):
    test.start_server(get_app(mode))

    target = test.table("table")

    assert target.cell(0, 0).get_text() == "0"
    assert target.paging.next.exists()
    assert not target.paging.previous.exists()

    target.paging.next.click()

    assert target.cell(0, 0).get_text() == "5"
    assert target.paging.next.exists()
    assert target.paging.previous.exists()

    target.paging.previous.click()

    assert target.cell(0, 0).get_text() == "0"
    assert target.paging.next.exists()
    assert not target.paging.previous.exists()
    assert test.get_log_errors() == []


@pytest.mark.parametrize("mode", ["custom", "native"])
def test_tpag002_ops_on_first_page(test, mode):
    test.start_server(get_app(mode))

    target = test.table("table")

    assert target.paging.current.get_value() == "1"
    assert not target.paging.first.exists()
    assert not target.paging.previous.exists()
    assert target.paging.next.exists()
    assert target.paging.last.exists()
    assert test.get_log_errors() == []


@pytest.mark.parametrize("mode", ["custom", "native"])
def test_tpag003_ops_on_last_page(test, mode):
    test.start_server(get_app(mode))

    target = test.table("table")

    target.paging.last.click()

    assert target.paging.current.get_value() == str(pages)
    assert target.paging.first.exists()
    assert target.paging.previous.exists()
    assert not target.paging.next.exists()
    assert not target.paging.last.exists()
    assert test.get_log_errors() == []


def test_tpag004_ops_input_with_enter(test):
    test.start_server(get_app("native"))

    target = test.table("table")

    text00 = target.cell(0, 0).get_text()

    assert target.paging.current.get_value() == "1"

    target.paging.current.click()
    test.send_keys("100" + Keys.ENTER)

    assert target.paging.current.get_value() == "100"
    assert target.cell(0, 0).get_text() != text00
    assert test.get_log_errors() == []


def test_tpag005_ops_input_with_unfocus(test):
    test.start_server(get_app("native"))

    target = test.table("table")

    text00 = target.cell(0, 0).get_text()

    assert target.paging.current.get_value() == "1"

    target.paging.current.click()
    test.send_keys("100")
    target.cell(0, 0).click()

    assert target.paging.current.get_value() == "100"
    assert target.cell(0, 0).get_text() != text00
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "value,expected_value", [(0, 1), (-1, 1), ("a", 1), (pages * 2, pages)]
)
def test_tpag006_ops_input_invalid_with_enter(test, value, expected_value):
    test.start_server(get_app("native"))

    target = test.table("table")

    assert target.paging.current.get_value() == "1"

    target.paging.current.click()
    test.send_keys(str(value) + Keys.ENTER)

    assert target.paging.current.get_value() == str(expected_value)
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "value,expected_value", [(0, 1), (-1, 1), ("a", 1), (pages * 2, pages)]
)
def test_tpag007_ops_input_invalid_with_unfocus(test, value, expected_value):
    test.start_server(get_app("native"))

    target = test.table("table")

    assert target.paging.current.get_value() == "1"

    target.paging.current.click()
    test.send_keys(str(value))
    target.cell(0, 0).click()

    assert target.paging.current.get_value() == str(expected_value)
    assert test.get_log_errors() == []


@pytest.mark.parametrize("mode", ["custom", "native"])
def test_tpag008_hide_with_single_page(test, mode):
    test.start_server(get_app(mode=mode, data=df[0:PAGE_SIZE]))

    target = test.table("table")

    assert not target.paging.exists()
    assert test.get_log_errors() == []


def test_tpag009_hide_with_invalid_page_count(test):
    test.start_server(get_app(mode="custom", page_count=-1))

    target = test.table("table")

    assert not target.paging.exists()
    assert test.get_log_errors() == []


def test_tpag010_limits_page(test):
    test.start_server(get_app(mode="custom", page_count=10))

    target = test.table("table")

    target.paging.last.click()

    assert target.paging.current.get_value() == "10"
    assert test.get_log_errors() == []


def get_app2():
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("i=20", id="button", n_clicks=0),
            DataTable(
                id="table",
                page_size=5,
                columns=[{"name": "i", "id": "i"}, {"name": "square", "id": "square"}],
                data=[{"i": i, "square": i**2} for i in range(50 + 1)],
                page_current=5,
            ),
            dcc.Graph(),
        ]
    )

    @app.callback(Output("table", "data"), Input("button", "n_clicks"))
    def update_table_data(n):
        return (
            [{"i": i, "square": i**2} for i in range(20 + 1)]
            if n > 0
            else dash.no_update
        )

    return app


def test_tpag011_valid_page(test):
    test.start_server(get_app2())

    test.find_element(".js-plotly-plot")

    target = test.table("table")
    test.find_element("#button").click()

    assert target.paging.current.get_value() == "1"
    assert test.get_log_errors() == []

    test.table("table").is_ready()
    test.percy_snapshot("test_tpag011 Pagination row visible")
