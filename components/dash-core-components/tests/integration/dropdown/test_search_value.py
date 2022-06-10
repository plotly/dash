from dash import Dash, Input, Output, dcc, html


def test_ddsv001_search_value(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [dcc.Dropdown(id="dropdown", search_value="something"), html.Div(id="output")]
    )

    @app.callback(
        Output("output", "children"), inputs=[Input("dropdown", "search_value")]
    )
    def update_output(search_value):
        return f'search_value="{search_value}"'

    dash_duo.start_server(app)

    # Get the inner input used for search value.
    input_ = dash_duo.find_element("#dropdown input")

    dash_duo.wait_for_text_to_equal("#output", 'search_value="something"')

    input_.send_keys("x")
    dash_duo.wait_for_text_to_equal("#output", 'search_value="x"')

    assert dash_duo.get_logs() == []
