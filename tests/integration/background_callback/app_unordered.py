from dash import Dash, Input, Output, dcc, State, html, callback

from tests.integration.background_callback.utils import get_background_callback_manager

background_callback_manager = get_background_callback_manager()
handle = background_callback_manager.handle

app = Dash(__name__, background_callback_manager=background_callback_manager)

app.layout = html.Div(
    [
        html.Div(id="output"),
        html.Button("click", id="click"),
        dcc.Store(data="stored", id="stored"),
    ]
)


@callback(
    Output("output", "children"),
    State("stored", "data"),
    Input("click", "n_clicks"),
    background=True,
    prevent_initial_call=True,
)
def update_output(stored, n_clicks):
    return stored


if __name__ == "__main__":
    app.run(debug=True)
