import dash
from dash._grouping import make_grouping_by_index, grouping_len, flatten_grouping
from dash._utils import create_callback_id
from dash.dependencies import Input, State, Output, ClientsideFunction
from dash._compression import GzipCompressionManager
import mock
import json
import string
import pytest
from fixtures import (  # noqa: F401
    scalar_grouping_size,
    list_grouping_size,
    dict_grouping_size,
    mixed_grouping_size,
)


def make_dependency_grouping(schema, dep_classes):
    """
    Build a grouping of dependency objects with type matching the dep_classes argument.
    If dep_classes is a list with more than one element, then the returned grouping
    will cycle through these classes (e.g. to mix Input and State).
    """
    if not isinstance(dep_classes, list):
        dep_classes = [dep_classes]

    flat_names = list(string.ascii_letters[: grouping_len(schema)])
    flat_dependencies = [
        dep_classes[i % len(dep_classes)]("component", name)
        for i, name in enumerate(flat_names)
    ]
    return make_grouping_by_index(schema, flat_dependencies)


def check_output_for_grouping(grouping):
    """
    Check the behavior of a callback that returns the specified grouping
    """
    outputs = make_dependency_grouping(grouping, Output)
    multi = not isinstance(outputs, Output)
    app = dash.Dash()
    mock_fn = mock.Mock()
    mock_fn.return_value = grouping
    if multi:
        callback_id = create_callback_id(flatten_grouping(outputs), [])
    else:
        callback_id = create_callback_id(outputs, [])

    app.callback(
        outputs,
        Input("input-a", "prop"),
    )(mock_fn)

    wrapped_fn = app.callback_map[callback_id]["callback"]

    expected_outputs = [
        (dep.component_id, dep.component_property, val)
        for dep, val in zip(flatten_grouping(outputs), flatten_grouping(grouping))
    ]

    outputs_list = [{"id": out[0], "property": out[1]} for out in expected_outputs]
    if not multi:
        outputs_list = outputs_list[0]

    result = json.loads(wrapped_fn("Hello", outputs_list=outputs_list))

    response = result["response"]
    for id, prop, val in expected_outputs:
        assert response[id][prop] == val


def test_callback_output_scalar(scalar_grouping_size):
    check_output_for_grouping(scalar_grouping_size[0])


def test_callback_output_tuple(list_grouping_size):
    if list_grouping_size[1] == 0:
        pytest.skip("Empty output grouping is not valid")

    check_output_for_grouping(list_grouping_size[0])


def test_callback_output_dict(dict_grouping_size):
    if dict_grouping_size[1] == 0:
        pytest.skip("Empty output grouping is not valid")

    check_output_for_grouping(dict_grouping_size[0])


def test_callback_output_size(mixed_grouping_size):
    check_output_for_grouping(mixed_grouping_size[0])


def check_callback_inputs_for_grouping(grouping):
    """
    Check the expected behavior of a callback function configured to input arguments
    according to the form of the provided grouping. If the grouping is a dict, then
    the callback function should be called with keyword arguments. Otherwise, it
    should be called with positional arguments
    """
    inputs = make_dependency_grouping(grouping, [Input, State])

    app = dash.Dash()
    mock_fn = mock.Mock()
    mock_fn.return_value = 23

    app.callback(
        Output("output-a", "prop"),
        inputs,
    )(mock_fn)

    wrapped_fn = app.callback_map["output-a.prop"]["callback"]

    flat_input_state_values = flatten_grouping(grouping)
    flat_input_values = flat_input_state_values[0::2]
    flat_state_values = flat_input_state_values[1::2]
    flat_inputs = flat_input_values + flat_state_values

    json.loads(
        wrapped_fn(*flat_inputs, outputs_list={"id": "output-a", "property": "prop"})
    )

    if isinstance(grouping, dict):
        # Check that user callback function was called with named keyword arguments
        mock_fn.assert_called_once_with(**grouping)
    elif isinstance(grouping, (tuple, list)):
        # Check that user callback function was called with positional arguments
        mock_fn.assert_called_once_with(*grouping)
    else:
        # Check that user callback function was called with single argument
        mock_fn.assert_called_once_with(grouping)


def test_callback_input_scalar_grouping(scalar_grouping_size):
    if scalar_grouping_size[1] == 0:
        pytest.skip("Empty input grouping is not valid")

    check_callback_inputs_for_grouping(scalar_grouping_size[0])


def test_callback_input_list_grouping(list_grouping_size):
    if list_grouping_size[1] == 0:
        pytest.skip("Empty input grouping is not valid")

    check_callback_inputs_for_grouping(list_grouping_size[0])


def test_callback_input_dict_grouping(dict_grouping_size):
    if dict_grouping_size[1] == 0:
        pytest.skip("Empty input grouping is not valid")

    check_callback_inputs_for_grouping(dict_grouping_size[0])


def test_callback_input_mixed_grouping(mixed_grouping_size):
    check_callback_inputs_for_grouping(mixed_grouping_size[0])


@pytest.mark.parametrize(
    "grouping",
    [
        [[0, 1], 2],
        dict(a=[0, 1], b=2),
    ],
)
def test_clientside_callback_grouping_validation(grouping):
    """
    Clientside callbacks do not support dependency groupings yet, so we make sure that
    these are not allowed through validation.

    This test should be removed when grouping support is added for clientside
    callbacks.
    """
    app = dash.Dash()

    # Should pass validation with no groupings
    app.clientside_callback(
        ClientsideFunction("foo", "bar"),
        Output("output-a", "prop"),
        Input("input-a", "prop"),
    )

    # Validation error with output is a grouping
    with pytest.raises(dash.exceptions.IncorrectTypeException):
        app.clientside_callback(
            ClientsideFunction("foo", "bar"),
            make_dependency_grouping(grouping, [Output]),
            Input("input-a", "prop"),
        )

    # Validation error with input is a grouping
    with pytest.raises(dash.exceptions.IncorrectTypeException):
        app.clientside_callback(
            ClientsideFunction("foo", "bar"),
            Output("output-a", "prop"),
            make_dependency_grouping(grouping, [Input]),
        )

    # Validation error when both are groupings
    with pytest.raises(dash.exceptions.IncorrectTypeException):
        app.clientside_callback(
            ClientsideFunction("foo", "bar"),
            make_dependency_grouping(grouping, [Output]),
            make_dependency_grouping(grouping, [Input]),
        )


def test_callback_compression_manager_parameter():
    """Test that compression_manager can be passed to callback decorator."""
    app = dash.Dash()
    compression_manager = GzipCompressionManager()

    @app.callback(
        Output("output", "children"),
        Input("input", "value"),
        compression_manager=compression_manager,
    )
    def update_output(value):
        return value

    # Verify the callback was registered
    assert len(app.callback_map) == 1

    # Get the registered callback entry
    callback_id = "output.children"
    assert callback_id in app.callback_map
    callback_entry = app.callback_map[callback_id]

    # Verify compression manager is stored in the callback entry
    assert "compression_manager" in callback_entry
    assert callback_entry["compression_manager"] is compression_manager


def test_callback_without_compression_manager():
    """Test that callbacks work normally without compression_manager."""
    app = dash.Dash()

    @app.callback(Output("output", "children"), Input("input", "value"))
    def update_output(value):
        return value

    # Verify the callback was registered
    assert len(app.callback_map) == 1

    # Get the registered callback entry
    callback_id = "output.children"
    callback_entry = app.callback_map[callback_id]

    # Verify no compression manager is stored
    assert callback_entry["compression_manager"] is None


def test_multiple_callbacks_different_compression_managers():
    """Test that different callbacks can have different compression managers."""
    app = dash.Dash()
    compression_manager1 = GzipCompressionManager(level=1)
    compression_manager2 = GzipCompressionManager(level=9)

    @app.callback(
        Output("output1", "children"),
        Input("input1", "value"),
        compression_manager=compression_manager1,
    )
    def update_output1(value):
        return value

    @app.callback(
        Output("output2", "children"),
        Input("input2", "value"),
        compression_manager=compression_manager2,
    )
    def update_output2(value):
        return value

    # Verify both callbacks were registered
    assert len(app.callback_map) == 2

    # Get the registered callback entries
    callback_entry1 = app.callback_map["output1.children"]
    callback_entry2 = app.callback_map["output2.children"]

    # Extract compression managers
    manager1 = callback_entry1["compression_manager"]
    manager2 = callback_entry2["compression_manager"]

    # Verify different managers are assigned
    assert manager1 is compression_manager1
    assert manager2 is compression_manager2
    assert manager1.level != manager2.level
