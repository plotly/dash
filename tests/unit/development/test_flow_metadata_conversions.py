import json
import os
from collections import OrderedDict

import pytest

from dash.development._py_components_generation import (
    create_docstring,
    prohibit_events,
    js_to_py_type,
)
from . import assert_flow_docstring

_dir = os.path.dirname(os.path.abspath(__file__))

expected_arg_strings = OrderedDict(
    [
        [
            "children",
            "a list of or a singular dash component, string or number",
        ],  # noqa: E501
        ["requiredString", "string"],
        ["optionalString", "string"],
        ["optionalBoolean", "boolean"],
        ["optionalFunc", ""],
        [
            "optionalNode",
            "a list of or a singular dash component, string or number",
        ],  # noqa: E501
        ["optionalArray", "list"],
        ["requiredUnion", "string | number"],
        [
            "optionalSignature(shape)",
            "\n".join(
                [
                    "dict containing keys 'checked', 'children', 'customData', 'disabled', 'label', 'primaryText', 'secondaryText', 'style', 'value'.",
                    # noqa: E501
                    "Those keys have the following types:",
                    "- checked (boolean; optional)",
                    "- children (a list of or a singular dash component, string or number; optional)",  # noqa: E501
                    "- customData (bool | number | str | dict | list; required): A test description",  # noqa: E501
                    "- disabled (boolean; optional)",
                    "- label (string; optional)",
                    "- primaryText (string; required): Another test description",
                    "- secondaryText (string; optional)",
                    "- style (dict; optional)",
                    "- value (bool | number | str | dict | list; required)",
                ]
            ),
        ],
        [
            "requiredNested",
            "\n".join(
                [
                    "dict containing keys 'customData', 'value'.",
                    "Those keys have the following types:",
                    "- customData (required): . customData has the following type: dict containing keys 'checked', 'children', 'customData', 'disabled', 'label', 'primaryText', 'secondaryText', 'style', 'value'.",
                    # noqa: E501
                    "  Those keys have the following types:",
                    "  - checked (boolean; optional)",
                    "  - children (a list of or a singular dash component, string or number; optional)",  # noqa: E501
                    "  - customData (bool | number | str | dict | list; required)",
                    "  - disabled (boolean; optional)",
                    "  - label (string; optional)",
                    "  - primaryText (string; required)",
                    "  - secondaryText (string; optional)",
                    "  - style (dict; optional)",
                    "  - value (bool | number | str | dict | list; required)",
                    "- value (bool | number | str | dict | list; required)",
                ]
            ),
        ],
    ]
)


@pytest.fixture
def load_test_flow_metadata_json():
    path = os.path.join(_dir, "flow_metadata_test.json")
    with open(path) as data_file:
        json_string = data_file.read()
        data = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(json_string)
    return data


def test_docstring(load_test_flow_metadata_json):
    docstring = create_docstring(
        "Flow_component",
        load_test_flow_metadata_json["props"],
        load_test_flow_metadata_json["description"],
    )
    prohibit_events(load_test_flow_metadata_json["props"]),
    assert_flow_docstring(docstring)


def test_docgen_to_python_args(load_test_flow_metadata_json):
    props = load_test_flow_metadata_json["props"]

    for prop_name, prop in list(props.items()):
        assert (
            js_to_py_type(prop["flowType"], is_flow_type=True)
            == expected_arg_strings[prop_name]
        )
