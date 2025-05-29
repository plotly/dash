from dash import Dash, Input, Output, dcc, html


def test_tabs001_in_vertical_mode(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Tabs(
                id="tabs",
                value="tab-3",
                children=[
                    dcc.Tab(
                        label="Tab one",
                        value="tab-1",
                        id="tab-1",
                        children=[html.Div("Tab One Content")],
                    ),
                    dcc.Tab(
                        label="Tab two",
                        value="tab-2",
                        id="tab-2",
                        children=[html.Div("Tab Two Content")],
                    ),
                    dcc.Tab(
                        label="Tab three",
                        value="tab-3",
                        id="tab-3",
                        children=[html.Div("Tab Three Content")],
                    ),
                ],
                vertical=True,
            ),
            html.Div(id="tabs-content"),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#tab-3", "Tab three")
    dash_dcc.percy_snapshot("Core Tabs - vertical mode")
    assert dash_dcc.get_logs() == []


def test_tabs002_without_children(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.H1("Dash Tabs component demo"),
            dcc.Tabs(
                id="tabs",
                value="tab-2",
                children=[
                    dcc.Tab(label="Tab one", value="tab-1", id="tab-1"),
                    dcc.Tab(label="Tab two", value="tab-2", id="tab-2"),
                ],
            ),
            html.Div(id="tabs-content"),
        ]
    )

    @app.callback(
        Output("tabs-content", "children"),
        [Input("tabs", "value")],
    )
    def render_content(tab):
        if tab == "tab-1":
            return html.Div([html.H3("Test content 1")], id="test-tab-1")
        elif tab == "tab-2":
            return html.Div([html.H3("Test content 2")], id="test-tab-2")

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#tabs-content", "Test content 2")
    dash_dcc.percy_snapshot("Core initial tab - tab 2")

    dash_dcc.wait_for_element("#tab-1").click()
    dash_dcc.wait_for_text_to_equal("#tabs-content", "Test content 1")
    assert dash_dcc.get_logs() == []


def test_tabs003_without_children_undefined(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.H1("Dash Tabs component demo"),
            dcc.Tabs(id="tabs", value="tab-1"),
            html.Div(id="tabs-content"),
        ],
        id="app",
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#tabs-content")
    assert dash_dcc.find_element("#app").text == "Dash Tabs component demo"
    assert dash_dcc.find_element(".tab-content").get_property("innerHTML") == ""
    assert dash_dcc.find_element("#tabs").get_property("innerHTML") == ""
    assert dash_dcc.find_element("#tabs-content").get_property("innerHTML") == ""
    assert dash_dcc.get_logs() == []


def test_tabs004_without_value(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H1("Dash Tabs component demo"),
            dcc.Tabs(
                id="tabs-without-value",
                children=[
                    dcc.Tab(label="Tab One", value="tab-1"),
                    dcc.Tab(label="Tab Two", value="tab-2"),
                ],
            ),
            html.Div(id="tabs-content"),
        ]
    )

    @app.callback(
        Output("tabs-content", "children"), [Input("tabs-without-value", "value")]
    )
    def render_content(tab):
        if tab == "tab-1":
            return html.H3("Default selected Tab content 1")
        elif tab == "tab-2":
            return html.H3("Tab content 2")

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#tabs-content", "Default selected Tab content 1")
    assert dash_dcc.get_logs() == []


def test_tabs005_disabled(dash_dcc):
    app = Dash(__name__, assets_folder="../../assets")
    app.layout = html.Div(
        [
            html.H1("Dash Tabs component with disabled tab demo"),
            dcc.Tabs(
                id="tabs-example",
                value="tab-2",
                children=[
                    dcc.Tab(
                        label="Disabled Tab",
                        value="tab-1",
                        id="tab-1",
                        className="test-custom-tab",
                        disabled=True,
                    ),
                    dcc.Tab(
                        label="Active Tab",
                        value="tab-2",
                        id="tab-2",
                        className="test-custom-tab",
                    ),
                ],
            ),
            html.Div(id="tabs-content-example"),
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_element("#tab-2")
    dash_dcc.wait_for_element(".tab--disabled")
    assert dash_dcc.get_logs() == []
