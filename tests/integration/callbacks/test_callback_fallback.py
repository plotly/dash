from dash import *
from dash._utils import to_json
import traceback
from dash import ctx
from dash.exceptions import PreventUpdate
import json


def test_cbfb001_callback_fallback(dash_duo):
    def callback_fallback(output=None):
        error_message = "error in callback"

        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if str(e) == "":
                        raise PreventUpdate
                alertError(f"{error_message}", f"{output}\n {traceback.format_exc()}")
                resp = {
                    "app_notification": {
                        "children": json.loads(
                            to_json(
                                notification(
                                    "error",
                                    "there was an issue, IT has been notified",
                                    ctx,
                                )
                            )
                        )
                    }
                }
                return json.dumps({"multi": True, "response": resp})

            return wrapper

        return decorator

    def callback_fallback2(output=None):
        error_message = "error in callback"

        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if str(e) == "":
                        raise PreventUpdate
                alertError(f"{error_message}", f"{output}\n {traceback.format_exc()}")
                resp = {
                    "app_notification": {
                        "children": json.loads(
                            to_json(
                                notification(
                                    "error",
                                    "I'm sorry Dave, I'm afraid I can't do that",
                                    ctx,
                                )
                            )
                        )
                    }
                }
                return json.dumps({"multi": True, "response": resp})

            return wrapper

        return decorator

    app = Dash(
        __name__,
        callback_fallback=callback_fallback,
    )

    def notification(type, msg, ctx=None):
        if type == "error":
            return html.Div(
                children=msg + (f' - {ctx.triggered[0]["value"]}' if ctx else ""),
                style={"color": "red"},
            )
        return ""

    def alertError(subject, message):
        print(subject)
        print(message)
        pass

    @callback(
        Output("children", "children"),
        Input("click", "n_clicks"),
        State("testChecked", "value"),
        prevent_initial_call=True,
    )
    def partialFailingCall(n, c):
        if c:
            return rawr
        return f"I ran properly - {n}"

    @callback(
        Output("children2", "children"),
        Input("click2", "n_clicks"),
        State("testChecked2", "value"),
        callback_fallback=callback_fallback2,
        prevent_initial_call=True,
    )
    def partialFailingCall(n, c):
        if not c:
            return rawr
        return f"I ran properly - {n}"

    app.layout = html.Div(
        children=[
            html.Div(id="app_notification"),
            html.Div(
                [
                    html.Div("When checked, the callback will fail"),
                    html.Button("test callback", id="click"),
                    dcc.Checklist([True], id="testChecked"),
                    html.Div(id="children"),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        "When not checked, the callback will fail, callback handler is different"
                    ),
                    html.Button("test callback", id="click2"),
                    dcc.Checklist([True], id="testChecked2"),
                    html.Div(id="children2"),
                ]
            ),
        ]
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#click", "test callback")
    dash_duo.find_element("#click").click()
    dash_duo.wait_for_text_to_equal("#children", "I ran properly - 1")
    dash_duo.find_element("#testChecked input").click()
    dash_duo.find_element("#click").click()
    dash_duo.wait_for_text_to_equal(
        "#app_notification", "there was an issue, IT has been notified - 2"
    )
    dash_duo.wait_for_text_to_equal("#children", "I ran properly - 1")

    dash_duo.find_element("#click2").click()
    dash_duo.wait_for_text_to_equal(
        "#app_notification", "I'm sorry Dave, I'm afraid I can't do that - 1"
    )
    dash_duo.wait_for_text_to_equal("#children2", "")
    dash_duo.find_element("#testChecked2 input").click()
    dash_duo.find_element("#click2").click()
    dash_duo.wait_for_text_to_equal("#children2", "I ran properly - 2")
    dash_duo.wait_for_text_to_equal(
        "#app_notification", "I'm sorry Dave, I'm afraid I can't do that - 1"
    )
