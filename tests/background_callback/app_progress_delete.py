from dash import Dash, Input, Output, State, html, clientside_callback
import time

from tests.background_callback.utils import get_background_callback_manager

background_callback_manager = get_background_callback_manager()
handle = background_callback_manager.handle

app = Dash(__name__, background_callback_manager=background_callback_manager)

app.layout = html.Div(
    [
        html.Button("Start", id="start"),
        html.Div(id="output"),
        html.Div(id="progress-output"),
        html.Div(0, id="progress-counter"),
    ]
)

clientside_callback(
    "function(_, previous) { return parseInt(previous) + 1;}",
    Output("progress-counter", "children"),
    Input("progress-output", "children"),
    State("progress-counter", "children"),
    prevent_initial_call=True,
)


@app.callback(
    Output("output", "children"),
    Input("start", "n_clicks"),
    progress=Output("progress-output", "children"),
    interval=200,
    background=True,
    prevent_initial_call=True,
)
def on_bg_progress(set_progress, _):
    set_progress("start")
    time.sleep(2)
    set_progress("stop")
    return "done"


if __name__ == "__main__":
    app.run(debug=True)
