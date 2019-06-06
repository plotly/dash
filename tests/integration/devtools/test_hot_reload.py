import os
import textwrap
import dash_html_components as html
import dash


def test_dvhr001_hot_reload(dash_duo):
    app = dash.Dash(__name__, assets_folder="hr_assets")
    app.layout = html.Div([html.H3("Hot reload")], id="hot-reload-content")

    dash_duo.start_app_server(
        app,
        dev_tools_hot_reload=True,
        dev_tools_hot_reload_interval=100,
        dev_tools_hot_reload_max_retry=30,
    )

    # default overload color is blue
    dash_duo.wait_for_style_to_equal(
        "#hot-reload-content", "background-color", "rgba(0, 0, 255, 1)"
    )

    hot_reload_file = os.path.join(
        os.path.dirname(__file__), "hr_assets", "hot_reload.css"
    )
    with open(hot_reload_file, "r+") as fp:
        old_content = fp.read()
        fp.truncate(0)
        fp.seek(0)
        fp.write(
            textwrap.dedent(
                """
        #hot-reload-content {
            background-color: red;
        }
        """
            )
        )

    try:
        # red is live changed during the test execution
        dash_duo.wait_for_style_to_equal(
            "#hot-reload-content", "background-color", "rgba(255, 0, 0, 1)"
        )
    finally:
        with open(hot_reload_file, "w") as f:
            f.write(old_content)
