import dash
from dash.dependencies import Input, State, Output
import dash_html_components as html
import dash_core_components as dcc
import time
from multiprocessing import Value

from utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle


app = dash.Dash(__name__, long_callback_manager=long_callback_manager)
app._cache_key = Value("i", 0)


# Control return value of cache_by function using multiprocessing value
def cache_fn():
    return app._cache_key.value


long_callback_manager.cache_by = [cache_fn]


app.layout = html.Div(
    [
        dcc.Input(id="input", value="AAA"),
        html.Button(id="run-button", children="Run"),
        html.Div(id="status", children="Finished"),
        html.Div(id="result", children="No results"),
    ]
)


@app.long_callback(
    Output("result", "children"),
    [Input("run-button", "n_clicks"), State("input", "value")],
    progress=Output("status", "children"),
    progress_default="Finished",
    interval=500,
    cache_args_to_ignore=0,
)
def update_output(set_progress, _n_clicks, value):
    for i in range(4):
        set_progress(f"Progress {i}/4")
        time.sleep(2)
    return f"Result for '{value}'"


if __name__ == "__main__":
    app.run_server(debug=True)
