import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from dash.dash_table import DataTable
from dash.html import Button, Div


def get_app():
    app = dash.Dash(__name__)

    columns = [{"name": i, "id": i} for i in ["a", "b"]]
    data = [dict(a=1, b=2), dict(a=11, b=22)]

    app.layout = Div(
        [
            Button(id="clear-table", children=["Clear table"]),
            DataTable(id="table", columns=columns, data=data),
        ]
    )

    @app.callback(
        [Output("table", "data"), Output("table", "columns")],
        [Input("clear-table", "n_clicks")],
    )
    def clear_table(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        nonlocal columns, data

        return (data, columns) if n_clicks % 2 == 0 else (None, None)

    return app


def test_empt001_clear_(test):
    test.start_server(get_app())

    target = test.table("table")

    assert target.is_ready()
    assert len(test.find_elements("tr")) == 3
    test.find_element("#clear-table").click()
    assert target.is_ready()
    assert len(test.find_elements("tr")) == 0
    assert test.get_log_errors() == []
