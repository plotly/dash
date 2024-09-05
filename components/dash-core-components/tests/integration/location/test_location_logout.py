from dash import Dash, Input, Output, dcc, html
import pytest
import time


@pytest.mark.parametrize("add_initial_logout_button", [False, True])
def test_llgo001_location_logout(dash_dcc, add_initial_logout_button):
    # FIXME: Logout button is deprecated, remove this test for dash 3.0
    app = Dash(__name__)

    with pytest.warns(
        DeprecationWarning,
        match="The Logout Button is no longer used with Dash Enterprise and can be replaced with a html.Button or html.A.",
    ):
        app.layout = [
            html.H2("Logout test"),
            html.Div(id="content"),
        ]
        if add_initial_logout_button:
            app.layout.append(dcc.LogoutButton())
        else:

            @app.callback(Output("content", "children"), Input("content", "id"))
            def on_location(location_path):
                return dcc.LogoutButton(id="logout-btn", logout_url="/_logout")

            dash_dcc.start_server(app)
            time.sleep(1)

            assert dash_dcc.get_logs() == []
