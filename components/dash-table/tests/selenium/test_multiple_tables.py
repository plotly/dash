import dash
from dash.testing import wait

from dash.dash_table import DataTable
from dash.html import Div

from selenium.webdriver.common.keys import Keys

import pandas as pd

url = "https://github.com/plotly/datasets/raw/master/" "26k-consumer-complaints.csv"
rawDf = pd.read_csv(url, nrows=100)
df = rawDf.to_dict("records")


def get_app(props=dict()):
    app = dash.Dash(__name__)

    baseProps = dict(
        columns=[dict(name=i, id=i, selectable=True) for i in rawDf.columns],
        data=df,
        editable=True,
        filter_action="native",
        fixed_columns={"headers": True},
        fixed_rows={"headers": True},
        page_action="native",
        row_deletable=True,
        row_selectable=True,
        sort_action="native",
    )

    baseProps.update(props)

    app.layout = Div([DataTable(**baseProps), DataTable(**baseProps)])

    return app


def test_tbmu001_select_row(test):
    test.start_server(get_app())

    wait.until(lambda: len(test.get_table_ids()) == 2, 3)
    ids = test.get_table_ids()

    table1 = test.table(ids[0])
    table2 = test.table(ids[1])

    table2.row(1).select()
    wait.until(lambda: table2.row(1).is_selected(), 3)

    table1.row(0).select()
    wait.until(lambda: table1.row(0).is_selected(), 3)
    wait.until(lambda: table2.row(1).is_selected(), 3)

    assert test.get_log_errors() == []


def test_tbmu002_select_column(test):
    test.start_server(get_app(dict(column_selectable="single")))

    wait.until(lambda: len(test.get_table_ids()) == 2, 3)
    ids = test.get_table_ids()

    table1 = test.table(ids[0])
    table2 = test.table(ids[1])

    table1.column("Complaint ID").select()
    table2.column("Product").select()

    assert table1.column("Complaint ID").is_selected()
    assert table2.column("Product").is_selected()


def test_tbmu003_edit_on_enter(test):
    test.start_server(get_app())

    wait.until(lambda: len(test.get_table_ids()) == 2, 3)
    ids = test.get_table_ids()

    table1 = test.table(ids[0])
    table2 = test.table(ids[1])

    initial_text = table2.cell(0, 0).get_text()

    table1.cell(0, 0).click()
    test.send_keys("abc" + Keys.ENTER)

    assert table1.cell(0, 0).get_text() == "abc"
    assert table2.cell(0, 0).get_text() == initial_text


def test_tbmu004_edit_click_outside(test):
    test.start_server(get_app())

    wait.until(lambda: len(test.get_table_ids()) == 2, 3)
    ids = test.get_table_ids()

    table1 = test.table(ids[0])
    table2 = test.table(ids[1])

    initial_text = table2.cell(0, 0).get_text()

    table1.cell(0, 0).click()
    test.send_keys("abc")
    table1.cell(1, 0).click()

    assert table1.cell(0, 0).get_text() == "abc"
    assert table2.cell(0, 0).get_text() == initial_text
