import werkzeug

from dash import Dash, Input, Output, dcc, html
from dash.exceptions import PreventUpdate
import json
import os
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time


@pytest.mark.parametrize("is_eager", [True, False])
def test_tagr001_graph_does_not_resize_in_tabs(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)
    app.layout = html.Div(
        [
            html.H1("Dash Tabs component demo"),
            dcc.Tabs(
                id="tabs-example",
                value="tab-1-example",
                children=[
                    dcc.Tab(label="Tab One", value="tab-1-example", id="tab-1"),
                    dcc.Tab(label="Tab Two", value="tab-2-example", id="tab-2"),
                    dcc.Tab(
                        label="Tab Three",
                        value="tab-3-example",
                        id="tab-3",
                        disabled=True,
                        disabled_className="disabled-tab",
                    ),
                ],
            ),
            html.Div(id="tabs-content-example"),
        ]
    )

    @app.callback(
        Output("tabs-content-example", "children"),
        [Input("tabs-example", "value")],
    )
    def render_content(tab):
        if tab == "tab-1-example":
            return html.Div(
                [
                    html.H3("Tab content 1"),
                    dcc.Graph(
                        id="graph-1-tabs",
                        figure={
                            "data": [{"x": [1, 2, 3], "y": [3, 1, 2], "type": "bar"}]
                        },
                    ),
                ]
            )
        elif tab == "tab-2-example":
            return html.Div(
                [
                    html.H3("Tab content 2"),
                    dcc.Graph(
                        id="graph-2-tabs",
                        figure={
                            "data": [{"x": [1, 2, 3], "y": [5, 10, 6], "type": "bar"}]
                        },
                    ),
                ]
            )

    dash_dcc.start_server(app)

    tab_one = dash_dcc.wait_for_element("#tab-1")
    tab_two = dash_dcc.wait_for_element("#tab-2")

    # wait for disabled tab with custom className
    dash_dcc.wait_for_element("#tab-3.disabled-tab")

    WebDriverWait(dash_dcc.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "tab-2"))
    )

    # wait for Graph to be ready
    WebDriverWait(dash_dcc.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph-1-tabs .main-svg"))
    )

    is_eager = "eager" if is_eager else "lazy"

    dash_dcc.percy_snapshot(
        f"Tabs with Graph - initial (graph should not resize) ({is_eager})"
    )
    tab_two.click()

    # wait for Graph to be ready
    WebDriverWait(dash_dcc.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph-2-tabs .main-svg"))
    )

    dash_dcc.percy_snapshot(
        f"Tabs with Graph - clicked tab 2 (graph should not resize) ({is_eager})"
    )

    WebDriverWait(dash_dcc.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "tab-1"))
    )

    tab_one.click()

    # wait for Graph to be loaded after clicking
    WebDriverWait(dash_dcc.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph-1-tabs .main-svg"))
    )

    dash_dcc.percy_snapshot(
        f"Tabs with Graph - clicked tab 1 (graph should not resize) ({is_eager})"
    )

    assert dash_dcc.get_logs() == []


@pytest.mark.xfail(
    condition=werkzeug.__version__ in ("2.1.0", "2.1.1"),
    reason="Bug with 204 and Transfer-Encoding",
    strict=False,
)
@pytest.mark.parametrize("is_eager", [True, False])
def test_tagr002_tabs_render_without_selected(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)

    menu = html.Div([html.Div("one", id="one"), html.Div("two", id="two")])

    tabs_one = html.Div(
        [dcc.Tabs([dcc.Tab(dcc.Graph(id="graph-one"), label="tab-one-one")])],
        id="tabs-one",
        style={"display": "none"},
    )

    tabs_two = html.Div(
        [dcc.Tabs([dcc.Tab(dcc.Graph(id="graph-two"), label="tab-two-one")])],
        id="tabs-two",
        style={"display": "none"},
    )

    app.layout = html.Div([menu, tabs_one, tabs_two])

    for i in ("one", "two"):

        @app.callback(Output(f"tabs-{i}", "style"), [Input(i, "n_clicks")])
        def on_click_update_tabs(n_clicks):
            if n_clicks is None:
                raise PreventUpdate

            if n_clicks % 2 == 1:
                return {"display": "block"}
            return {"display": "none"}

        @app.callback(Output(f"graph-{i}", "figure"), [Input(i, "n_clicks")])
        def on_click_update_graph(n_clicks):
            if n_clicks is None:
                raise PreventUpdate

            return {
                "data": [{"x": [1, 2, 3, 4], "y": [4, 3, 2, 1]}],
                "layout": {"width": 700, "height": 450},
            }

    dash_dcc.start_server(app)

    button_one = dash_dcc.wait_for_element("#one")
    button_two = dash_dcc.wait_for_element("#two")

    button_one.click()

    # wait for tabs to be loaded after clicking
    WebDriverWait(dash_dcc.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph-one .main-svg"))
    )

    is_eager = "eager" if is_eager else "lazy"

    time.sleep(1)
    dash_dcc.percy_snapshot(f"Tabs-1 rendered ({is_eager})")

    button_two.click()

    # wait for tabs to be loaded after clicking
    WebDriverWait(dash_dcc.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph-two .main-svg"))
    )

    time.sleep(1)
    dash_dcc.percy_snapshot(f"Tabs-2 rendered ({is_eager})")

    # do some extra tests while we're here
    # and have access to Graph and plotly.js
    check_graph_config_shape(dash_dcc)

    assert dash_dcc.get_logs() == []


def check_graph_config_shape(dash_dcc):
    config_schema = dash_dcc.driver.execute_script(
        "return Plotly.PlotSchema.get().config;"
    )
    with open(os.path.join(dcc.__path__[0], "metadata.json")) as meta:
        graph_meta = json.load(meta)["src/components/Graph.react.js"]
        config_prop_shape = graph_meta["props"]["config"]["type"]["value"]

    ignored_config = [
        "setBackground",
        "showSources",
        "logging",
        "globalTransforms",
        "notifyOnLogging",
        "role",
        "typesetMath",
    ]

    def crawl(schema, props):
        for prop_name in props:
            assert prop_name in schema

        for item_name, item in schema.items():
            if item_name in ignored_config:
                continue

            assert item_name in props
            if "valType" not in item:
                crawl(item, props[item_name]["value"])

    crawl(config_schema, config_prop_shape)

    assert dash_dcc.get_logs() == []
