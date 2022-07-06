import json

from dash import Dash, Input, Output, html, callback, ALL, ctx

from tests.integration.long_callback.utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle

app = Dash(__name__, long_callback_manager=long_callback_manager)

app.layout = html.Div(
    [
        html.Button(id={"type": "run-button", "index": 0}, children="Run 1"),
        html.Button(id={"type": "run-button", "index": 1}, children="Run 2"),
        html.Button(id={"type": "run-button", "index": 2}, children="Run 3"),
        html.Div(id="result", children="No results"),
        html.Div(id="running"),
    ]
)
app.test_lock = lock = long_callback_manager.test_lock


@callback(
    Output("result", "children"),
    [Input({"type": "run-button", "index": ALL}, "n_clicks")],
    background=True,
    prevent_initial_call=True,
    running=[(Output("running", "children"), "on", "off")],
)
def update_output(n_clicks):
    triggered = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    return json.dumps(dict(triggered=triggered, value=n_clicks[triggered["index"]]))


if __name__ == "__main__":
    app.run_server(debug=True)
