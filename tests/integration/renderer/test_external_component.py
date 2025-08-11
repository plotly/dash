from dash import Dash, html, dcc, html, Input, Output, State, MATCH
from dash_test_components import ExternalComponent


def test_rext001_render_external_component(dash_duo):
    app = Dash()
    app.layout = html.Div(
        [
            dcc.Input(id="sync", value="synced"),
            html.Button("sync", id="sync-btn"),
            ExternalComponent(
                id="ext",
                input_id="external",
                text="external",
                extra_component={
                    "type": "Div",
                    "namespace": "dash_html_components",
                    "props": {
                        "id": "extra",
                        "children": [
                            html.Div("extra children", id={"type": "extra", "index": 1})
                        ],
                    },
                },
            ),
            ExternalComponent(
                id="without-id",
                text="without-id",
            ),
            html.Div(html.Div(id={"type": "output", "index": 1}), id="out"),
        ]
    )

    @app.callback(
        Output("ext", "text"),
        Input("sync-btn", "n_clicks"),
        State("sync", "value"),
        prevent_initial_call=True,
    )
    def on_sync(_, value):
        return value

    @app.callback(
        Output({"type": "output", "index": MATCH}, "children"),
        Input({"type": "extra", "index": MATCH}, "n_clicks"),
        prevent_initial_call=True,
    )
    def click(*_):
        return "clicked"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#external", "external")
    dash_duo.find_element("#sync-btn").click()
    dash_duo.wait_for_text_to_equal("#external", "synced")

    dash_duo.wait_for_text_to_equal("#extra", "extra children")

    dash_duo.find_element("#extra > div").click()
    dash_duo.wait_for_text_to_equal("#out", "clicked")

    assert dash_duo.get_logs() == []


def test_rext002_render_external_component_temp(dash_duo):
    app = Dash()
    app.layout = html.Div(
        [
            dcc.Tabs(
                [
                    dcc.Tab(
                        label="Tab 1",
                        children=[
                            ExternalComponent(
                                id="ext",
                                extra_component={
                                    "type": "Div",
                                    "namespace": "dash_html_components",
                                    "props": {
                                        "id": "extra",
                                        "children": [
                                            html.Div(
                                                "extra children",
                                                id={"type": "extra", "index": 1},
                                            )
                                        ],
                                    },
                                },
                                extra_component_temp=True,
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="Tab 2",
                        children=[
                            ExternalComponent(
                                id="without-id",
                                text="without-id",
                            ),
                        ],
                    ),
                ]
            ),
        ]
    )

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#extra", "extra children")

    dash_duo.find_element(".tab:nth-child(2)").click()
    assert (
        dash_duo.find_element("#without-id input").get_attribute("value")
        == "without-id"
    )

    dash_duo.find_element(".tab").click()
    dash_duo.find_element("#ext")
    assert (
        len(dash_duo.find_elements("#ext > *")) == 0
    ), "extra component should be removed"

    dash_duo.find_element(".tab:nth-child(2)").click()
    assert (
        dash_duo.find_element("#without-id input").get_attribute("value")
        == "without-id"
    )

    assert dash_duo.get_logs() == []
