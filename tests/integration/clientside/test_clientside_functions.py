from dash import Dash, html, Input, Output, no_update, State
import json
from multiprocessing import Value


def test_sp001_clientside_setprops(dash_duo):

    call_count = Value("i", 0)

    app = Dash(__name__)

    ids = [
        {"id": {"index": "1", "type": "test"}, "children": ["rawr"]},
        {"id": "two", "children": "this is a test"},
        {"id": "three", "children": "i see trees of green"},
    ]

    app.layout = html.Div(
        [
            *[html.Div(id=x["id"]) for x in ids],
            html.Div(id="four"),
            html.Button(id="setup", children="test setprops"),
        ]
    )

    app.clientside_callback(
        """
            () => {
                window.dash_clientside.setProps("""
        + json.dumps(ids)
        + """)
                return window.dash_clientside.no_update
            }
        """,
        Output("setup", "id"),
        Input("setup", "n_clicks"),
        prevent_initial_call=True,
    )


    for x in ids:

        @app.callback(
            Output(x["id"], "id", allow_duplicate=True),
            Output("four", "children", allow_duplicate=True),
            Input(x["id"], "children"),
            State(x["id"], "id"),
            prevent_initial_call=True,
        )
        def prinout(c, id):
            call_count.value += 1
            for y in ids:
                if y["id"] == id:
                    assert y["children"] == c
            return no_update, call_count.value

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#setup", "test setprops")
    dash_duo.find_element("#setup").click()
    dash_duo.wait_for_text_to_equal("#two", "this is a test")
    dash_duo.wait_for_text_to_equal("#three", "i see trees of green")
    dash_duo.wait_for_text_to_equal("#four", "3")
