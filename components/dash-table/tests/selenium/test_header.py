import dash
from dash.testing import wait

from utils import get_props

from dash.dash_table import DataTable

import pytest


def get_app(props=dict()):
    app = dash.Dash(__name__)

    baseProps = get_props()
    baseProps.update(
        dict(columns=[dict(c, hideable="last") for c in baseProps["columns"]])
    )

    baseProps.update(props)

    app.layout = DataTable(**baseProps)

    return app


def get_sigle_row_app(props=dict()):
    app = dash.Dash(__name__)

    baseProps = get_props()
    baseProps.update(
        dict(
            columns=[dict(c, hideable=True, name=c["id"]) for c in baseProps["columns"]]
        )
    )

    baseProps.update(props)

    app.layout = DataTable(**baseProps)

    return app


@pytest.mark.parametrize("row", [0, 1, 2])
def test_head001_renames_only_row(test, row):
    test.start_server(get_app())

    target = test.table("table")

    title = [
        target.column("rows").get_text(0),
        target.column("rows").get_text(1),
        target.column("rows").get_text(2),
    ]

    target.column("rows").edit(row)

    alert = test.driver.switch_to.alert
    alert.send_keys("modified")
    alert.accept()

    for i in range(3):
        wait.until(
            lambda: target.column("rows").get_text(i) == "modified"
            if row == i
            else title[i],
            3,
        )

    assert test.get_log_errors() == []


def test_head002_preserves_hidden_columns_on_rename(test):
    test.start_server(get_app(dict(merge_duplicate_headers=True)))

    target = test.table("table")

    wait.until(lambda: target.column(6).get().get_attribute("colspan") == "4", 3)
    assert target.column(6).get_text() == ""

    target.column(8).hide(2)
    target.column(6).hide(2)
    target.column(1).hide(2)

    target.column(5).edit()

    alert = test.driver.switch_to.alert
    alert.send_keys("Chill")
    alert.accept()

    target.toggle_columns().open()
    for el in target.toggle_columns().get_hidden():
        el.click()

    target.toggle_columns().close()

    wait.until(lambda: target.column(6).get().get_attribute("colspan") == "4", 3)

    assert target.column(6).get_text() == "Chill"
    assert test.get_log_errors() == []


def test_head003_preserves_column_name_on_cancel(test):
    test.start_server(get_app())

    target = test.table("table")

    target.column("rows").edit(0)

    alert = test.driver.switch_to.alert
    alert.send_keys("Chill")
    alert.dismiss()

    assert target.column("rows").get_text(0) == "rows"
    assert test.get_log_errors() == []


def test_head004_change_single_row_header(test):
    test.start_server(get_sigle_row_app())

    target = test.table("table")

    target.column("rows").edit(0)

    alert = test.driver.switch_to.alert
    alert.send_keys("Chill")
    alert.accept()

    assert target.column("rows").get_text(0) == "Chill"
    assert test.get_log_errors() == []
