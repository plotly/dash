import dash
from dash.dependencies import Input, State, Output
import dash_html_components as html
import dash_core_components as dcc
import time

from utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle


app = dash.Dash(__name__, long_callback_manager=long_callback_manager)
app.layout = html.Div(
    [
        dcc.Input(id="input", value="hello, world"),
        html.Button(id="run-button", children="Run"),
        html.Button(id="cancel-button", children="Cancel"),
        html.Div(id="status", children="Finished"),
        html.Div(id="result", children="No results"),
    ]
)


@app.long_callback(
    Output("result", "children"),
    [Input("run-button", "n_clicks"), State("input", "value")],
    progress=Output("status", "children"),
    progress_default="Finished",
    cancel=[Input("cancel-button", "n_clicks")],
    interval=500,
)
def update_output(set_progress, n_clicks, value):
    for i in range(4):
        set_progress(f"Progress {i}/4")
        time.sleep(1)
    return f"Processed '{value}'"


if __name__ == "__main__":
    app.run_server(debug=True)
