import dash
import dash.testing.wait as wait
from dash_table import DataTable

import pandas as pd
import pytest

df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/solar.csv")


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
    base_props = dict(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        row_selectable="single",
        row_deletable=True,
        data=df.to_dict("records"),
        fixed_rows={"headers": True, "data": 1},
        style_cell=dict(width=150),
        style_table=dict(width=500),
    )

    props = {**base_props, **fixed_rows, **fixed_columns, **ops}

    app = dash.Dash(__name__)
    app.layout = DataTable(**props)

    test.start_server(app)

    target = test.table("table")
    assert target.is_ready()

    fixed_width = test.driver.execute_script(
        "return parseFloat(getComputedStyle(document.querySelector('#table .cell-0-0')).width) || 0;"
    )
    margin_left = test.driver.execute_script(
        "return parseFloat(getComputedStyle(document.querySelector('#table .cell-0-1')).marginLeft);"
    )

    assert -margin_left == fixed_width

    test.driver.execute_script(
        "document.querySelector('#table .row-1').scrollBy(200, 0);"
    )

    wait.until(
        lambda: -test.driver.execute_script(
            "return parseFloat(getComputedStyle(document.querySelector('#table .cell-0-1')).marginLeft);"
        )
        == fixed_width + 200,
        3,
    )

    test.driver.execute_script(
        "document.querySelector('#table .row-1').scrollBy(-200, 0);"
    )

    wait.until(
        lambda: -test.driver.execute_script(
            "return parseFloat(getComputedStyle(document.querySelector('#table .cell-0-1')).marginLeft);"
        )
        == fixed_width,
        3,
    )
