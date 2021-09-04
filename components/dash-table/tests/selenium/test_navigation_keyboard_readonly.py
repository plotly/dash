import dash

from utils import get_props

from dash.dash_table import DataTable

from selenium.webdriver.common.keys import Keys

import pytest


def get_app(editable):
    app = dash.Dash(__name__)

    baseProps = get_props()
    baseProps.update(dict(editable=editable))

    if editable:
        for c in baseProps["columns"]:
            c["editable"] = not c["id"] in ["bbb", "eee", "fff"]

    app.layout = DataTable(**baseProps)

    return app


@pytest.mark.parametrize("editable", [False, True])
@pytest.mark.parametrize(
    "name,start_id,end_id",
    [
        ["in and out of dropdown cell", "ggg", "bbb"],
        ["in and out of label cell", "eee", "fff"],
    ],
)
def test_kron001_navigate_into(test, editable, name, start_id, end_id):
    test.start_server(get_app(editable))

    target = test.table("table")

    target.cell(2, start_id).click()

    for i in range(2):
        test.send_keys(Keys.ARROW_RIGHT)
        assert target.cell(2, end_id).is_focused()

        test.send_keys(Keys.ARROW_LEFT)
        assert target.cell(2, start_id).is_focused()
        assert not target.cell(2, end_id).is_focused()

        assert test.get_log_errors() == []
