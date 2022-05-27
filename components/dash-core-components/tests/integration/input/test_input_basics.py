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
        return "input_{}".format(type_)

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id=input_id(_), type=_, placeholder="input type {}".format(_))
            for _ in ALLOWED_TYPES
        ]
        + [html.Div(id="output")]
        + [
            dcc.Input(
                id=input_id(_) + "2", type=_, placeholder="input type {}".format(_)
            )
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
        dash_dcc.find_element("#input_{}".format(atype)).send_keys(
            "test intp001 - input[{}]".format(atype)
        )

    with pytest.raises(WebDriverException):
        dash_dcc.find_element("#input_hidden").send_keys("no interaction")

    dash_dcc.percy_snapshot("inbs001 - dcc callback output rendering")

    assert dash_dcc.get_logs() == []


def test_inbs002_user_class(dash_dcc):
    app = Dash(__name__, assets_folder="../../assets")

    app.layout = html.Div(className="test-input-css", children=[dcc.Input()])

    dash_dcc.start_server(app)

    dash_dcc.find_element(".test-input-css")

    def get_style(attr):
        sel = "document.querySelector('.test-input-css input')"
        return dash_dcc.driver.execute_script(f"return getComputedStyle({sel}).{attr}")

    assert get_style("borderColor") == "rgb(255, 105, 180)"
    assert get_style("width") == "420px"

    assert dash_dcc.get_logs() == []
