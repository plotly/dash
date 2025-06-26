import time

import dash
from dash import html, no_update
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from tests.background_callback.utils import get_background_callback_manager

background_callback_manager = get_background_callback_manager()
handle = background_callback_manager.handle

app = dash.Dash(__name__, background_callback_manager=background_callback_manager)
app.enable_dev_tools(debug=True, dev_tools_ui=True)
app.layout = html.Div(
    [
        html.Div([html.P(id="output", children=["Button not clicked"])]),
        html.Button(id="button", children="Run Job!"),
        html.Div(id="output-status"),
        html.Div(id="output1"),
        html.Div(id="output2"),
        html.Div(id="output3"),
        html.Button("multi-output", id="multi-output"),
    ]
)
app.test_lock = lock = background_callback_manager.test_lock


@app.callback(
    output=Output("output", "children"),
    inputs=Input("button", "n_clicks"),
    running=[
        (Output("button", "disabled"), True, False),
    ],
    prevent_initial_call=True,
    background=True,
)
def callback(n_clicks):
    time.sleep(1)
    if n_clicks == 2:
        raise Exception("bad error")

    if n_clicks == 4:
        raise PreventUpdate
    return f"Clicked {n_clicks} times"


@app.callback(
    output=[Output("output-status", "children")]
    + [Output(f"output{i}", "children") for i in range(1, 4)],
    inputs=[Input("multi-output", "n_clicks")],
    running=[
        (Output("multi-output", "disabled"), True, False),
    ],
    prevent_initial_call=True,
    background=True,
)
def long_multi(n_clicks):
    time.sleep(1)
    return (
        [f"Updated: {n_clicks}"]
        + [i for i in range(1, n_clicks + 1)]
        + [no_update for _ in range(n_clicks + 1, 4)]
    )


if __name__ == "__main__":
    app.run(debug=True)
