import requests

from dash import Dash, Input, Output, html, dcc


def test_cbmf001_bad_output_outputs(dash_thread_server):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="i", value="initial value"),
            html.Div(html.Div([1.5, None, "string", html.Div(id="o1")])),
        ]
    )

    @app.callback(Output("o1", "children"), [Input("i", "value")])
    def update_output(value):
        return value

    dash_thread_server(app)

    # first a good request
    response = requests.post(
        dash_thread_server.url + "/_dash-update-component",
        json=dict(
            output="o1.children",
            outputs={"id": "o1", "property": "children"},
            inputs=[{"id": "i", "property": "value", "value": 9}],
            changedPropIds=["i.value"],
        ),
    )
    assert response.status_code == 200
    assert '"o1":{"children":9}' in response.text

    # now some bad ones
    outspecs = [
        {"output": "o1.nope", "outputs": {"id": "o1", "property": "nope"}},
        {"output": "o1.children", "outputs": {"id": "o1", "property": "nope"}},
        {"output": "o1.nope", "outputs": {"id": "o1", "property": "children"}},
        {"output": "o1.children", "outputs": {"id": "nope", "property": "children"}},
        {"output": "nope.children", "outputs": {"id": "nope", "property": "children"}},
    ]
    for outspeci in outspecs:
        response = requests.post(
            dash_thread_server.url + "/_dash-update-component",
            json=dict(
                inputs=[{"id": "i", "property": "value", "value": 9}],
                changedPropIds=["i.value"],
                **outspeci
            ),
        )
        assert response.status_code == 500
        assert "o1" not in response.text
        assert "children" not in response.text
        assert "nope" not in response.text
        assert "500 Internal Server Error" in response.text
