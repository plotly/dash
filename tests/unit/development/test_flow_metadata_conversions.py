# flake8: ignore=E501
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
        ["children", "a list of or a singular dash component, string or number"],
        ["requiredString", "string"],
        ["optionalString", "string"],
        ["optionalBoolean", "boolean"],
        ["optionalFunc", ""],
        ["optionalNode", "a list of or a singular dash component, string or number"],
        ["optionalArray", "list"],
        ["requiredUnion", "string | number"],
        [
            "optionalSignature(shape)",
            "\n".join(
                [
                    "dict with keys:\n",
                    "    - checked (boolean; optional)\n",
                    "    - children (a list of or a singular dash component, string or number; optional)\n",
                    "    - customData (bool | number | str | dict | list; required):\n"
                    "        A test description.\n",
                    "    - disabled (boolean; optional)\n",
                    "    - label (string; optional)\n",
                    "    - primaryText (string; required):\n"
                    "        Another test description.\n",
                    "    - secondaryText (string; optional)\n",
                    "    - style (dict; optional)\n",
                    "    - value (bool | number | str | dict | list; required)",
                ]
            ),
        ],
        [
            "requiredNested",
            "\n".join(
                [
                    "dict with keys:\n",
                    "    - customData (dict; required)\n\n"
                    "        `customData` is a dict with keys:\n",
                    "        - checked (boolean; optional)\n",
                    "        - children (a list of or a singular dash component, string or number; optional)\n",
                    "        - customData (bool | number | str | dict | list; required)\n",
                    "        - disabled (boolean; optional)\n",
                    "        - label (string; optional)\n",
                    "        - primaryText (string; required)\n",
                    "        - secondaryText (string; optional)\n",
                    "        - style (dict; optional)\n",
                    "        - value (bool | number | str | dict | list; required)\n",
                    "    - value (bool | number | str | dict | list; required)",
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
    "",
    "- optionalArray (list; optional):",
    "    An array test with a particularly  long description that covers",
    "    several lines. It includes the newline character  and should span",
    "    3 lines in total.",
    "",
    "- optionalBoolean (boolean; default False):",
    "    A boolean test.",
    "",
    "- optionalNode (a list of or a singular dash component, string or number; optional):",
    "    A node test.",
    "",
    "- optionalSignature(shape) (dict; optional):",
    "    This is a test of an object's shape.",
    "",
    "    `optionalSignature(shape)` is a dict with keys:",
    "",
    "    - checked (boolean; optional)",
    "",
    "    - children (a list of or a singular dash component, string or number; optional)",
    "",
    "    - customData (bool | number | str | dict | list; required):",
    "        A test description.",
    "",
    "    - disabled (boolean; optional)",
    "",
    "    - label (string; optional)",
    "",
    "    - primaryText (string; required):",
    "        Another test description.",
    "",
    "    - secondaryText (string; optional)",
    "",
    "    - style (dict; optional)",
    "",
    "    - value (bool | number | str | dict | list; required)",
    "",
    "- optionalString (string; default ''):",
    "    A string that isn't required.",
    "",
    "- requiredNested (dict; required)",
    "",
    "    `requiredNested` is a dict with keys:",
    "",
    "    - customData (dict; required)",
    "",
    "        `customData` is a dict with keys:",
    "",
    "        - checked (boolean; optional)",
    "",
    "        - children (a list of or a singular dash component, string or number; optional)",
    "",
    "        - customData (bool | number | str | dict | list; required)",
    "",
    "        - disabled (boolean; optional)",
    "",
    "        - label (string; optional)",
    "",
    "        - primaryText (string; required)",
    "",
    "        - secondaryText (string; optional)",
    "",
    "        - style (dict; optional)",
    "",
    "        - value (bool | number | str | dict | list; required)",
    "",
    "    - value (bool | number | str | dict | list; required)",
    "",
    "- requiredString (string; required):",
    "    A required string.",
    "",
    "- requiredUnion (string | number; required)",
]


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
    print(docstring.splitlines())
    prohibit_events(load_test_flow_metadata_json["props"]),
    assert not list(unified_diff(expected_doc, docstring.splitlines()))


def test_docgen_to_python_args(load_test_flow_metadata_json):
    props = load_test_flow_metadata_json["props"]
    for prop_name, prop in list(props.items()):
        assert (
            js_to_py_type(prop["flowType"], is_flow_type=True)
            == expected_arg_strings[prop_name]
        )
