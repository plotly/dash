import pytest
from dash import Dash, Input, Output, html, dcc
from fastapi import FastAPI
import traceback
import re
from dash.backends._fastapi import FastAPIDashServer


class CustomDashServer(FastAPIDashServer):
    def _get_traceback(self, _secret, error: Exception):
        tb = error.__traceback__
        errors = traceback.format_exception(type(error), error, tb)
        pass_errs = []
        callback_handled = False
        for err in errors:
            if self.error_handling_mode == "prune":
                if not callback_handled:
                    if "callback invoked" in str(err) and "_callback.py" in str(err):
                        callback_handled = True
                    continue
            pass_errs.append(err)
        formatted_tb = "".join(pass_errs)
        error_type = type(error).__name__
        error_msg = str(error)
        # Parse traceback lines to group by file
        file_cards = []
        pattern = re.compile(r'  File "(.+)", line (\d+), in (\w+)')
        lines = formatted_tb.split("\n")
        current_file = None
        card_lines = []
        for line in lines[:-1]:  # Skip the last line (error message)
            match = pattern.match(line)
            if match:
                if current_file and card_lines:
                    file_cards.append((current_file, card_lines))
                current_file = (
                    f"{match.group(1)} (line {match.group(2)}, in {match.group(3)})"
                )
                card_lines = [line]
            elif current_file:
                card_lines.append(line)
        if current_file and card_lines:
            file_cards.append((current_file, card_lines))
        cards_html = ""
        for filename, card in file_cards:
            cards_html += (
                f"""
            <div class=\"error-card\">
                <div class=\"error-card-header\">{filename}</div>
                <pre class=\"error-card-traceback\">"""
                + "\n".join(card)
                + """</pre>
            </div>
            """
            )
        html = f"""
        <!doctype html>
        <html lang=\"en\">
          <head>
            <title>{error_type}: {error_msg} // Custom Debugger</title>
            <style>
              body {{ font-family: monospace; background: #fff; color: #333; }}
              .debugger {{ margin: 2em; max-width: 700px; }}
            </style>
          </head>
          <body>
            <div class=\"debugger\">
              <h1>{error_type}: {error_msg}</h1>
              {cards_html}
            </div>
          </body>
        </html>
        """
        return html


@pytest.mark.parametrize(
    "fixture,input_value",
    [
        ("dash_duo", "Hello CustomBackend!"),
    ],
)
def test_custom_backend_basic_callback(request, fixture, input_value):
    dash_duo = request.getfixturevalue(fixture)
    app = Dash(__name__, backend=CustomDashServer)
    app.layout = html.Div(
        [dcc.Input(id="input", value=input_value, type="text"), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), Input("input", "value"))
    def update_output(value):
        return f"You typed: {value}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", f"You typed: {input_value}")
    dash_duo.clear_input(dash_duo.find_element("#input"))
    dash_duo.find_element("#input").send_keys("CustomBackend Test")
    dash_duo.wait_for_text_to_equal("#output", "You typed: CustomBackend Test")
    assert dash_duo.get_logs() == []


@pytest.mark.parametrize(
    "fixture,start_server_kwargs",
    [
        ("dash_duo", {"debug": True, "reload": False, "dev_tools_ui": True}),
    ],
)
def test_custom_backend_error_handling(request, fixture, start_server_kwargs):
    dash_duo = request.getfixturevalue(fixture)
    app = Dash(__name__, backend=CustomDashServer)
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
    "fixture,start_server_kwargs",
    [
        (
            "dash_duo",
            {
                "debug": True,
                "dev_tools_ui": True,
                "dev_tools_prune_errors": False,
                "reload": False,
            },
        ),
    ],
)
def test_custom_backend_error_handling_no_prune(request, fixture, start_server_kwargs):
    dash_duo = request.getfixturevalue(fixture)
    app = Dash(__name__, backend=CustomDashServer)
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
    assert "Custom Debugger" in error0
    assert "in error_callback" in error0
    assert "ZeroDivisionError" in error0
    assert "_callback.py" in error0


@pytest.mark.parametrize(
    "fixture,start_server_kwargs, error_msg",
    [
        ("dash_duo", {"debug": True, "reload": False}, "custombackend.py"),
    ],
)
def test_custom_backend_error_handling_prune(
    request, fixture, start_server_kwargs, error_msg
):
    dash_duo = request.getfixturevalue(fixture)
    app = Dash(__name__, backend=CustomDashServer)
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
    assert "Custom Debugger" in error0
    assert "in error_callback" in error0
    assert "ZeroDivisionError" in error0
    assert "_callback.py" not in error0


@pytest.mark.parametrize(
    "fixture,input_value",
    [
        ("dash_duo", "Background CustomBackend!"),
    ],
)
def test_custom_backend_background_callback(request, fixture, input_value):
    dash_duo = request.getfixturevalue(fixture)
    import diskcache

    cache = diskcache.Cache("./cache")
    from dash.background_callback import DiskcacheManager

    background_callback_manager = DiskcacheManager(cache)

    app = Dash(
        __name__,
        backend=CustomDashServer,
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
    dash_duo.find_element("#input").send_keys("CustomBackend BG Test")
    dash_duo.wait_for_text_to_equal(
        "#output", "Background typed: CustomBackend BG Test"
    )
    assert dash_duo.get_logs() == []
