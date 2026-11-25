import pytest
from dash import Dash, Input, Output, dcc, html


@pytest.mark.parametrize("nested", [False, True], ids=["consecutive", "nested"])
def test_grls001_consecutive_relayouts(dash_duo, nested):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Replace figure", id="replace"),
            dcc.Graph(
                id="graph",
                figure={
                    "data": [{"y": [-8, 3, 16, 5]}],
                    "layout": {"width": 600, "height": 400},
                },
            ),
        ]
    )

    @app.callback(
        Output("graph", "figure"),
        Input("replace", "n_clicks"),
        prevent_initial_call=True,
    )
    def replace(_):
        return {
            "data": [{"y": [10, 11, 12, 13]}],
            "layout": {
                "width": 600,
                "height": 400,
                "title": {"text": "Replacement"},
                "yaxis": {"range": [9, 14]},
            },
        }

    dash_duo.start_server(app)
    dash_duo.wait_for_element("#graph .main-svg")
    dash_duo.driver.execute_async_script(
        """
        const nested = arguments[0];
        const done = arguments[arguments.length - 1];
        const gd = document.querySelector('#graph .js-plotly-plot');
        if (nested) {
            gd.once('plotly_relayout', () => {
                Plotly.relayout(gd, {'xaxis.range': [0, 1]});
            });
        }
        Plotly.relayout(gd, {'yaxis.range': [0, 5]});
        if (!nested) {
            Plotly.relayout(gd, {'xaxis.range': [0, 1]});
        }
        // Wait for the sync-triggered Plotly.react and subsequent frames.
        gd.once('plotly_afterplot', () => {
            requestAnimationFrame(() => requestAnimationFrame(done));
        });
        """,
        nested,
    )
    ranges = dash_duo.driver.execute_script(
        """
        const gd = document.querySelector('#graph .js-plotly-plot');
        const figure = window.dash_component_api.getLayout('graph').props.figure;
        return [gd._fullLayout.yaxis.range, gd._fullLayout.xaxis.range,
                figure.layout.yaxis?.range, figure.layout.xaxis?.range];
        """
    )
    assert ranges == [[0, 5], [0, 1], [0, 5], [0, 1]]

    dash_duo.find_element("#replace").click()
    dash_duo.wait_for_text_to_equal("#graph .gtitle", "Replacement")
    dash_duo.driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        const gd = document.querySelector('#graph .js-plotly-plot');
        Plotly.relayout(gd, {'xaxis.range': [1, 2]});
        gd.once('plotly_afterplot', () => {
            requestAnimationFrame(() => requestAnimationFrame(done));
        });
        """
    )
    figure = dash_duo.driver.execute_script(
        "return window.dash_component_api.getLayout('graph').props.figure;"
    )
    assert figure["data"][0]["y"] == [10, 11, 12, 13]
    assert figure["layout"]["title"]["text"] == "Replacement"
    assert figure["layout"]["yaxis"]["range"] == [9, 14]
    assert figure["layout"]["xaxis"]["range"] == [1, 2]
    assert dash_duo.get_logs() == []
