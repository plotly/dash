import pytest
from dash import ALL, Dash, Input, Output, html
from dash.testing.wait import until
import dash_test_components as dt


@pytest.mark.parametrize(
    "outputs", ["single", "mixed", "all", "all-sentinel", "pattern"]
)
def test_clnu001_no_update_does_not_redraw(dash_duo, outputs):
    app = Dash(__name__)
    pattern = outputs == "pattern"
    counters = (
        [dt.DrawCounter(id={"type": "counter", "index": i}) for i in range(2)]
        if pattern
        else [dt.DrawCounter(id="counter"), dt.DrawCounter(id="other")]
    )
    app.layout = html.Div(
        [html.Button("Run", id="run"), html.Div(id="active"), *counters]
    )
    callback_outputs = [Output("counter", "id")]
    body = "return dc.no_update;"
    if outputs in ("mixed", "all", "all-sentinel"):
        callback_outputs = [
            Output("counter", "id"),
            Output("active", "children"),
            Output("other", "id"),
        ]
        body = {
            "mixed": "return [dc.no_update, n, dc.no_update];",
            "all": "return [dc.no_update, dc.no_update, dc.no_update];",
            "all-sentinel": "return dc.no_update;",
        }[outputs]
    elif pattern:
        callback_outputs = [Output({"type": "counter", "index": ALL}, "id")]
        body = "return [dc.no_update, dc.no_update];"

    app.clientside_callback(
        "function(n) { const dc = window.dash_clientside; "
        "window.noUpdateCalls = (window.noUpdateCalls || 0) + 1; " + body + "}",
        *callback_outputs,
        Input("run", "n_clicks"),
        prevent_initial_call=True,
    )
    dash_duo.start_server(app)
    selectors = (
        [
            '[id=\'{"index":0,"type":"counter"}\']',
            '[id=\'{"index":1,"type":"counter"}\']',
        ]
        if pattern
        else ["#counter", "#other"]
    )
    for selector in selectors:
        dash_duo.wait_for_text_to_equal(selector, "1")
    for n in range(1, 4):
        dash_duo.find_element("#run").click()
        until(
            lambda: dash_duo.driver.execute_script("return window.noUpdateCalls;") == n
            and not dash_duo.redux_state_is_loading,
            timeout=5,
        )
        dash_duo.driver.execute_async_script(
            "const done = arguments[0]; requestAnimationFrame(() => requestAnimationFrame(done));"
        )
        for selector in selectors:
            assert dash_duo.find_element(selector).text == "1"
        if outputs == "mixed":
            dash_duo.wait_for_text_to_equal("#active", str(n))
    assert dash_duo.get_logs() == []


def test_clnu002_no_update_with_another_prop_on_the_same_component(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Run", id="run"),
            html.Div("initial", id="result", title="original"),
        ]
    )
    app.clientside_callback(
        """function(n) {
            const skip = window.dash_clientside.no_update;
            return n % 2 ? [skip, String(n)] : [String(n), skip];
        }""",
        Output("result", "children"),
        Output("result", "title"),
        Input("run", "n_clicks"),
        prevent_initial_call=True,
    )
    dash_duo.start_server(app)
    for n in range(1, 4):
        dash_duo.find_element("#run").click()
        until(
            lambda: dash_duo.find_element("#result").get_attribute("title")
            == str(n if n % 2 else n - 1),
            timeout=5,
        )
        dash_duo.wait_for_text_to_equal("#result", "initial" if n == 1 else "2")
    assert dash_duo.get_logs() == []
