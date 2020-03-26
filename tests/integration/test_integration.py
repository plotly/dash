import datetime

from copy import copy
from multiprocessing import Value
from selenium.webdriver.common.keys import Keys

import pytest

from bs4 import BeautifulSoup

import dash_dangerously_set_inner_html
import dash_flow_example

import dash_html_components as html
import dash_core_components as dcc

from dash import Dash, no_update

from dash.dependencies import Input, Output, State
from dash.exceptions import (
    PreventUpdate,
    InvalidCallbackReturnValue,
    IncorrectTypeException,
)
from dash.testing.wait import until


def test_inin001_simple_callback(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(html.Div([1.5, None, "string", html.Div(id="output-1")])),
        ]
    )

    call_count = Value("i", 0)

    @app.callback(Output("output-1", "children"), [Input("input", "value")])
    def update_output(value):
        call_count.value += 1
        return value

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output-1", "initial value")
    dash_duo.percy_snapshot(name="simple-callback-1")

    input1 = dash_duo.find_element("#input")
    dash_duo.clear_input(input1)
    input1.send_keys("hello world")

    dash_duo.wait_for_text_to_equal("#output-1", "hello world")
    dash_duo.percy_snapshot(name="simple-callback-2")

    # an initial call, one for clearing the input
    # and one for each hello world character
    assert call_count.value == 2 + len("hello world")

    assert not dash_duo.get_logs()


def test_inin002_wildcard_callback(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(
                html.Div(
                    [
                        1.5,
                        None,
                        "string",
                        html.Div(
                            id="output-1",
                            **{"data-cb": "initial value", "aria-cb": "initial value"}
                        ),
                    ]
                )
            ),
        ]
    )

    input_call_count = Value("i", 0)

    @app.callback(Output("output-1", "data-cb"), [Input("input", "value")])
    def update_data(value):
        input_call_count.value += 1
        return value

    @app.callback(Output("output-1", "children"), [Input("output-1", "data-cb")])
    def update_text(data):
        return data

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output-1", "initial value")
    dash_duo.percy_snapshot(name="wildcard-callback-1")

    input1 = dash_duo.find_element("#input")
    dash_duo.clear_input(input1)
    input1.send_keys("hello world")

    dash_duo.wait_for_text_to_equal("#output-1", "hello world")
    dash_duo.percy_snapshot(name="wildcard-callback-2")

    # an initial call, one for clearing the input
    # and one for each hello world character
    assert input_call_count.value == 2 + len("hello world")

    assert not dash_duo.get_logs()


def test_inin003_aborted_callback(dash_duo):
    """Raising PreventUpdate OR returning no_update prevents update and
    triggering dependencies."""

    initial_input = "initial input"
    initial_output = "initial output"

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value=initial_input),
            html.Div(initial_output, id="output1"),
            html.Div(initial_output, id="output2"),
        ]
    )

    callback1_count = Value("i", 0)
    callback2_count = Value("i", 0)

    @app.callback(Output("output1", "children"), [Input("input", "value")])
    def callback1(value):
        callback1_count.value += 1
        if callback1_count.value > 2:
            return no_update
        raise PreventUpdate("testing callback does not update")
        return value

    @app.callback(Output("output2", "children"), [Input("output1", "children")])
    def callback2(value):
        callback2_count.value += 1
        return value

    dash_duo.start_server(app)

    input_ = dash_duo.find_element("#input")
    input_.send_keys("xyz")
    dash_duo.wait_for_text_to_equal("#input", "initial inputxyz")

    until(
        lambda: callback1_count.value == 4,
        timeout=3,
        msg="callback1 runs 4x (initial page load and 3x through send_keys)",
    )

    assert (
        callback2_count.value == 0
    ), "callback2 is never triggered, even on initial load"

    # double check that output1 and output2 children were not updated
    assert dash_duo.find_element("#output1").text == initial_output
    assert dash_duo.find_element("#output2").text == initial_output

    assert not dash_duo.get_logs()

    dash_duo.percy_snapshot(name="aborted")


def test_inin004_wildcard_data_attributes(dash_duo):
    app = Dash()
    test_time = datetime.datetime(2012, 1, 10, 2, 3)
    test_date = datetime.date(test_time.year, test_time.month, test_time.day)
    attrs = {
        "id": "inner-element",
        "data-string": "multiple words",
        "data-number": 512,
        "data-none": None,
        "data-date": test_date,
        "aria-progress": 5,
    }
    app.layout = html.Div([html.Div(**attrs)], id="data-element")

    dash_duo.start_server(app)

    div = dash_duo.find_element("#data-element")

    # attribute order is ill-defined - BeautifulSoup will sort them
    actual = BeautifulSoup(div.get_attribute("innerHTML"), "lxml").decode()
    expected = BeautifulSoup(
        "<div "
        + " ".join('{}="{!s}"'.format(k, v) for k, v in attrs.items() if v is not None)
        + "></div>",
        "lxml",
    ).decode()

    assert actual == expected, "all attrs are included except None values"

    assert not dash_duo.get_logs()


def test_inin005_no_props_component(dash_duo):
    app = Dash()
    app.layout = html.Div(
        [
            dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
                """
            <h1>No Props Component</h1>
        """
            )
        ]
    )

    dash_duo.start_server(app)

    assert not dash_duo.get_logs()
    dash_duo.percy_snapshot(name="no-props-component")


def test_inin006_flow_component(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            dash_flow_example.ExampleReactComponent(
                id="react", value="my-value", label="react component"
            ),
            dash_flow_example.ExampleFlowComponent(
                id="flow", value="my-value", label="flow component"
            ),
            html.Hr(),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"), [Input("react", "value"), Input("flow", "value")]
    )
    def display_output(react_value, flow_value):
        return html.Div(
            [
                "You have entered {} and {}".format(react_value, flow_value),
                html.Hr(),
                html.Label("Flow Component Docstring"),
                html.Pre(dash_flow_example.ExampleFlowComponent.__doc__),
                html.Hr(),
                html.Label("React PropTypes Component Docstring"),
                html.Pre(dash_flow_example.ExampleReactComponent.__doc__),
                html.Div(id="waitfor"),
            ]
        )

    dash_duo.start_server(app)
    dash_duo.wait_for_element("#waitfor")
    dash_duo.percy_snapshot(name="flowtype")


def test_inin007_meta_tags(dash_duo):
    metas = [
        {"name": "description", "content": "my dash app"},
        {"name": "custom", "content": "customized"},
    ]

    app = Dash(meta_tags=metas)

    app.layout = html.Div(id="content")

    dash_duo.start_server(app)

    meta = dash_duo.find_elements("meta")

    # -2 for the meta charset and http-equiv.
    assert len(meta) == len(metas) + 2, "Should have 2 extra meta tags"

    for i in range(2, len(meta)):
        meta_tag = meta[i]
        meta_info = metas[i - 2]
        assert meta_tag.get_attribute("name") == meta_info["name"]
        assert meta_tag.get_attribute("content") == meta_info["content"]


def test_inin008_index_customization(dash_duo):
    app = Dash()

    app.index_string = """<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            <div id="custom-header">My custom header</div>
            <div id="add"></div>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
            <div id="custom-footer">My custom footer</div>
            <script>
            // Test the formatting doesn"t mess up script tags.
            var elem = document.getElementById('add');
            if (!elem) {
                throw Error('could not find container to add');
            }
            elem.innerHTML = 'Got added';
            var config = {};
            fetch('/nonexist').then(r => r.json())
                .then(r => config = r).catch(err => ({config}));
            </script>
        </body>
    </html>"""

    app.layout = html.Div("Dash app", id="app")

    dash_duo.start_server(app)

    assert dash_duo.find_element("#custom-header").text == "My custom header"
    assert dash_duo.find_element("#custom-footer").text == "My custom footer"
    assert dash_duo.wait_for_element("#add").text == "Got added"

    dash_duo.percy_snapshot("custom-index")


def test_inin009_invalid_index_string(dash_duo):
    app = Dash()

    def will_raise():
        app.index_string = """<!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
            </head>
            <body>
                <div id="custom-header">My custom header</div>
                <div id="add"></div>
                <footer>
                </footer>
            </body>
        </html>"""

    with pytest.raises(Exception) as err:
        will_raise()

    exc_msg = str(err.value)
    assert "{%app_entry%}" in exc_msg
    assert "{%config%}" in exc_msg
    assert "{%scripts%}" in exc_msg

    app.layout = html.Div("Hello World", id="a")

    dash_duo.start_server(app)
    assert dash_duo.find_element("#a").text == "Hello World"


def test_inin010_func_layout_accepted(dash_duo):
    app = Dash()

    def create_layout():
        return html.Div("Hello World", id="a")

    app.layout = create_layout

    dash_duo.start_server(app)
    assert dash_duo.find_element("#a").text == "Hello World"


def test_inin012_multi_output_no_update(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("B", "btn"),
            html.P("initial1", "n1"),
            html.P("initial2", "n2"),
            html.P("initial3", "n3"),
        ]
    )

    @app.callback(
        [Output("n1", "children"), Output("n2", "children"), Output("n3", "children")],
        [Input("btn", "n_clicks")],
    )
    def show_clicks(n):
        # partial or complete cancelation of updates via no_update
        return [
            no_update if n and n > 4 else n,
            no_update if n and n > 2 else n,
            # make a new instance, to mock up caching and restoring no_update
            copy(no_update),
        ]

    dash_duo.start_server(app)

    dash_duo.multiple_click("#btn", 10)

    dash_duo.wait_for_text_to_equal("#n1", "4")
    dash_duo.wait_for_text_to_equal("#n2", "2")
    dash_duo.wait_for_text_to_equal("#n3", "initial3")


def test_inin013_no_update_chains(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="a_in", value="a"),
            dcc.Input(id="b_in", value="b"),
            html.P("", id="a_out"),
            html.P("", id="a_out_short"),
            html.P("", id="b_out"),
            html.P("", id="ab_out"),
        ]
    )

    @app.callback(
        [Output("a_out", "children"), Output("a_out_short", "children")],
        [Input("a_in", "value")],
    )
    def a_out(a):
        return a, a if len(a) < 3 else no_update

    @app.callback(Output("b_out", "children"), [Input("b_in", "value")])
    def b_out(b):
        return b

    @app.callback(
        Output("ab_out", "children"),
        [Input("a_out_short", "children")],
        [State("b_out", "children")],
    )
    def ab_out(a, b):
        return a + " " + b

    dash_duo.start_server(app)

    a_in = dash_duo.find_element("#a_in")
    b_in = dash_duo.find_element("#b_in")

    b_in.send_keys("b")
    a_in.send_keys("a")
    dash_duo.wait_for_text_to_equal("#a_out", "aa")
    dash_duo.wait_for_text_to_equal("#b_out", "bb")
    dash_duo.wait_for_text_to_equal("#a_out_short", "aa")
    dash_duo.wait_for_text_to_equal("#ab_out", "aa bb")

    b_in.send_keys("b")
    a_in.send_keys("a")
    dash_duo.wait_for_text_to_equal("#a_out", "aaa")
    dash_duo.wait_for_text_to_equal("#b_out", "bbb")
    dash_duo.wait_for_text_to_equal("#a_out_short", "aa")
    # ab_out has not been triggered because a_out_short received no_update
    dash_duo.wait_for_text_to_equal("#ab_out", "aa bb")

    b_in.send_keys("b")
    a_in.send_keys(Keys.END)
    a_in.send_keys(Keys.BACKSPACE)
    dash_duo.wait_for_text_to_equal("#a_out", "aa")
    dash_duo.wait_for_text_to_equal("#b_out", "bbbb")
    dash_duo.wait_for_text_to_equal("#a_out_short", "aa")
    # now ab_out *is* triggered - a_out_short got a new value
    # even though that value is the same as the last value it got
    dash_duo.wait_for_text_to_equal("#ab_out", "aa bbbb")


def test_inin014_with_custom_renderer(dash_duo):
    app = Dash(__name__)

    app.index_string = """<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            <div>Testing custom DashRenderer</div>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                <script id="_dash-renderer" type="application/javascript">
                    console.log('firing up a custom renderer!')
                    const renderer = new DashRenderer({
                        request_pre: () => {
                            var output = document.getElementById('output-pre')
                            if(output) {
                                output.innerHTML = 'request_pre!!!';
                            }
                        },
                        request_post: () => {
                            var output = document.getElementById('output-post')
                            if(output) {
                                output.innerHTML = 'request_post ran!';
                            }
                        }
                    })
                </script>
            </footer>
            <div>With request hooks</div>
        </body>
    </html>"""

    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(
                html.Div(
                    [
                        html.Div(id="output-1"),
                        html.Div(id="output-pre"),
                        html.Div(id="output-post"),
                    ]
                )
            ),
        ]
    )

    @app.callback(Output("output-1", "children"), [Input("input", "value")])
    def update_output(value):
        return value

    dash_duo.start_server(app)

    input1 = dash_duo.find_element("#input")
    dash_duo.clear_input(input1)

    input1.send_keys("fire request hooks")

    dash_duo.wait_for_text_to_equal("#output-1", "fire request hooks")
    assert dash_duo.find_element("#output-pre").text == "request_pre!!!"
    assert dash_duo.find_element("#output-post").text == "request_post ran!"

    dash_duo.percy_snapshot(name="request-hooks intg")


def test_inin015_with_custom_renderer_interpolated(dash_duo):

    renderer = """
        <script id="_dash-renderer" type="application/javascript">
            console.log('firing up a custom renderer!')
            const renderer = new DashRenderer({
                request_pre: () => {
                    var output = document.getElementById('output-pre')
                    if(output) {
                        output.innerHTML = 'request_pre was here!';
                    }
                },
                request_post: () => {
                    var output = document.getElementById('output-post')
                    if(output) {
                        output.innerHTML = 'request_post!!!';
                    }
                }
            })
        </script>
    """

    class CustomDash(Dash):
        def interpolate_index(self, **kwargs):
            return """<!DOCTYPE html>
            <html>
                <head>
                    <title>My App</title>
                </head>
                <body>

                    <div id="custom-header">My custom header</div>
                    {app_entry}
                    {config}
                    {scripts}
                    {renderer}
                    <div id="custom-footer">My custom footer</div>
                </body>
            </html>""".format(
                app_entry=kwargs["app_entry"],
                config=kwargs["config"],
                scripts=kwargs["scripts"],
                renderer=renderer,
            )

    app = CustomDash()

    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(
                html.Div(
                    [
                        html.Div(id="output-1"),
                        html.Div(id="output-pre"),
                        html.Div(id="output-post"),
                    ]
                )
            ),
        ]
    )

    @app.callback(Output("output-1", "children"), [Input("input", "value")])
    def update_output(value):
        return value

    dash_duo.start_server(app)

    input1 = dash_duo.find_element("#input")
    dash_duo.clear_input(input1)

    input1.send_keys("fire request hooks")

    dash_duo.wait_for_text_to_equal("#output-1", "fire request hooks")
    assert dash_duo.find_element("#output-pre").text == "request_pre was here!"
    assert dash_duo.find_element("#output-post").text == "request_post!!!"

    dash_duo.percy_snapshot(name="request-hooks interpolated")


def test_inin017_late_component_register(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [html.Button("Click me to put a dcc ", id="btn-insert"), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), [Input("btn-insert", "n_clicks")])
    def update_output(value):
        if value is None:
            raise PreventUpdate

        return dcc.Input(id="inserted-input")

    dash_duo.start_server(app)

    btn = dash_duo.find_element("#btn-insert")
    btn.click()

    dash_duo.find_element("#inserted-input")


def test_inin019_callback_dep_types():
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Div("child", id="in"), html.Div("state", id="state"), html.Div(id="out")]
    )

    with pytest.raises(IncorrectTypeException):

        @app.callback([[Output("out", "children")]], [Input("in", "children")])
        def f(i):
            return i

        pytest.fail("extra output nesting")

    with pytest.raises(IncorrectTypeException):

        @app.callback(Output("out", "children"), Input("in", "children"))
        def f2(i):
            return i

        pytest.fail("un-nested input")

    with pytest.raises(IncorrectTypeException):

        @app.callback(
            Output("out", "children"),
            [Input("in", "children")],
            State("state", "children"),
        )
        def f3(i):
            return i

        pytest.fail("un-nested state")

    # all OK with tuples
    @app.callback(
        (Output("out", "children"),),
        (Input("in", "children"),),
        (State("state", "children"),),
    )
    def f4(i):
        return i


def test_inin020_callback_return_validation():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="a"),
            html.Div(id="b"),
            html.Div(id="c"),
            html.Div(id="d"),
            html.Div(id="e"),
            html.Div(id="f"),
        ]
    )

    @app.callback(Output("b", "children"), [Input("a", "children")])
    def single(a):
        return set([1])

    with pytest.raises(InvalidCallbackReturnValue):
        # outputs_list (normally callback_context.outputs_list) is provided
        # by the dispatcher from the request.
        single("aaa", outputs_list={"id": "b", "property": "children"})
        pytest.fail("not serializable")

    @app.callback(
        [Output("c", "children"), Output("d", "children")], [Input("a", "children")]
    )
    def multi(a):
        return [1, set([2])]

    with pytest.raises(InvalidCallbackReturnValue):
        outputs_list = [
            {"id": "c", "property": "children"},
            {"id": "d", "property": "children"},
        ]
        multi("aaa", outputs_list=outputs_list)
        pytest.fail("nested non-serializable")

    @app.callback(
        [Output("e", "children"), Output("f", "children")], [Input("a", "children")]
    )
    def multi2(a):
        return ["abc"]

    with pytest.raises(InvalidCallbackReturnValue):
        outputs_list = [
            {"id": "e", "property": "children"},
            {"id": "f", "property": "children"},
        ]
        multi2("aaa", outputs_list=outputs_list)
        pytest.fail("wrong-length list")


def test_inin_024_port_env_success(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div("hi", "out")
    dash_duo.start_server(app, port="12345")
    assert dash_duo.server_url == "http://localhost:12345"
    dash_duo.wait_for_text_to_equal("#out", "hi")
