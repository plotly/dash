from multiprocessing import Lock, Value
import time

import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output, State


def test_lcb001_fast_input(dash_duo, diskcache_manager):
    """
    Make sure that we settle to the correct final value when handling rapid inputs
    """
    lock = Lock()

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(html.Div([1.5, None, "string", html.Div(id="output-1")])),
        ]
    )

    @app.long_callback(
        diskcache_manager,
        Output("output-1", "children"),
        [Input("input", "value")],
        interval=500,
    )
    def update_output(value):
        time.sleep(0.1)
        return value

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output-1", "initial value", 2)
    input_ = dash_duo.find_element("#input")
    dash_duo.clear_input(input_)

    for key in "hello world":
        with lock:
            input_.send_keys(key)

    dash_duo.wait_for_text_to_equal("#output-1", "hello world", 4)
    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []


def test_lcb002_long_callback_running(dash_duo, diskcache_manager):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="button-1", children="Click Here", n_clicks=0),
            html.Div(id="status", children="Finished"),
            html.Div(id="result", children="Not clicked"),
        ]
    )

    @app.long_callback(
        diskcache_manager,
        Output("result", "children"),
        [Input("button-1", "n_clicks")],
        running=[(Output("status", "children"), "Running", "Finished")],
        interval=500,
    )
    def update_output(n_clicks):
        time.sleep(2)
        return f"Clicked {n_clicks} time(s)"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#result", "Clicked 0 time(s)", 4)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 4)

    # Click button and check that status has changed to "Running"
    dash_duo.find_element("#button-1").click()
    dash_duo.wait_for_text_to_equal("#status", "Running", 2)

    # Wait for calculation to finish, then check that status is "Finished"
    dash_duo.wait_for_text_to_equal("#result", "Clicked 1 time(s)", 4)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 2)

    # Click button twice and check that status has changed to "Running"
    dash_duo.find_element("#button-1").click()
    dash_duo.find_element("#button-1").click()
    dash_duo.wait_for_text_to_equal("#status", "Running", 2)

    # Wait for calculation to finish, then check that status is "Finished"
    dash_duo.wait_for_text_to_equal("#result", "Clicked 3 time(s)", 4)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 2)

    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []


def test_lcb003_long_callback_running_cancel(dash_duo, diskcache_manager):
    lock = Lock()
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Button(id="run-button", children="Run"),
            html.Button(id="cancel-button", children="Cancel"),
            html.Div(id="status", children="Finished"),
            html.Div(id="result", children="No results"),
        ]
    )

    @app.long_callback(
        diskcache_manager,
        Output("result", "children"),
        [Input("run-button", "n_clicks"), State("input", "value")],
        running=[(Output("status", "children"), "Running", "Finished")],
        cancel=[Input("cancel-button", "n_clicks")],
        interval=500,
    )
    def update_output(n_clicks, value):
        time.sleep(2)
        return f"Processed '{value}'"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#result", "Processed 'initial value'", 4)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 4)

    # Update input text box
    input_ = dash_duo.find_element("#input")
    dash_duo.clear_input(input_)

    for key in "hello world":
        with lock:
            input_.send_keys(key)

    # Click run button and check that status has changed to "Running"
    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Running", 2)

    # Then click Cancel button and make sure that the status changes to finish
    # without update result
    dash_duo.find_element("#cancel-button").click()
    dash_duo.wait_for_text_to_equal("#result", "Processed 'initial value'", 4)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 4)

    # Click run button again, and let it finish
    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Running", 2)
    dash_duo.wait_for_text_to_equal("#result", "Processed 'hello world'", 4)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 2)

    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []


def test_lcb004_long_callback_progress(dash_duo, diskcache_manager):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value="hello, world"),
            html.Button(id="run-button", children="Run"),
            html.Button(id="cancel-button", children="Cancel"),
            html.Div(id="status", children="Finished"),
            html.Div(id="result", children="No results"),
        ]
    )

    @app.long_callback(
        diskcache_manager,
        Output("result", "children"),
        [Input("run-button", "n_clicks"), State("input", "value")],
        progress=Output("status", "children"),
        progress_default="Finished",
        cancel=[Input("cancel-button", "n_clicks")],
        interval=500,
        prevent_initial_callback=True,
    )
    def update_output(set_progress, n_clicks, value):
        for i in range(4):
            set_progress(f"Progress {i}/4")
            time.sleep(1)
        return f"Processed '{value}'"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#result", "No results", 2)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 2)

    # Click run button and check that status eventually cycles to 2/4
    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 4)

    # Then click Cancel button and make sure that the status changes to finish
    # without updating result
    dash_duo.find_element("#cancel-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Finished", 4)
    dash_duo.wait_for_text_to_equal("#result", "No results", 4)

    # Click run button and allow callback to finish
    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 4)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 4)
    dash_duo.wait_for_text_to_equal("#result", "Processed 'hello, world'", 2)

    # Click run button again with same input.
    # without caching, this should rerun callback and display progress
    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 4)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 4)
    dash_duo.wait_for_text_to_equal("#result", "Processed 'hello, world'", 2)

    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []


def test_lcb005_long_callback_caching(dash_duo, diskcache_manager):
    lock = Lock()

    # Control return value of cache_by function using multiprocessing value
    cache_key = Value("i", 0)

    def cache_fn():
        return cache_key.value

    diskcache_manager.cache_by = [cache_fn]

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value="AAA"),
            html.Button(id="run-button", children="Run", n_clicks=0),
            html.Div(id="status", children="Finished"),
            html.Div(id="result", children="No results"),
        ]
    )

    @app.long_callback(
        diskcache_manager,
        [Output("result", "children"), Output("run-button", "n_clicks")],
        [Input("run-button", "n_clicks"), State("input", "value")],
        progress=Output("status", "children"),
        progress_default="Finished",
        interval=500,
        prevent_initial_callback=True,
    )
    def update_output(set_progress, _n_clicks, value):
        for i in range(4):
            set_progress(f"Progress {i}/4")
            time.sleep(2)
        return f"Result for '{value}'", 0

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#result", "No results", 2)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 2)

    # Click run button and check that status eventually cycles to 2/4
    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 6)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 6)
    dash_duo.wait_for_text_to_equal("#result", "Result for 'AAA'", 1)

    # Update input text box to BBB
    input_ = dash_duo.find_element("#input")
    dash_duo.clear_input(input_)
    for key in "BBB":
        with lock:
            input_.send_keys(key)

    # Click run button and check that status eventually cycles to 2/4
    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 6)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 6)
    dash_duo.wait_for_text_to_equal("#result", "Result for 'BBB'", 1)

    # Update input text box back to AAA
    input_ = dash_duo.find_element("#input")
    dash_duo.clear_input(input_)
    for key in "AAA":
        with lock:
            input_.send_keys(key)

    # Click run button and this time the cached result is used,
    # So we can get the result right away
    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Finished", 1)
    dash_duo.wait_for_text_to_equal("#result", "Result for 'AAA'", 1)

    # Update input text box back to BBB
    input_ = dash_duo.find_element("#input")
    dash_duo.clear_input(input_)
    for key in "BBB":
        with lock:
            input_.send_keys(key)

    # Click run button and this time the cached result is used,
    # So we can get the result right away
    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Finished", 1)
    dash_duo.wait_for_text_to_equal("#result", "Result for 'BBB'", 1)

    # Update input text box back to AAA
    input_ = dash_duo.find_element("#input")
    dash_duo.clear_input(input_)
    for key in "AAA":
        with lock:
            input_.send_keys(key)

    # Change cache key
    cache_key.value = 1

    dash_duo.find_element("#run-button").click()
    dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 6)
    dash_duo.wait_for_text_to_equal("#status", "Finished", 6)
    dash_duo.wait_for_text_to_equal("#result", "Result for 'AAA'", 1)

    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []
