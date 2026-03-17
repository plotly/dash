import dash
from dash.dependencies import Input, Output
from dash import html
from dash.dash_table import DataTable

import json
import time
import pandas as pd

url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
rawDf = pd.read_csv(url, nrows=100)
rawDf["id"] = rawDf.index + 3000
df = rawDf.to_dict("records")


def get_app():
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            DataTable(
                id="table",
                columns=[{"name": i, "id": i} for i in rawDf.columns],
                data=df,
                row_selectable=True,
                selected_rows=[],
                filter_action="custom",
                filter_query="",
                sort_action="custom",
                sort_by=[],
                page_action="custom",
                page_current=0,
                page_size=10,
                style_cell=dict(width=100, min_width=100, max_width=100),
            ),
            html.Button("Set selected + sort_by", id="sort"),
            html.Button("Set selected + filter", id="filter"),
            html.Button("Set selected + page", id="page"),
            html.Div(id="selected_rows_output"),
        ]
    )

    @app.callback(
        Output("selected_rows_output", "children"),
        Input("table", "selected_rows"),
    )
    def show_selected_rows(selected_rows):
        return json.dumps(selected_rows) if selected_rows is not None else "None"

    @app.callback(
        Output("table", "selected_rows"),
        Output("table", "sort_by"),
        Input("sort", "n_clicks"),
        prevent_initial_call=True,
    )
    def set_selected_and_sort(_):
        return [0, 1, 2], [{"column_id": rawDf.columns[0], "direction": "asc"}]

    @app.callback(
        Output("table", "selected_rows", allow_duplicate=True),
        Output("table", "filter_query"),
        Input("filter", "n_clicks"),
        prevent_initial_call=True,
    )
    def set_selected_and_filter(_):
        return [0, 1, 2], "{} > 1".format(rawDf.columns[0])

    @app.callback(
        Output("table", "selected_rows", allow_duplicate=True),
        Output("table", "page_current"),
        Input("page", "n_clicks"),
        prevent_initial_call=True,
    )
    def set_selected_and_page(_):
        return [0, 1, 2], 1

    return app


def test_tsrc001_selected_rows_persists_with_sort_by(test):
    test.start_server(get_app())

    test.find_element("#sort").click()
    time.sleep(1)

    assert test.find_element("#selected_rows_output").text == json.dumps([0, 1, 2])
    assert test.get_log_errors() == []


def test_tsrc002_selected_rows_persists_with_filter_query(test):
    test.start_server(get_app())

    test.find_element("#filter").click()
    time.sleep(1)

    assert test.find_element("#selected_rows_output").text == json.dumps([0, 1, 2])
    assert test.get_log_errors() == []


def test_tsrc003_selected_rows_persists_with_page_current(test):
    test.start_server(get_app())

    test.find_element("#page").click()
    time.sleep(1)

    assert test.find_element("#selected_rows_output").text == json.dumps([0, 1, 2])
    assert test.get_log_errors() == []
