from dash import Dash, Input, Output, State, dcc, html
import time

from tests.integration.long_callback.utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle

app = Dash(__name__)
app.layout = html.Div(
    [
        dcc.Input(id="input", value="initial value"),
        html.Button(id="run-button", children="Run"),
        html.Button(id="cancel-button", children="Cancel"),
        html.Div(id="status", children="Finished"),
        html.Div(id="result", children="No results"),
    ]
)


@app.long_callback(
    Output("result", "children"),
    [Input("run-button", "n_clicks"), State("input", "value")],
    running=[(Output("status", "children"), "Running", "Finished")],
    cancel=[Input("cancel-button", "n_clicks")],
    interval=500,
    manager=long_callback_manager,
    prevent_initial_call=True,
)
def update_output(n_clicks, value):
    time.sleep(2)
    return f"Processed '{value}'"


if __name__ == "__main__":
    app.run_server(debug=True)
