import pytest
from dash import Dash, Input, Output, html, dcc


@pytest.mark.parametrize(
    "backend,fixture,input_value",
    [
        ("fastapi", "dash_duo", "Hello FastAPI!"),
        ("quart", "dash_duo_mp", "Hello Quart!"),
    ],
)
def test_backend_basic_callback(request, backend, fixture, input_value):
    dash_duo = request.getfixturevalue(fixture)
    if backend == "fastapi":
        from fastapi import FastAPI

        server = FastAPI()
    else:
        import quart

        server = quart.Quart(__name__)
    app = Dash(__name__, server=server)
    app.layout = html.Div(
        [dcc.Input(id="input", value=input_value, type="text"), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), Input("input", "value"))
    def update_output(value):
        return f"You typed: {value}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", f"You typed: {input_value}")
    dash_duo.clear_input(dash_duo.find_element("#input"))
    dash_duo.find_element("#input").send_keys(f"{backend.title()} Test")
    dash_duo.wait_for_text_to_equal("#output", f"You typed: {backend.title()} Test")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize(
    "backend,fixture,start_server_kwargs",
    [
        (
            "fastapi",
            "dash_duo",
            {"debug": True, "reload": False, "dev_tools_ui": True},
        ),
        (
            "quart",
            "dash_duo_mp",
            {
                "debug": True,
                "use_reloader": False,
                "dev_tools_hot_reload": False,
            },
        ),
    ],
)
def test_backend_error_handling(request, backend, fixture, start_server_kwargs):
    dash_duo = request.getfixturevalue(fixture)
    app = Dash(__name__, backend=backend)
    app.layout = html.Div(
        [html.Button(id="btn", children="Error", n_clicks=0), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def error_callback(n):
        if n and n > 0:
            return 1 / 0  # Intentional error
        return "No error"

    dash_duo.start_server(app, **start_server_kwargs)
    dash_duo.wait_for_text_to_equal("#output", "No error")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")


def get_error_html(dash_duo, index):
    # error is in an iframe so is annoying to read out - get it from the store
    return dash_duo.driver.execute_script(
        "return store.getState().error.backEnd[{}].error.html;".format(index)
    )


@pytest.mark.parametrize(
    "backend,fixture,start_server_kwargs, error_msg",
    [
        (
            "fastapi",
            "dash_duo",
            {
                "debug": True,
                "dev_tools_ui": True,
                "dev_tools_prune_errors": False,
                "reload": False,
            },
            "_fastapi.py",
        ),
        (
            "quart",
            "dash_duo_mp",
            {
                "debug": True,
                "use_reloader": False,
                "dev_tools_hot_reload": False,
                "dev_tools_prune_errors": False,
            },
            "_quart.py",
        ),
    ],
)
def test_backend_error_handling_no_prune(
    request, backend, fixture, start_server_kwargs, error_msg
):
    dash_duo = request.getfixturevalue(fixture)
    app = Dash(__name__, backend=backend)
    app.layout = html.Div(
        [html.Button(id="btn", children="Error", n_clicks=0), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def error_callback(n):
        if n and n > 0:
            return 1 / 0  # Intentional error
        return "No error"

    dash_duo.start_server(app, **start_server_kwargs)
    dash_duo.wait_for_text_to_equal("#output", "No error")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")

    error0 = get_error_html(dash_duo, 0)
    assert "in error_callback" in error0
    assert "ZeroDivisionError" in error0
    assert "backends/" in error0 and error_msg in error0


@pytest.mark.parametrize(
    "backend,fixture,start_server_kwargs, error_msg",
    [
        ("fastapi", "dash_duo", {"debug": True, "reload": False}, "fastapi.py"),
        (
            "quart",
            "dash_duo_mp",
            {
                "debug": True,
                "use_reloader": False,
                "dev_tools_hot_reload": False,
            },
            "quart.py",
        ),
    ],
)
def test_backend_error_handling_prune(
    request, backend, fixture, start_server_kwargs, error_msg
):
    dash_duo = request.getfixturevalue(fixture)
    app = Dash(__name__, backend=backend)
    app.layout = html.Div(
        [html.Button(id="btn", children="Error", n_clicks=0), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def error_callback(n):
        if n and n > 0:
            return 1 / 0  # Intentional error
        return "No error"

    dash_duo.start_server(app, **start_server_kwargs)
    dash_duo.wait_for_text_to_equal("#output", "No error")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")

    error0 = get_error_html(dash_duo, 0)
    assert "in error_callback" in error0
    assert "ZeroDivisionError" in error0
    assert "dash/backends/" not in error0 and error_msg not in error0


@pytest.mark.parametrize(
    "backend,fixture,input_value",
    [
        ("fastapi", "dash_duo", "Background FastAPI!"),
        ("quart", "dash_duo_mp", "Background Quart!"),
    ],
)
def test_backend_background_callback(request, backend, fixture, input_value):
    dash_duo = request.getfixturevalue(fixture)
    import diskcache

    cache = diskcache.Cache("./cache")
    from dash.background_callback import DiskcacheManager

    background_callback_manager = DiskcacheManager(cache)

    app = Dash(
        __name__,
        backend=backend,
        background_callback_manager=background_callback_manager,
    )
    app.layout = html.Div(
        [dcc.Input(id="input", value=input_value, type="text"), html.Div(id="output")]
    )

    @app.callback(
        Output("output", "children"), Input("input", "value"), background=True
    )
    def update_output_bg(value):
        return f"Background typed: {value}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", f"Background typed: {input_value}")
    dash_duo.clear_input(dash_duo.find_element("#input"))
    dash_duo.find_element("#input").send_keys(f"{backend.title()} BG Test")
    dash_duo.wait_for_text_to_equal(
        "#output", f"Background typed: {backend.title()} BG Test"
    )
    assert dash_duo.get_logs() == []
