from multiprocessing import Value

from dash.testing import wait
from dash import Dash, Input, Output, State, dcc, html, callback_context
import pytest
import time


@pytest.mark.parametrize(
    "confirms", [[False, False], [False, True], [True, False], [True, True]]
)
@pytest.mark.parametrize("confirm_callback", [True, False])
@pytest.mark.parametrize(
    "components",
    [
        [
            html.Button(id="button", children="Send confirm", n_clicks=0),
            dcc.ConfirmDialog(id="confirm", message="Please confirm."),
        ],
        [
            dcc.ConfirmDialogProvider(
                html.Button("click me", id="button"),
                id="confirm",
                message="Please confirm.",
            )
        ],
    ],
)
def test_cnfd001_dialog(dash_dcc, confirm_callback, confirms, components):
    app = Dash(__name__)
    app.layout = html.Div(components + [html.Div(id="confirmed")])

    @app.callback(Output("confirm", "displayed"), [Input("button", "n_clicks")])
    def on_click_confirm(n_clicks):
        if n_clicks:
            return True

    count = Value("i", 0)

    if confirm_callback:

        @app.callback(
            Output("confirmed", "children"),
            [
                Input("confirm", "submit_n_clicks"),
                Input("confirm", "cancel_n_clicks"),
            ],
            [
                State("confirm", "submit_n_clicks_timestamp"),
                State("confirm", "cancel_n_clicks_timestamp"),
            ],
        )
        def on_confirmed(
            submit_n_clicks,
            cancel_n_clicks,
            submit_timestamp,
            cancel_timestamp,
        ):
            count.value += 1

            if not submit_n_clicks and not cancel_n_clicks:
                return ""

            trigger = callback_context.triggered[0]["prop_id"].split(".")[1]

            return "confirmed" if trigger == "submit_n_clicks" else "canceled"

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#button")

    for confirm in confirms:
        dash_dcc.find_element("#button").click()
        time.sleep(0.5)
        if confirm:
            dash_dcc.driver.switch_to.alert.accept()
        else:
            dash_dcc.driver.switch_to.alert.dismiss()
        time.sleep(0.5)

        if confirm_callback:
            dash_dcc.wait_for_text_to_equal(
                "#confirmed", "confirmed" if confirm else "canceled"
            )

    if confirm_callback:
        assert wait.until(lambda: count.value == 1 + len(confirms), 3)

    assert dash_dcc.get_logs() == []


def test_cnfd002_injected_confirm(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="button", children="Send confirm"),
            html.Div(id="confirm-container"),
            dcc.Location(id="dummy-location"),
        ]
    )

    @app.callback(
        Output("confirm-container", "children"),
        [Input("button", "n_clicks")],
    )
    def on_click(n_clicks):
        if n_clicks:
            return dcc.ConfirmDialog(
                displayed=True, id="confirm", message="Please confirm."
            )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#button").click()

    time.sleep(1)
    dash_dcc.driver.switch_to.alert.accept()

    assert dash_dcc.get_logs() == []
