import dash
import dash.testing.wait as wait
from dash.dash_table import DataTable

import os
import pandas as pd
import pytest
from selenium.webdriver.common.keys import Keys

df = pd.read_csv(os.path.join(os.path.dirname(__file__), "assets/solar.csv"))

base_props = dict(
    id="table",
    columns=[{"name": i, "id": i} for i in df.columns],
    row_selectable="single",
    row_deletable=True,
    data=df.to_dict("records"),
    editable=True,
    fixed_rows={"headers": True, "data": 1},
    style_cell=dict(width=150),
    style_table=dict(width=500),
)


def get_margin(test):
    return test.driver.execute_script(
        "return parseFloat(getComputedStyle(document.querySelector('#table .cell-0-1')).marginLeft);"
    )


def get_scroll(test):
    return test.driver.execute_script(
        "return document.querySelector('#table .dt-table-container__row-1').scrollLeft;"
    )


def scroll_by(test, value):
    test.driver.execute_script(
        "document.querySelector('#table .dt-table-container__row-1').scrollBy({}, 0);".format(
            value
        )
    )


@pytest.mark.parametrize(
    "fixed_rows",
    [dict(fixed_rows=dict(headers=True)), dict(fixed_rows=dict(headers=True, data=1))],
)
@pytest.mark.parametrize(
    "fixed_columns",
    [
        dict(),
        dict(fixed_columns=dict(headers=True)),
        dict(fixed_columns=dict(headers=True, data=1)),
    ],
)
@pytest.mark.parametrize(
    "ops", [dict(), dict(row_selectable="single", row_deletable=True)]
)
def test_scrol001_fixed_alignment(test, fixed_rows, fixed_columns, ops):
    props = {**base_props, **fixed_rows, **fixed_columns, **ops}

    app = dash.Dash(__name__)
    app.layout = DataTable(**props)

    test.start_server(app)

    target = test.table("table")
    assert target.is_ready()

    fixed_width = test.driver.execute_script(
        "return parseFloat(getComputedStyle(document.querySelector('#table .cell-0-0')).width) || 0;"
    )

    assert -get_margin(test) == pytest.approx(fixed_width, abs=1)

    scroll_by(test, 200)

    wait.until(lambda: -get_margin(test) == pytest.approx(fixed_width + 200, abs=1), 3)

    scroll_by(test, -200)

    wait.until(lambda: -get_margin(test) == pytest.approx(fixed_width, abs=1), 3)
    assert test.get_log_errors() == []


@pytest.mark.parametrize(
    "fixed_rows",
    [dict(fixed_rows=dict(headers=True)), dict(fixed_rows=dict(headers=True, data=1))],
)
@pytest.mark.parametrize(
    "fixed_columns",
    [
        dict(),
        dict(fixed_columns=dict(headers=True)),
        dict(fixed_columns=dict(headers=True, data=1)),
    ],
)
@pytest.mark.parametrize(
    "ops", [dict(), dict(row_selectable="single", row_deletable=True)]
)
def test_scrol002_edit_navigate(test, fixed_rows, fixed_columns, ops):
    props = {**base_props, **fixed_rows, **fixed_columns, **ops}

    app = dash.Dash(__name__)
    app.layout = DataTable(**props)

    test.start_server(app)

    target = test.table("table")
    assert target.is_ready()

    fixed_width = test.driver.execute_script(
        "return parseFloat(getComputedStyle(document.querySelector('#table .cell-0-0')).width) || 0;"
    )

    scroll_by(test, 200)

    # alignment is ok after editing a cell
    target.cell(0, 3).click()
    test.send_keys("abc" + Keys.ENTER)

    wait.until(lambda: target.cell(1, 3).is_selected(), 3)
    wait.until(
        lambda: -get_margin(test)
        == pytest.approx(fixed_width + get_scroll(test), abs=1),
        3,
    )

    # alignment is ok after navigating
    test.send_keys(Keys.ARROW_DOWN)
    test.send_keys(Keys.ARROW_RIGHT)

    wait.until(lambda: target.cell(2, 4).is_selected(), 3)
    wait.until(
        lambda: -get_margin(test)
        == pytest.approx(fixed_width + get_scroll(test), abs=1),
        3,
    )
    assert test.get_log_errors() == []
