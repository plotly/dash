import os
import time

import dash
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from tests.integration.long_callback.utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle

app = dash.Dash(__name__, long_callback_manager=long_callback_manager)
app.enable_dev_tools(debug=True, dev_tools_ui=True)
app.layout = html.Div(
    [
        html.Div([html.P(id="output", children=["Button not clicked"])]),
        html.Button(id="button", children="Run Job!"),
    ]
)


@app.long_callback(
    output=Output("output", "children"),
    inputs=Input("button", "n_clicks"),
    running=[
        (Output("button", "disabled"), True, False),
    ],
    prevent_initial_call=True,
)
def callback(n_clicks):
    if os.getenv("LONG_CALLBACK_MANAGER") != "celery":
        # Diskmanager needs some time, celery takes too long.
        time.sleep(1)
    if n_clicks == 2:
        raise Exception("bad error")

    if n_clicks == 4:
        raise PreventUpdate
    return f"Clicked {n_clicks} times"


if __name__ == "__main__":
    app.run_server(debug=True)
