from dash import Dash, Input, Output, dcc, html, page_container, register_page

import time

from tests.integration.long_callback.utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle


app = Dash(
    __name__,
    use_pages=True,
    pages_folder="",
    long_callback_manager=long_callback_manager,
)

app.layout = html.Div(
    [
        dcc.Link("page1", "/"),
        dcc.Link("page2", "/2"),
        html.Button("Cancel", id="shared_cancel"),
        page_container,
    ]
)


register_page(
    "one",
    "/",
    layout=html.Div(
        [
            html.Button("start", id="start1"),
            html.Button("cancel1", id="cancel1"),
            html.Div("idle", id="progress1"),
            html.Div("initial", id="output1"),
            html.Div("no-cancel-btn", id="no-cancel-btn"),
            html.Div("no-cancel", id="no-cancel-output"),
        ]
    ),
)
register_page(
    "two",
    "/2",
    layout=html.Div(
        [
            html.Button("start2", id="start2"),
            html.Button("cancel2", id="cancel2"),
            html.Div("idle", id="progress2"),
            html.Div("initial", id="output2"),
        ]
    ),
)


@app.callback(
    Output("no-cancel-output", "children"),
    Input("no-cancel-btn", "n_clicks"),
    background=True,
    prevent_initial_call=True,
)
def on_click_no_cancel(_):
    return "Not Canceled"


@app.callback(
    Output("output1", "children"),
    Input("start1", "n_clicks"),
    running=[
        (Output("progress1", "children"), "running", "idle"),
    ],
    cancel=[
        Input("cancel1", "n_clicks"),
        Input("shared_cancel", "n_clicks"),
    ],
    background=True,
    prevent_initial_call=True,
    interval=300,
)
def on_click1(n_clicks):
    time.sleep(2)
    return f"Click {n_clicks}"


@app.callback(
    Output("output2", "children"),
    Input("start2", "n_clicks"),
    running=[
        (Output("progress2", "children"), "running", "idle"),
    ],
    cancel=[
        Input("cancel2", "n_clicks"),
        Input("shared_cancel", "n_clicks"),
    ],
    background=True,
    prevent_initial_call=True,
    interval=300,
)
def on_click1(n_clicks):
    time.sleep(2)
    return f"Click {n_clicks}"


if __name__ == "__main__":
    app.run(debug=True)
