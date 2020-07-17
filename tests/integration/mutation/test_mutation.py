# -*- coding: UTF-8 -*-from multiprocessing import Value
import pytest
import dash_html_components as html
from dash import Dash, no_update
from dash.dependencies import Input, Output, Mutation
from dash.exceptions import PreventUpdate


@pytest.mark.parametrize(
    "mutation,process_clicks",
    [
        ("base + value", lambda n_clicks: n_clicks),
        (True, lambda n_clicks: Mutation(mutation="base + value", output=n_clicks)),
    ],
)
def test_cbmu001_one_mutation(dash_duo, mutation, process_clicks):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [html.Button(id="btn", children=["Click me"]), html.Div(id="div", children=0)]
    )

    @app.callback(
        Output("div", "children", mutation),
        [Input("btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def update_div(n_clicks):
        return process_clicks(n_clicks)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#div", "0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#div", "1")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#div", "3")
    assert dash_duo.get_logs() == []


def raise_(ex):
    raise ex


@pytest.mark.parametrize("mutation", ["base + value", True])
@pytest.mark.parametrize(
    "process_clicks",
    [lambda n_clicks: no_update, lambda n_clicks: raise_(PreventUpdate)],
)
def test_cbmu002_one_mutation_none(dash_duo, mutation, process_clicks):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [html.Button(id="btn", children=["Click me"]), html.Div(id="div", children=0)]
    )

    @app.callback(
        Output("div", "children", mutation),
        [Input("btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def update_div(n_clicks):
        return process_clicks(n_clicks)

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#div", "0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#div", "0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#div", "0")
    assert dash_duo.get_logs() == []
