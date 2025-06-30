from dash import Dash, Input, Output, html, callback, set_props
import time

from tests.background_callback.utils import get_background_callback_manager

background_callback_manager = get_background_callback_manager()
handle = background_callback_manager.handle

app = Dash(__name__, background_callback_manager=background_callback_manager)
app.test_lock = lock = background_callback_manager.test_lock

app.layout = html.Div(
    [
        html.Button("start", id="start"),
        html.Div(id="secondary"),
        html.Div(id="no-output"),
        html.Div("initial", id="output"),
        html.Button("start-no-output", id="start-no-output"),
    ]
)


@callback(
    Output("output", "children"),
    Input("start", "n_clicks"),
    prevent_initial_call=True,
    background=True,
    interval=500,
)
def on_click(_):
    set_props("secondary", {"children": "first"})
    set_props("secondary", {"style": {"background": "red"}})
    time.sleep(2)
    set_props("secondary", {"children": "second"})
    return "completed"


@callback(
    Input("start-no-output", "n_clicks"),
    prevent_initial_call=True,
    background=True,
)
def on_click(_):
    set_props("no-output", {"children": "started"})
    time.sleep(2)
    set_props("no-output", {"children": "completed"})


if __name__ == "__main__":
    app.run(debug=True)
