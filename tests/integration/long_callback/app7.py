from dash import Dash, Input, Output, State, dcc, html

import time

from tests.integration.long_callback.utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle


app = Dash(__name__, long_callback_manager=long_callback_manager)
app.layout = html.Div(
    [
        html.Button(id="show-layout-button", children="Show"),
        html.Div(id="dynamic-layout"),
    ]
)

app.validation_layout = html.Div(
    [
        html.Button(id="show-layout-button", children="Show"),
        html.Div(id="dynamic-layout"),
        dcc.Input(id="input", value="hello, world"),
        html.Button(id="run-button", children="Run"),
        html.Button(id="cancel-button", children="Cancel"),
        html.Div(id="status", children="Finished"),
        html.Div(id="result", children="No results"),
    ]
)


@app.callback(
    Output("dynamic-layout", "children"), Input("show-layout-button", "n_clicks")
)
def make_layout(n_clicks):
    if n_clicks is not None:
        return html.Div(
            [
                dcc.Input(id="input", value="hello, world"),
                html.Button(id="run-button", children="Run"),
                html.Button(id="cancel-button", children="Cancel"),
                html.Div(id="status", children="Finished"),
                html.Div(id="result", children="No results"),
            ]
        )
    else:
        return []


@app.long_callback(
    Output("result", "children"),
    [Input("run-button", "n_clicks"), State("input", "value")],
    progress=Output("status", "children"),
    progress_default="Finished",
    cancel=[Input("cancel-button", "n_clicks")],
    interval=500,
    prevent_initial_call=True,
)
def update_output(set_progress, n_clicks, value):
    for i in range(4):
        set_progress(f"Progress {i}/4")
        time.sleep(1)
    return f"Processed '{value}'"


if __name__ == "__main__":
    app.run_server(debug=True)
