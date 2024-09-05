import dash
from dash import Input, Output, html, dcc
from dash.exceptions import PreventUpdate

from dash.dash_table import DataTable

from multiprocessing import Lock
from selenium.webdriver.common.keys import Keys

import pandas as pd

url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
rawDf = pd.read_csv(url)
df = rawDf.to_dict("records")


def get_app_and_locks():
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="input"),
            html.Button(["Blocking"], id="blocking"),
            html.Button(["Non Blocking"], id="non-blocking"),
            DataTable(
                id="table",
                columns=[{"name": i, "id": i} for i in rawDf.columns],
                data=df,
                editable=True,
                filter_action="native",
                fixed_columns={"headers": True},
                fixed_rows={"headers": True},
                page_action="native",
                row_deletable=True,
                row_selectable=True,
                sort_action="native",
            ),
        ]
    )

    blocking_lock = Lock()
    non_blocking_lock = Lock()

    @app.callback(
        Output("table", "style_cell_conditional"), [Input("non-blocking", "n_clicks")]
    )
    def non_blocking_callback(clicks):
        if clicks is None:
            raise PreventUpdate

        with non_blocking_lock:
            return []

    @app.callback(Output("table", "data"), [Input("blocking", "n_clicks")])
    def blocking_callback(clicks):
        if clicks is None:
            raise PreventUpdate

        with blocking_lock:
            return df

    return app, blocking_lock, non_blocking_lock


def test_tedi001_loading_on_data_change(test):
    app, blocking, non_blocking = get_app_and_locks()

    test.start_server(app)

    target = test.table("table")

    with blocking:
        test.find_element("#blocking").click()
        target.is_loading()
        target.cell(0, 0).click()
        assert len(target.cell(0, 0).find_all_inside("input")) == 0

    target.is_ready()
    assert target.cell(0, 0).find_inside("input") is not None
    assert test.get_log_errors() == []


def test_tedi002_ready_on_non_data_change(test):
    app, blocking, non_blocking = get_app_and_locks()

    test.start_server(app)

    target = test.table("table")

    with blocking:
        test.find_element("#non-blocking").click()
        target.is_ready()
        target.cell(0, 0).click()
        assert target.cell(0, 0).find_inside("input") is not None

    target.is_ready()
    assert target.cell(0, 0).find_inside("input") is not None
    assert test.get_log_errors() == []


def test_tedi003_does_not_steal_focus(test):
    app, blocking, non_blocking = get_app_and_locks()

    test.start_server(app)

    target = test.table("table")

    with blocking:
        test.find_element("#blocking").click()
        test.find_element("#input").click()
        assert test.find_element("#input") == test.driver.switch_to.active_element

    target.is_ready()
    assert test.find_element("#input") == test.driver.switch_to.active_element
    assert test.get_log_errors() == []


def test_tedi004_edit_on_non_blocking(test):
    app, blocking, non_blocking = get_app_and_locks()

    test.start_server(app)

    target = test.table("table")

    with blocking:
        test.find_element("#non-blocking").click()
        target.cell(0, 0).click()
        test.send_keys("abc" + Keys.ENTER)
        assert target.cell(0, 0).get_text() == "abc"

    assert test.get_log_errors() == []


def test_tedi005_prevent_copy_paste_on_blocking(test):
    app, blocking, non_blocking = get_app_and_locks()

    test.start_server(app)

    target = test.table("table")

    with blocking:
        test.find_element("#blocking").click()
        target.cell(0, 0).click()
        with test.hold(Keys.SHIFT):
            test.send_keys(Keys.DOWN + Keys.RIGHT)

        test.copy()
        target.cell(2, 0).click()
        test.paste()

        for row in range(2):
            for col in range(2):
                assert (
                    target.cell(row + 2, col).get_text()
                    != target.cell(row, col).get_text()
                )

    assert test.get_log_errors() == []


def test_tedi006_allow_copy_paste_on_non_blocking(test):
    app, blocking, non_blocking = get_app_and_locks()

    test.start_server(app)

    target = test.table("table")

    with non_blocking:
        test.find_element("#non-blocking").click()
        target.cell(0, 0).click()
        with test.hold(Keys.SHIFT):
            test.send_keys(Keys.DOWN + Keys.RIGHT)

        test.copy()
        target.cell(2, 0).click()
        test.paste()

        for row in range(2):
            for col in range(2):
                assert (
                    target.cell(row + 2, col).get_text()
                    == target.cell(row, col).get_text()
                )

    assert test.get_log_errors() == []
