from dash import Dash, Input, Output, html

from tests.integration.long_callback.utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle

app = Dash(__name__, long_callback_manager=long_callback_manager)

app.layout = html.Div(
    [
        html.Button("click 1", id="button-1"),
        html.Button("click 2", id="button-2"),
        html.Div(id="output-1"),
        html.Div(id="output-2"),
    ]
)


def gen_callback(index):
    @app.callback(
        Output(f"output-{index}", "children"),
        Input(f"button-{index}", "n_clicks"),
        background=True,
        prevent_initial_call=True,
    )
    def callback_name(_):
        return f"Clicked on {index}"


for i in range(1, 3):
    gen_callback(i)


if __name__ == "__main__":
    app.run_server(debug=True)
