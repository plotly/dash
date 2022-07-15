from dash import Dash
from dash.dcc import Dropdown
from dash.html import Div
from dash.dash_table import DataTable

import pytest


@pytest.mark.DCC788
def test_ddvi001_fixed_table(dash_duo):
    app = Dash(__name__)
    app.layout = Div(
        [
            Dropdown(
                id="dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                value="NYC",
            ),
            DataTable(
                id="table",
                columns=[
                    {"name": x, "id": x, "selectable": True} for x in ["a", "b", "c"]
                ],
                editable=True,
                row_deletable=True,
                fixed_rows=dict(headers=True),
                fixed_columns=dict(headers=True),
                data=[
                    {"a": "a" + str(x), "b": "b" + str(x), "c": "c" + str(x)}
                    for x in range(0, 20)
                ],
            ),
        ]
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#dropdown").click()
    dash_duo.wait_for_element("#dropdown .Select-menu-outer")

    dash_duo.percy_snapshot("dcc.Dropdown dropdown overlaps table fixed rows/columns")

    assert dash_duo.get_logs() == []


def test_ddvi002_maxHeight(dash_duo):
    app = Dash(__name__)
    app.layout = Div(
        [Dropdown([str(i) for i in range(100)], "1", id="dropdown", maxHeight=800)]
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#dropdown").click()
    dash_duo.wait_for_element("#dropdown .Select-menu-outer")

    dash_duo.percy_snapshot("dcc.Dropdown dropdown menu maxHeight 800px")

    assert dash_duo.get_logs() == []
