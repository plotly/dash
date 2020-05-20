from time import sleep

import dash_core_components as dcc
import dash_html_components as html
import dash
import dash.testing.wait as wait


def test_dvui001_disable_props_check_config(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            html.P(id="tcid", children="Hello Props Check"),
            dcc.Graph(id="broken", animate=3),  # error ignored by disable
        ]
    )

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
        dev_tools_props_check=False,
    )

    dash_duo.wait_for_text_to_equal("#tcid", "Hello Props Check")
    assert dash_duo.find_elements("#broken svg.main-svg"), "graph should be rendered"

    # open the debug menu so we see the "hot reload off" indicator
    dash_duo.find_element(".dash-debug-menu").click()
    sleep(1)  # wait for debug menu opening animation

    dash_duo.percy_snapshot("devtools - disable props check - Graph should render")


def test_dvui002_disable_ui_config(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            html.P(id="tcid", children="Hello Disable UI"),
            dcc.Graph(id="broken", animate=3),  # error ignored by disable
        ]
    )

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
        dev_tools_ui=False,
    )

    dash_duo.wait_for_text_to_equal("#tcid", "Hello Disable UI")
    logs = str(wait.until(dash_duo.get_logs, timeout=1))
    assert (
        "Invalid argument `animate` passed into Graph" in logs
    ), "the error should present in the console without DEV tools UI"

    assert not dash_duo.find_elements(
        ".dash-debug-menu"
    ), "the debug menu icon should NOT show up"
    dash_duo.percy_snapshot("devtools - disable dev tools UI - no debug menu")
