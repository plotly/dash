import pytest
from selenium.common.exceptions import WebDriverException
from dash import Dash, Input, Output, dcc, html


ALLOWED_TYPES = (
    "text",
    "number",
    "password",
    "email",
    "range",
    "search",
    "tel",
    "url",
    "hidden",
)


def test_inbs001_all_types(dash_dcc):
    def input_id(type_):
        return f"input_{type_}"

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id=input_id(_), type=_, placeholder=f"input type {_}")
            for _ in ALLOWED_TYPES
        ]
        + [html.Div(id="output")]
        + [
            dcc.Input(id=input_id(_) + "2", type=_, placeholder=f"input type {_}")
            for _ in ALLOWED_TYPES
        ]
    )

    @app.callback(
        Output("output", "children"),
        [Input(input_id(_), "value") for _ in ALLOWED_TYPES],
    )
    def cb_render(*vals):
        return " | ".join((val for val in vals if val))

    dash_dcc.start_server(app)

    assert (
        dash_dcc.find_element("#input_hidden").get_attribute("type") == "hidden"
    ), "hidden input element should present with hidden type"

    for atype in ALLOWED_TYPES[:-1]:
        dash_dcc.find_element(f"#input_{atype}").send_keys(
            f"test intp001 - input[{atype}]"
        )

    with pytest.raises(WebDriverException):
        dash_dcc.find_element("#input_hidden").send_keys("no interaction")

    dash_dcc.percy_snapshot("inbs001 - dcc callback output rendering")

    assert dash_dcc.get_logs() == []


def test_inbs002_user_class(dash_dcc):
    app = Dash(__name__, assets_folder="../../assets")

    app.layout = html.Div(className="test-input-css", children=[dcc.Input()])

    dash_dcc.start_server(app)

    dash_dcc.wait_for_style_to_equal(
        ".test-input-css input", "borderColor", "rgb(255, 105, 180)"
    )
    dash_dcc.wait_for_style_to_equal(".test-input-css input", "width", "420px")

    assert dash_dcc.get_logs() == []


def test_inbs003_styles_are_scoped(dash_dcc):
    app = Dash(__name__)

    app.index_string = """
    <html>
        <body>
            <input id="ExternalInput" required />
            {%app_entry%}
            {%config%}
            {%scripts%}
            {%renderer%}
        </body>
    </html>
    """

    app.layout = html.Div(
        className="test-input-css",
        children=[dcc.Input(id="DashInput", required=True, className="unittest")],
    )

    dash_dcc.start_server(app)

    external_input = dash_dcc.find_element("#ExternalInput")
    dash_input = dash_dcc.find_element(".unittest")

    external_outline_css = external_input.value_of_css_property("outline")
    dash_outline_css = dash_input.value_of_css_property("outline")

    assert external_outline_css != dash_outline_css
