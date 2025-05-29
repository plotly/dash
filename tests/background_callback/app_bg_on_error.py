from dash import Dash, Input, Output, html, set_props
from tests.background_callback.utils import get_background_callback_manager

background_callback_manager = get_background_callback_manager()
handle = background_callback_manager.handle


def global_error_handler(err):
    set_props("global-output", {"children": f"global: {err}"})


app = Dash(
    __name__,
    background_callback_manager=background_callback_manager,
    on_error=global_error_handler,
)

app.layout = [
    html.Button("callback on_error", id="start-cb-onerror"),
    html.Div(id="cb-output"),
    html.Button("global on_error", id="start-global-onerror"),
    html.Div(id="global-output"),
]


def callback_on_error(err):
    set_props("cb-output", {"children": f"callback: {err}"})


@app.callback(
    Output("cb-output", "children"),
    Input("start-cb-onerror", "n_clicks"),
    prevent_initial_call=True,
    background=True,
    on_error=callback_on_error,
)
def on_click(_):
    raise Exception("callback error")


@app.callback(
    Output("global-output", "children"),
    Input("start-global-onerror", "n_clicks"),
    prevent_initial_call=True,
    background=True,
)
def on_click_global(_):
    raise Exception("global error")


if __name__ == "__main__":
    app.run(debug=True)
