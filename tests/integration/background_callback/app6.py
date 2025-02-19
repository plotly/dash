from dash import Dash, Input, Output, State, dcc, html

import time
from multiprocessing import Value

from tests.integration.background_callback.utils import get_background_callback_manager

background_callback_manager = get_background_callback_manager()
handle = background_callback_manager.handle

app = Dash(__name__, background_callback_manager=background_callback_manager)
app._cache_key = Value("i", 0)


# Control return value of cache_by function using multiprocessing value
def cache_fn():
    return app._cache_key.value


background_callback_manager.cache_by = [cache_fn]


app.layout = html.Div(
    [
        dcc.Input(id="input1", value="AAA"),
        html.Button(id="run-button1", children="Run"),
        html.Div(id="status1", children="Finished"),
        html.Div(id="result1", children="No results"),
        html.Hr(),
        dcc.Input(id="input2", value="aaa"),
        html.Button(id="run-button2", children="Run"),
        html.Div(id="status2", children="Finished"),
        html.Div(id="result2", children="No results"),
    ]
)


@app.callback(
    Output("result1", "children"),
    [Input("run-button1", "n_clicks"), State("input1", "value")],
    progress=Output("status1", "children"),
    progress_default="Finished",
    interval=500,
    cache_args_to_ignore=[0],
    background=True,
)
def update_output1(set_progress, _n_clicks, value):
    for i in range(4):
        set_progress(f"Progress {i}/4")
        time.sleep(2)
    return f"Result for '{value}'"


@app.callback(
    Output("result2", "children"),
    dict(button=Input("run-button2", "n_clicks"), value=State("input2", "value")),
    progress=Output("status2", "children"),
    progress_default="Finished",
    interval=500,
    cache_args_to_ignore=["button"],
    prevent_initial_call=True,
    background=True,
)
def update_output2(set_progress, button, value):
    for i in range(4):
        set_progress(f"Progress {i}/4")
        time.sleep(2)
    return f"Result for '{value}'"


if __name__ == "__main__":
    app.run(debug=True)
