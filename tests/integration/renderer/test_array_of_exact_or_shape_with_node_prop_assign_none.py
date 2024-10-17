from dash import Dash, html

from dash_test_components import ArrayOfExactOrShapeWithNodePropAssignNone


def test_aoeoswnpsn001_array_of_exact_or_shape_with_node_prop_assign_none(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            ArrayOfExactOrShapeWithNodePropAssignNone(
                id="test-component1",
                test_array_of_exact_prop=[{"label": c, "value": c} for c in "abc"],
                test_array_of_shape_prop=[{"label": c, "value": c} for c in "abc"],
            ),
            ArrayOfExactOrShapeWithNodePropAssignNone(
                id="test-component2",
                test_array_of_exact_prop=None,
                test_array_of_shape_prop=None,
            ),
        ]
    )

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal(
        "#test-component1",
        "length of test_array_of_exact_prop: 3, length of test_array_of_shape_prop: 3",
    )
    dash_duo.wait_for_text_to_equal(
        "#test-component2",
        "length of test_array_of_exact_prop: 0, length of test_array_of_shape_prop: 0",
    )
