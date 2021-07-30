import dash
from dash._grouping import make_grouping_by_index, grouping_len, flatten_grouping
from dash.dependencies import Input, State, Output
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

    wrapped_fn = app.callback(
        outputs,
        Input("input-a", "prop"),
    )(mock_fn)

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

    wrapped_fn = app.callback(
        Output("output-a", "prop"),
        inputs,
    )(mock_fn)

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
