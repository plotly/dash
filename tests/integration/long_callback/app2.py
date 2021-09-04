from dash import Dash, Input, Output, html

import time

from tests.integration.long_callback.utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle

app = Dash(__name__, long_callback_manager=long_callback_manager)
app.layout = html.Div(
    [
        html.Button(id="button-1", children="Click Here", n_clicks=0),
        html.Div(id="status", children="Finished"),
        html.Div(id="result", children="Not clicked"),
    ]
)


@app.long_callback(
    Output("result", "children"),
    [Input("button-1", "n_clicks")],
    running=[(Output("status", "children"), "Running", "Finished")],
    interval=500,
    prevent_initial_call=True,
)
def update_output(n_clicks):
    time.sleep(2)
    return f"Clicked {n_clicks} time(s)"


if __name__ == "__main__":
    app.run_server(debug=True)
