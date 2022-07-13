import datetime
import flask
import json
import pytest
import re

from bs4 import BeautifulSoup

import dash_dangerously_set_inner_html
import dash_flow_example

import dash
from dash import Dash, html, dcc, Input, Output
from dash.exceptions import PreventUpdate

from dash.testing.wait import until


def test_inin003_wildcard_data_attributes(dash_duo):
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

    assert dash_duo.get_logs() == []


def test_inin004_no_props_component(dash_duo):
    app = Dash()
    app.layout = html.Div(
        [
            dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
                """
            <h1>No Props Component</h1>
        """
            )
        ],
        id="app",
    )

    dash_duo.start_server(app)

    assert dash_duo.get_logs() == []
    assert dash_duo.find_element("h1").text == "No Props Component"

    inner = dash_duo.find_element("#app").get_property("innerHTML")
    expected = "<div> <h1>No Props Component</h1> </div>"
    assert re.sub("\\s+", " ", inner) == expected


def test_inin005_flow_component(dash_duo):
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


def test_inin006_meta_tags(dash_duo):
    metas = [
        {"name": "description", "content": "my dash app"},
        {"name": "custom", "content": "customized"},
    ]

    app = Dash(meta_tags=metas)

    app.layout = html.Div(id="content")

    dash_duo.start_server(app)

    meta = dash_duo.find_elements("meta")

    # -3 for the meta charset, http-equiv and viewport.
    assert len(meta) == len(metas) + 3, "Should have 3 extra meta tags"

    for i in range(3, len(meta)):
        meta_tag = meta[i]
        meta_info = metas[i - 3]
        assert meta_tag.get_attribute("name") == meta_info["name"]
        assert meta_tag.get_attribute("content") == meta_info["content"]


def test_inin007_change_viewport_meta_tag(dash_duo):
    """
    As of dash 2.5 the default viewport meta tag is:
        [{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
    Test verifies that this feature can be disabled by using an empty viewport tag.
    """

    app = Dash(meta_tags=[{"name": "viewport"}])

    app.layout = html.Div(id="content")

    dash_duo.start_server(app)

    viewport_meta = dash_duo.find_elements('meta[name="viewport"]')

    assert len(viewport_meta) == 1, "Should have 1 viewport meta tags"
    assert viewport_meta[0].get_attribute("content") == ""


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
    assert dash_duo.find_element("#app").text == "Dash app"
    assert dash_duo.wait_for_element("#add").text == "Got added"

    assert dash_duo.get_logs() == []


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

    dash_br.server_url = "http://localhost:{}/app1/".format(dash_thread_server.port)
    dash_br.wait_for_text_to_equal("#out", "The first")

    dash_br.server_url = "http://localhost:{}/app2/".format(dash_thread_server.port)
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

    until(lambda: '"label": 2' in dash_duo.find_element("#graph1_info").text, timeout=3)

    dash_duo.find_element("#tab2").click()

    dash_duo.find_element("#graph2:not(.dash-graph--pending)").click()

    until(lambda: '"label": 3' in dash_duo.find_element("#graph2_info").text, timeout=3)


def test_inin027_multi_page_without_pages_folder(dash_duo):
    app = Dash(__name__, pages_folder="")

    # test for storing arbitrary keyword arguments: An `id` prop is defined for every page
    # test for defining multiple pages within a single file: layout is passed directly to `register_page`
    # in the following two modules:
    dash.register_page(
        "multi_layout1",
        layout=html.Div("text for multi_layout1", id="text_multi_layout1"),
        path="/",
        title="Supplied Title",
        description="This is the supplied description",
        name="Supplied name",
        image="birds.jpeg",
        id="multi_layout1",
    )
    dash.register_page(
        "multi_layout2",
        layout=html.Div("text for multi_layout2", id="text_multi_layout2"),
        path="/layout2",
        id="multi_layout2",
    )

    dash.register_page(
        "not_found_404",
        layout=html.Div("text for not_found_404", id="text_not_found_404"),
        id="not_found_404",
    )

    app.layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        dcc.Link(
                            f"{page['name']} - {page['path']}",
                            id=page["id"],
                            href=page["path"],
                        )
                    )
                    for page in dash.page_registry.values()
                ]
            ),
            dash.page_container,
        ]
    )

    dash_duo.start_server(app)
    # test layout and title for each page in `page_registry` with link navigation
    for page in dash.page_registry.values():
        dash_duo.find_element("#" + page["id"]).click()
        dash_duo.wait_for_text_to_equal("#text_" + page["id"], "text for " + page["id"])
        assert dash_duo.driver.title == page["title"], "check that page title updates"

    # test registration of not_found_404
    assert "not_found_404" in dash.page_registry.keys(), "check custom not_found_404"

    # clean up so this page doesn't affect other tests
    del dash.page_registry["not_found_404"]

    assert not dash_duo.get_logs()
