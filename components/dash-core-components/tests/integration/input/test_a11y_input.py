import pytest
from dash import Dash
from dash.dcc import Input
from dash.html import Div, Label, P

input_types = [
    "text",
    "number",
]


@pytest.mark.parametrize("input_type", input_types)
def test_a11y001_label_focuses_input(dash_duo, input_type):
    app = Dash(__name__)
    app.layout = Label(
        [
            P("Click me", id="label"),
            Input(
                type=input_type,
                id="input",
                placeholder="Testing label that wraps a input can trigger the input",
            ),
        ],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#input")

    dash_duo.find_element("#label").click()
    assert input_has_focus(dash_duo, "#input"), "Input element is not focused"

    assert dash_duo.get_logs() == []


@pytest.mark.parametrize("input_type", input_types)
def test_a11y002_label_with_htmlFor_can_focus_input(dash_duo, input_type):
    app = Dash(__name__)
    app.layout = Div(
        [
            Label("Click me", htmlFor="input", id="label"),
            Input(
                type=input_type,
                id="input",
                placeholder="Testing label with `htmlFor` triggers the dropdown",
            ),
        ],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#input")

    dash_duo.find_element("#label").click()
    assert input_has_focus(dash_duo, "#input"), "Input element is not focused"

    assert dash_duo.get_logs() == []


def input_has_focus(dash_duo, id):
    element = dash_duo.find_element(id)
    return dash_duo.driver.execute_script(
        """
        const container = arguments[0];
        const activeElement = document.activeElement;
        return container === activeElement || container.contains(activeElement);
        """,
        element,
    )
