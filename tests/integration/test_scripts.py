import time
import pytest

from dash import Dash, Input, Output, html, dcc
from dash.exceptions import PreventUpdate


def get_script_sources(dash_duo):
    return [s.get_attribute("src") for s in dash_duo.find_elements("script")]


def hasWindowPlotly(dash_duo):
    return dash_duo.driver.execute_script("return !!window.Plotly")


@pytest.mark.parametrize("is_eager", [True, False])
def test_scri001_scripts(dash_duo, is_eager):
    app = Dash(__name__, eager_loading=is_eager)
    app.layout = html.Div([dcc.Graph(id="output", figure={"data": [{"y": [3, 1, 2]}]})])

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    assert hasWindowPlotly(dash_duo) is is_eager

    # Wait for the graph to appear
    dash_duo.find_element(".js-plotly-plot")

    assert hasWindowPlotly(dash_duo) is True


def test_scri002_scripts_on_request(dash_duo):
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

    assert hasWindowPlotly(dash_duo) is False

    dash_duo.find_element("#btn").click()

    # Wait for the graph to appear
    dash_duo.find_element(".js-plotly-plot")

    assert hasWindowPlotly(dash_duo) is True
