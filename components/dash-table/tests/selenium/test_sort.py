import dash

from utils import basic_modes, get_props

from dash.dash_table import DataTable

import pytest


def get_app(props=dict()):
    app = dash.Dash(__name__)

    baseProps = get_props()

    baseProps.update(dict(sort_action="native"))
    baseProps.update(props)

    app.layout = DataTable(**baseProps)

    return app


@pytest.mark.parametrize("props", basic_modes)
def test_sort001_can_sort(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.cell(0, "bbb-readonly").get_text() == "label Wet"
    target.cell(1, "bbb-readonly").get_text() == "label Snowy"
    target.cell(2, "bbb-readonly").get_text() == "label Tropical Beaches"
    target.cell(3, "bbb-readonly").get_text() == "label Humid"

    target.column("bbb-readonly").sort(2)

    for i in range(4):
        target.cell(i, "bbb-readonly").get_text() == "label Humid"

    assert test.get_log_errors() == []
