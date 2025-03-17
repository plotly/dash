from dash import Dash, Input, Output, dcc, html
import time

from tests.integration.background_callback.utils import get_background_callback_manager

background_callback_manager = get_background_callback_manager()
handle = background_callback_manager.handle

app = Dash(__name__)
app.layout = html.Div(
    [
        dcc.Input(id="input", value="initial value"),
        html.Div(html.Div([1.5, None, "string", html.Div(id="output-1")])),
    ]
)


@app.callback(
    Output("output-1", "children"),
    [Input("input", "value")],
    interval=500,
    manager=background_callback_manager,
    background=True,
)
def update_output(value):
    time.sleep(0.1)
    return value


if __name__ == "__main__":
    app.run(debug=True)
