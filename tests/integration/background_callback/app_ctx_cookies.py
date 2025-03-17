from dash import Dash, Input, Output, html, callback, ctx

from tests.integration.background_callback.utils import get_background_callback_manager

background_callback_manager = get_background_callback_manager()
handle = background_callback_manager.handle

app = Dash(__name__, background_callback_manager=background_callback_manager)

app.layout = html.Div(
    [
        html.Button("set-cookies", id="set-cookies"),
        html.Button("use-cookies", id="use-cookies"),
        html.Div(id="intermediate"),
        html.Div("output", id="output"),
    ]
)
app.test_lock = lock = background_callback_manager.test_lock


@callback(
    Output("intermediate", "children"),
    Input("set-cookies", "n_clicks"),
    prevent_initial_call=True,
)
def set_cookies(_):
    ctx.response.set_cookie("bg-cookie", "cookie-value")
    return "ok"


@callback(
    Output("output", "children"),
    Input("use-cookies", "n_clicks"),
    prevent_initial_call=True,
    background=True,
)
def use_cookies(_):
    value = ctx.cookies.get("bg-cookie")
    return value


if __name__ == "__main__":
    app.run(debug=True)
