import json
import os
from collections import OrderedDict
from difflib import unified_diff

import pytest

from dash.development._py_components_generation import (
    create_docstring,
    prohibit_events,
    js_to_py_type,
)

_dir = os.path.dirname(os.path.abspath(__file__))

expected_arg_strings = OrderedDict(
    [
        [
            "children",
            "a list of or a singular dash component, string or number",
        ],
        ["requiredString", "string"],
        ["optionalString", "string"],
        ["optionalBoolean", "boolean"],
        ["optionalFunc", ""],
        [
            "optionalNode",
            "a list of or a singular dash component, string or number",
        ],
        ["optionalArray", "list"],
        ["requiredUnion", "string | number"],
        [
            "optionalSignature(shape)",
            "\n".join(
                [
                    "dict containing keys 'checked', 'children', 'customData', 'disabled', 'label', 'primaryText', 'secondaryText', 'style', 'value'.",
                    "Those keys have the following types:",
                    "- checked (boolean; optional)",
                    "- children (a list of or a singular dash component, string or number; optional)",
                    "- customData (bool | number | str | dict | list; required): A test description",
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
                    "- customData (dict; required): customData has the following type: dict containing keys 'checked', 'children', 'customData', 'disabled', 'label', 'primaryText', 'secondaryText', 'style', 'value'.",
                    "  Those keys have the following types:",
                    "  - checked (boolean; optional)",
                    "  - children (a list of or a singular dash component, string or number; optional)",
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

expected_doc = [
    "A Flow_component component.",
    "This is a test description of the component.",
    "It's multiple lines long.",
    "",
    "Keyword arguments:",
    "- requiredString (string; required): A required string",
    "- optionalString (string; default ''): A string that isn't required.",
    "- optionalBoolean (boolean; default False): A boolean test",
    "- optionalNode (a list of or a singular dash component, string or number; optional): "
    "A node test",
    "- optionalArray (list; optional): An array test with a particularly ",
    "long description that covers several lines. It includes the newline character ",
    "and should span 3 lines in total.",
    "- requiredUnion (string | number; required)",
    "- optionalSignature(shape) (dict; optional): This is a test of an object's shape. "
    "optionalSignature(shape) has the following type: dict containing keys 'checked', "
    "'children', 'customData', 'disabled', 'label', 'primaryText', 'secondaryText', "
    "'style', 'value'.",
    "  Those keys have the following types:",
    "  - checked (boolean; optional)",
    "  - children (a list of or a singular dash component, string or number; optional)",
    "  - customData (bool | number | str | dict | list; required): A test description",
    "  - disabled (boolean; optional)",
    "  - label (string; optional)",
    "  - primaryText (string; required): Another test description",
    "  - secondaryText (string; optional)",
    "  - style (dict; optional)",
    "  - value (bool | number | str | dict | list; required)",
    "- requiredNested (dict; required): requiredNested has the following type: dict containing "
    "keys 'customData', 'value'.",
    "  Those keys have the following types:",
    "  - customData (dict; required): customData has the following type: dict containing "
    "keys 'checked', 'children', 'customData', 'disabled', 'label', 'primaryText', "
    "'secondaryText', 'style', 'value'.",
    "    Those keys have the following types:",
    "    - checked (boolean; optional)",
    "    - children (a list of or a singular dash component, string or number; optional)",
    "    - customData (bool | number | str | dict | list; required)",
    "    - disabled (boolean; optional)",
    "    - label (string; optional)",
    "    - primaryText (string; required)",
    "    - secondaryText (string; optional)",
    "    - style (dict; optional)",
    "    - value (bool | number | str | dict | list; required)",
    "  - value (bool | number | str | dict | list; required)",
]


@pytest.fixture
def load_test_flow_metadata_json():
    path = os.path.join(_dir, "flow_metadata_test.json")
    with open(path) as data_file:
        json_string = data_file.read()
        data = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
            json_string
        )
    return data


def test_docstring(load_test_flow_metadata_json):
    docstring = create_docstring(
        "Flow_component",
        load_test_flow_metadata_json["props"],
        load_test_flow_metadata_json["description"],
    )
    prohibit_events(load_test_flow_metadata_json["props"]),
    assert not list(unified_diff(expected_doc, docstring.splitlines()))


def test_docgen_to_python_args(load_test_flow_metadata_json):
    props = load_test_flow_metadata_json["props"]

    for prop_name, prop in list(props.items()):
        assert (
            js_to_py_type(prop["flowType"], is_flow_type=True)
            == expected_arg_strings[prop_name]
        )
