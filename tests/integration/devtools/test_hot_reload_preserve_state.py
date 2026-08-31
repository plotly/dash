from selenium.common.exceptions import WebDriverException

from dash._utils import generate_hash
from dash.testing.wait import until

from dash import Dash, Input, Output, dcc, html, no_update, set_props


def make_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input-a", value="initial-a"),
            dcc.Input(id="input-b", value="initial-b"),
            dcc.Dropdown(id="dropdown", options=["a", "b", "c"], value="a"),
            html.Div(id="out"),
            html.Div(id="dd-out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("input-a", "value"))
    def out(value):
        return f"out: {value}"

    @app.callback(Output("dd-out", "children"), Input("dropdown", "value"))
    def dd_out(value):
        return f"dd: {value}"

    return app


hot_reload_settings = dict(
    dev_tools_hot_reload=True,
    dev_tools_ui=True,
    dev_tools_serve_dev_bundles=True,
    dev_tools_hot_reload_interval=0.1,
    dev_tools_hot_reload_max_retry=100,
)


def soft_reload(app):
    # Simulate the hash change the server produces when it restarts after
    # a backend code edit.
    _reload = app._hot_reload
    with _reload.lock:
        _reload.hash = generate_hash()


def hard_reload(app):
    # Simulate a non-css asset change: hard=True with no css files makes
    # the renderer do a full page reload.
    _reload = app._hot_reload
    with _reload.lock:
        _reload.hash = generate_hash()
        _reload.hard = True


def test_dvps001_soft_reload_preserves_ui_state(dash_duo):
    app = make_app()
    dash_duo.start_server(
        app, dev_tools_hot_reload_preserve_state=True, **hot_reload_settings
    )

    dash_duo.wait_for_text_to_equal("#out", "out: initial-a")

    # Make some UI edits.
    dash_duo.find_element("#input-a").send_keys("-edited")
    dash_duo.wait_for_text_to_equal("#out", "out: initial-a-edited")
    dash_duo.select_dcc_dropdown("#dropdown", "b")
    dash_duo.wait_for_text_to_equal("#dd-out", "dd: b")

    # Soft reloads keep the js context - use a marker to prove the page
    # itself did not reload.
    dash_duo.driver.execute_script("window.someVar = 42;")

    # Change input-b's initial value in the "new code": the new value must
    # win over any preserved state.
    app.layout.children[1].value = "changed-in-code"
    soft_reload(app)

    # The new layout is in: the reload really happened.
    dash_duo.wait_for_text_to_equal("#input-b", "changed-in-code")
    # It was a soft reload.
    assert dash_duo.driver.execute_script("return window.someVar") == 42

    # UI edits to unchanged-in-code props were restored, and the initial
    # callbacks re-ran with the restored values.
    dash_duo.wait_for_text_to_equal("#input-a", "initial-a-edited")
    dash_duo.wait_for_text_to_equal("#out", "out: initial-a-edited")
    dash_duo.wait_for_text_to_equal("#dd-out", "dd: b")

    assert dash_duo.get_logs() == []


def test_dvps002_hard_reload_preserves_ui_state(dash_duo):
    app = make_app()
    dash_duo.start_server(
        app, dev_tools_hot_reload_preserve_state=True, **hot_reload_settings
    )

    dash_duo.wait_for_text_to_equal("#out", "out: initial-a")
    dash_duo.find_element("#input-a").send_keys("-edited")
    dash_duo.wait_for_text_to_equal("#out", "out: initial-a-edited")

    dash_duo.driver.execute_script("window.someVar = 42;")
    hard_reload(app)

    # The page fully reloaded: the js context is gone.
    def some_var_gone():
        try:
            return dash_duo.driver.execute_script("return window.someVar") is None
        except WebDriverException:
            return False

    until(some_var_gone, timeout=10)

    # But the UI edit survived through sessionStorage.
    dash_duo.wait_for_text_to_equal("#input-a", "initial-a-edited")
    dash_duo.wait_for_text_to_equal("#out", "out: initial-a-edited")

    # A manual browser refresh is the escape hatch: no snapshot is written,
    # so the app comes back in its initial state.
    dash_duo.driver.refresh()
    dash_duo.wait_for_text_to_equal("#input-a", "initial-a")
    dash_duo.wait_for_text_to_equal("#out", "out: initial-a")


def test_dvps003_preserve_state_off_by_default(dash_duo):
    app = make_app()
    dash_duo.start_server(app, **hot_reload_settings)

    dash_duo.wait_for_text_to_equal("#out", "out: initial-a")
    dash_duo.find_element("#input-a").send_keys("-edited")
    dash_duo.wait_for_text_to_equal("#out", "out: initial-a-edited")

    # Add a marker component so we can tell the reload completed.
    app.layout.children.append(html.Div("v2", id="version"))
    soft_reload(app)

    dash_duo.wait_for_text_to_equal("#version", "v2")

    # Without the flag, the soft reload resets UI state.
    dash_duo.wait_for_text_to_equal("#out", "out: initial-a")
    dash_duo.wait_for_text_to_equal("#input-a", "initial-a")


def test_dvps004_preserves_state_in_callback_generated_content(dash_duo):
    # Components that only exist after an initial callback runs (e.g. pages
    # content) don't appear in the initial layout: their state is restored
    # when the callback inserts them.
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div([html.Div(id="content"), html.Div(id="out")])

    @app.callback(Output("content", "children"), Input("content", "id"))
    def render_content(_):
        return dcc.Input(id="inner-input", value="initial-inner")

    @app.callback(Output("out", "children"), Input("inner-input", "value"))
    def out(value):
        return f"out: {value}"

    dash_duo.start_server(
        app, dev_tools_hot_reload_preserve_state=True, **hot_reload_settings
    )

    dash_duo.wait_for_text_to_equal("#out", "out: initial-inner")
    dash_duo.find_element("#inner-input").send_keys("-edited")
    dash_duo.wait_for_text_to_equal("#out", "out: initial-inner-edited")

    dash_duo.driver.execute_script("window.someVar = 42;")
    soft_reload(app)

    # someVar still set: it was a soft reload; and the edit survived even
    # though the component came from a callback, not the initial layout.
    dash_duo.wait_for_text_to_equal("#inner-input", "initial-inner-edited")
    dash_duo.wait_for_text_to_equal("#out", "out: initial-inner-edited")
    assert dash_duo.driver.execute_script("return window.someVar") == 42

    assert dash_duo.get_logs() == []


def test_dvps005_preserves_memory_store_data(dash_duo):
    # Data written to a memory-type dcc.Store by a callback lives only in
    # the layout, so it must be preserved directly - it can't be recomputed
    # here since the writing callback has prevent_initial_call=True.
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            dcc.Store(id="store"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("store", "data"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def write(n_clicks):
        return {"n": n_clicks}

    @app.callback(Output("out", "children"), Input("store", "data"))
    def read(data):
        return f"data: {data}"

    dash_duo.start_server(
        app, dev_tools_hot_reload_preserve_state=True, **hot_reload_settings
    )

    dash_duo.wait_for_text_to_equal("#out", "data: None")
    dash_duo.find_element("#btn").click()
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out", "data: {'n': 2}")

    dash_duo.driver.execute_script("window.someVar = 42;")
    soft_reload(app)

    # The store data came back through the restore, not a recompute.
    dash_duo.wait_for_text_to_equal("#out", "data: {'n': 2}")
    assert dash_duo.driver.execute_script("return window.someVar") == 42

    assert dash_duo.get_logs() == []


def test_dvps006_preserves_clientside_set_props(dash_duo):
    # Props set through window.dash_clientside.set_props count as UI state.
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            dcc.Input(id="target", value="initial"),
            html.Div(id="out"),
        ]
    )

    app.clientside_callback(
        """
        function(n_clicks) {
            window.dash_clientside.set_props(
                'target', {value: 'set-' + n_clicks});
            return window.dash_clientside.no_update;
        }
        """,
        Output("btn", "style"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )

    @app.callback(Output("out", "children"), Input("target", "value"))
    def out(value):
        return f"out: {value}"

    dash_duo.start_server(
        app, dev_tools_hot_reload_preserve_state=True, **hot_reload_settings
    )

    dash_duo.wait_for_text_to_equal("#out", "out: initial")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out", "out: set-1")

    dash_duo.driver.execute_script("window.someVar = 42;")
    soft_reload(app)

    dash_duo.wait_for_text_to_equal("#target", "set-1")
    dash_duo.wait_for_text_to_equal("#out", "out: set-1")
    assert dash_duo.driver.execute_script("return window.someVar") == 42

    assert dash_duo.get_logs() == []


def test_dvps007_preserves_server_set_props(dash_duo):
    # Props set through dash.set_props in a server callback count as UI
    # state too.
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            dcc.Input(id="target", value="initial"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("btn", "style"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def set_target(n_clicks):
        set_props("target", {"value": f"set-{n_clicks}"})
        return no_update

    @app.callback(Output("out", "children"), Input("target", "value"))
    def out(value):
        return f"out: {value}"

    dash_duo.start_server(
        app, dev_tools_hot_reload_preserve_state=True, **hot_reload_settings
    )

    dash_duo.wait_for_text_to_equal("#out", "out: initial")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out", "out: set-1")

    dash_duo.driver.execute_script("window.someVar = 42;")
    soft_reload(app)

    dash_duo.wait_for_text_to_equal("#target", "set-1")
    dash_duo.wait_for_text_to_equal("#out", "out: set-1")
    assert dash_duo.driver.execute_script("return window.someVar") == 42

    assert dash_duo.get_logs() == []
