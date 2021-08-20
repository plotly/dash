from dash.exceptions import PreventUpdate
from dash import Dash, Input, Output, dcc, html
import flask
import time


def test_llgo001_location_logout(dash_dcc):
    app = Dash(__name__)

    @app.server.route("/_logout", methods=["POST"])
    def on_logout():
        rep = flask.redirect("/logged-out")
        rep.set_cookie("logout-cookie", "", 0)
        return rep

    app.layout = html.Div(
        [html.H2("Logout test"), dcc.Location(id="location"), html.Div(id="content")]
    )

    @app.callback(Output("content", "children"), [Input("location", "pathname")])
    def on_location(location_path):
        if location_path is None:
            raise PreventUpdate

        if "logged-out" in location_path:
            return "Logged out"
        else:

            @flask.after_this_request
            def _insert_cookie(rep):
                rep.set_cookie("logout-cookie", "logged-in")
                return rep

            return dcc.LogoutButton(id="logout-btn", logout_url="/_logout")

    dash_dcc.start_server(app)
    time.sleep(1)
    dash_dcc.percy_snapshot("Core Logout button")

    assert dash_dcc.driver.get_cookie("logout-cookie")["value"] == "logged-in"

    dash_dcc.wait_for_element("#logout-btn").click()
    dash_dcc.wait_for_text_to_equal("#content", "Logged out")

    assert not dash_dcc.driver.get_cookie("logout-cookie")

    assert dash_dcc.get_logs() == []
