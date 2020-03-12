import time
import pytest

import dash_html_components as html
import dash_core_components as dcc

from dash import Dash

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from selenium.webdriver.common.by import By


def findSyncPlotlyJs(scripts):
    for script in scripts:
        if "dash_core_components/plotly" in script.get_attribute("src"):
            return script


def findAsyncPlotlyJs(scripts):
    for script in scripts:
        if "dash_core_components/async-plotlyjs" in script.get_attribute("src"):
            return script


@pytest.mark.parametrize("is_eager", [True, False])
def test_scripts(dash_duo, is_eager):
    app = Dash(__name__, eager_loading=is_eager)
    app.layout = html.Div([dcc.Graph(id="output", figure={"data": [{"y": [3, 1, 2]}]})])

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    # Give time for the async dependency to be requested (if any)
    time.sleep(2)

    scripts = dash_duo.driver.find_elements(By.CSS_SELECTOR, "script")

    assert (findSyncPlotlyJs(scripts) is None) is not is_eager
    assert (findAsyncPlotlyJs(scripts) is None) is is_eager


def test_scripts_on_request(dash_duo):
    app = Dash(__name__, eager_loading=False)
    app.layout = html.Div(id="div", children=[html.Button(id="btn")])

    @app.callback(Output("div", "children"), [Input("btn", "n_clicks")])
    def load_chart(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        return dcc.Graph(id="output", figure={"data": [{"y": [3, 1, 2]}]})

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    # Give time for the async dependency to be requested (if any)
    time.sleep(2)

    scripts = dash_duo.driver.find_elements(By.CSS_SELECTOR, "script")
    assert findSyncPlotlyJs(scripts) is None
    assert findAsyncPlotlyJs(scripts) is None

    dash_duo.find_element("#btn").click()

    # Give time for the async dependency to be requested (if any)
    time.sleep(2)

    scripts = dash_duo.driver.find_elements(By.CSS_SELECTOR, "script")
    assert findSyncPlotlyJs(scripts) is None
    assert findAsyncPlotlyJs(scripts) is not None
