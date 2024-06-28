from dash.exceptions import PreventUpdate
from dash import Dash, Input, Output, dcc, html
import flask
import pytest
import time


@pytest.mark.parametrize("add_initial_logout_button", [False, True])
def test_llgo001_location_logout(dash_dcc, add_initial_logout_button):
    app = Dash(__name__)

    @app.server.route("/_logout", methods=["POST"])
    def on_logout():
        rep = flask.redirect("/logged-out")
        rep.set_cookie("logout-cookie", "", 0)
        return rep

    layout_children = [
        html.H2("Logout test"),
        dcc.Location(id="location"),
        html.Div(id="content"),
    ]
    if add_initial_logout_button:
        layout_children.append(dcc.LogoutButton())
    app.layout = html.Div(layout_children)

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

    with pytest.warns(
        DeprecationWarning,
        match="The Logout Button is no longer used with Dash Enterprise and can be replaced with a html.Button or html.A.",
    ):
        dash_dcc.start_server(app)
        time.sleep(1)
        dash_dcc.percy_snapshot("Core Logout button")

        assert dash_dcc.driver.get_cookie("logout-cookie")["value"] == "logged-in"

        dash_dcc.wait_for_element("#logout-btn").click()
        dash_dcc.wait_for_text_to_equal("#content", "Logged out")

        assert not dash_dcc.driver.get_cookie("logout-cookie")

        assert dash_dcc.get_logs() == []
