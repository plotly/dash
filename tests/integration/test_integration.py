import datetime
import flask
import json
import pytest

from bs4 import BeautifulSoup

import dash_dangerously_set_inner_html
import dash_flow_example

import dash_html_components as html
import dash_core_components as dcc

from dash import Dash

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


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
            // Test the formatting doesn't mess up script tags.
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


def test_inin_024_port_env_success(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div("hi", "out")
    dash_duo.start_server(app, port="12345")
    assert dash_duo.server_url == "http://localhost:12345"
    dash_duo.wait_for_text_to_equal("#out", "hi")


def nested_app(server, path, text):
    app = Dash(__name__, server=server, url_base_pathname=path)
    app.layout = html.Div(id="out")

    @app.callback(Output("out", "children"), [Input("out", "n_clicks")])
    def out(n):
        return text

    return app


def test_inin025_url_base_pathname(dash_br, dash_thread_server):
    server = flask.Flask(__name__)
    app = nested_app(server, "/app1/", "The first")
    nested_app(server, "/app2/", "The second")

    dash_thread_server(app)

    dash_br.server_url = "http://localhost:8050/app1/"
    dash_br.wait_for_text_to_equal("#out", "The first")

    dash_br.server_url = "http://localhost:8050/app2/"
    dash_br.wait_for_text_to_equal("#out", "The second")


def test_inin026_graphs_in_tabs_do_not_share_state(dash_duo):
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            dcc.Tabs(
                id="tabs",
                children=[
                    dcc.Tab(label="Tab 1", value="tab1", id="tab1"),
                    dcc.Tab(label="Tab 2", value="tab2", id="tab2"),
                ],
                value="tab1",
            ),
            # Tab content
            html.Div(id="tab_content"),
        ]
    )
    tab1_layout = [
        html.Div(
            [
                dcc.Graph(
                    id="graph1",
                    figure={"data": [{"x": [1, 2, 3], "y": [5, 10, 6], "type": "bar"}]},
                )
            ]
        ),
        html.Pre(id="graph1_info"),
    ]

    tab2_layout = [
        html.Div(
            [
                dcc.Graph(
                    id="graph2",
                    figure={"data": [{"x": [4, 3, 2], "y": [5, 10, 6], "type": "bar"}]},
                )
            ]
        ),
        html.Pre(id="graph2_info"),
    ]

    @app.callback(Output("graph1_info", "children"), Input("graph1", "clickData"))
    def display_hover_data(hover_data):
        return json.dumps(hover_data)

    @app.callback(Output("graph2_info", "children"), Input("graph2", "clickData"))
    def display_hover_data_2(hover_data):
        return json.dumps(hover_data)

    @app.callback(Output("tab_content", "children"), Input("tabs", "value"))
    def render_content(tab):
        return tab2_layout if tab == "tab2" else tab1_layout

    dash_duo.start_server(app)

    dash_duo.find_element("#graph1:not(.dash-graph--pending)").click()

    graph_1_expected_clickdata = {
        "points": [
            {
                "curveNumber": 0,
                "pointNumber": 1,
                "pointIndex": 1,
                "x": 2,
                "y": 10,
                "label": 2,
                "value": 10,
            }
        ]
    }

    graph_2_expected_clickdata = {
        "points": [
            {
                "curveNumber": 0,
                "pointNumber": 1,
                "pointIndex": 1,
                "x": 3,
                "y": 10,
                "label": 3,
                "value": 10,
            }
        ]
    }

    dash_duo.wait_for_text_to_equal(
        "#graph1_info", json.dumps(graph_1_expected_clickdata)
    )

    dash_duo.find_element("#tab2").click()

    dash_duo.find_element("#graph2:not(.dash-graph--pending)").click()

    dash_duo.wait_for_text_to_equal(
        "#graph2_info", json.dumps(graph_2_expected_clickdata)
    )
