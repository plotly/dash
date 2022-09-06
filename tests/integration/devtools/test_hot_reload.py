import os
from time import sleep

from dash.testing.wait import until

from dash import Dash, Input, Output, html
from dash.exceptions import PreventUpdate


RED_BG = """
#hot-reload-content {
    background-color: red;
}
"""

GOUDA = """
window.cheese = 'gouda';
"""


def replace_file(filename, new_content):
    path = os.path.join(os.path.dirname(__file__), "hr_assets", filename)
    with open(path, "r+") as fp:
        sleep(1)  # ensure a new mod time
        old_content = fp.read()
        fp.truncate(0)
        fp.seek(0)
        fp.write(new_content)

    return path, old_content


def test_dvhr001_hot_reload(dash_duo_mp):
    app = Dash(__name__, assets_folder="hr_assets")
    app.layout = html.Div(
        [html.H3("Hot reload", id="text"), html.Button("Click", id="btn")],
        id="hot-reload-content",
    )

    @app.callback(Output("text", "children"), [Input("btn", "n_clicks")])
    def new_text(n):
        if not n:
            raise PreventUpdate
        return n

    hot_reload_settings = dict(
        dev_tools_hot_reload=True,
        dev_tools_ui=True,
        dev_tools_serve_dev_bundles=True,
        dev_tools_hot_reload_interval=0.1,
        dev_tools_hot_reload_max_retry=100,
    )

    dash_duo_mp.start_server(app, **hot_reload_settings)

    # default overload color is blue
    dash_duo_mp.wait_for_style_to_equal(
        "#hot-reload-content", "background-color", "rgba(0, 0, 255, 1)"
    )

    # set a global var - if we soft reload it should still be there,
    # hard reload will delete it
    dash_duo_mp.driver.execute_script("window.someVar = 42;")
    assert dash_duo_mp.driver.execute_script("return window.someVar") == 42

    soft_reload_file, old_soft = replace_file("hot_reload.css", RED_BG)

    try:
        # red is live changed during the test execution
        dash_duo_mp.wait_for_style_to_equal(
            "#hot-reload-content", "background-color", "rgba(255, 0, 0, 1)"
        )
    finally:
        sleep(1)  # ensure a new mod time
        with open(soft_reload_file, "w") as f:
            f.write(old_soft)

    dash_duo_mp.wait_for_style_to_equal(
        "#hot-reload-content", "background-color", "rgba(0, 0, 255, 1)"
    )

    # only soft reload, someVar is still there
    assert dash_duo_mp.driver.execute_script("return window.someVar") == 42

    assert dash_duo_mp.driver.execute_script("return window.cheese") == "roquefort"

    hard_reload_file, old_hard = replace_file("hot_reload.js", GOUDA)

    try:
        until(
            lambda: dash_duo_mp.driver.execute_script("return window.cheese")
            == "gouda",
            timeout=10,
        )
    finally:
        sleep(1)  # ensure a new mod time
        with open(hard_reload_file, "w") as f:
            f.write(old_hard)

    until(
        lambda: dash_duo_mp.driver.execute_script("return window.cheese")
        == "roquefort",
        timeout=10,
    )

    # we've done a hard reload so someVar is gone
    assert dash_duo_mp.driver.execute_script("return window.someVar") is None

    # Now check the server status indicator functionality

    dash_duo_mp.find_element(".dash-debug-menu").click()
    dash_duo_mp.find_element(".dash-debug-menu__button--available")
    sleep(1)  # wait for opening animation
    dash_duo_mp.percy_snapshot(name="hot-reload-available")

    dash_duo_mp.server.stop()
    sleep(1)
    dash_duo_mp.wait_for_element(".dash-debug-menu__button--unavailable")
    dash_duo_mp.wait_for_no_elements(".dash-fe-error__title")
    dash_duo_mp.percy_snapshot(name="hot-reload-unavailable")

    dash_duo_mp.find_element(".dash-debug-menu").click()
    sleep(1)  # wait for opening animation
    dash_duo_mp.find_element(".dash-debug-disconnected")
    dash_duo_mp.percy_snapshot(name="hot-reload-unavailable-small")

    dash_duo_mp.find_element("#btn").click()
    dash_duo_mp.wait_for_text_to_equal(
        ".dash-fe-error__title", "Callback failed: the server did not respond."
    )

    # start up the server again
    dash_duo_mp.start_server(app, **hot_reload_settings)

    # rerenders with debug menu closed after reload
    # reopen and check that server is now available
    dash_duo_mp.find_element(".dash-debug-menu--closed").click()
    dash_duo_mp.find_element(".dash-debug-menu__button--available")
