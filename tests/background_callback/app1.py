import os

from dash import Dash, Input, Output, dcc, html
import time

from tests.background_callback.utils import get_background_callback_manager


os.environ["LONG_CALLBACK_MANAGER"] = "celery"
os.environ["REDIS_URL"] = "redis://localhost:6379"
redis_url = os.environ["REDIS_URL"].rstrip("/")
os.environ["CELERY_BROKER"] = f"{redis_url}/0"
os.environ["CELERY_BACKEND"] = f"{redis_url}/1"

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
