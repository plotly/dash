from collections import OrderedDict
from difflib import unified_diff

from dash.development._py_components_generation import (
    create_docstring,
    prohibit_events,
    js_to_py_type,
)
from . import expected_table_component_doc

expected_arg_strings = OrderedDict(
    [
        ["children", "a list of or a singular dash component, string or number"],
        ["optionalArray", "list"],
        ["optionalBool", "boolean"],
        ["optionalFunc", ""],
        ["optionalNumber", "number"],
        ["optionalObject", "dict"],
        ["optionalString", "string"],
        ["optionalSymbol", ""],
        ["optionalElement", "dash component"],
        ["optionalNode", "a list of or a singular dash component, string or number"],
        ["optionalMessage", ""],
        ["optionalEnum", "a value equal to: 'News', 'Photos'"],
        ["optionalUnion", "string | number"],
        ["optionalArrayOf", "list of numbers"],
        ["optionalObjectOf", "dict with strings as keys and values of type number"],
        [
            "optionalObjectWithExactAndNestedDescription",
            "\n".join(
                [
                    "dict with keys:\n",
                    "    - color (string; optional)\n",
                    "    - figure (dict; optional):",
                    "        Figure is a plotly graph object.\n",
                    "        `figure` is a dict with keys:\n",
                    # noqa: E501
                    "        - data (list of dicts; optional):",
                    "            data is a collection of traces.\n",
                    "        - layout (dict; optional):",
                    "            layout describes the rest of the figure.\n",
                    # noqa: E501
                    "    - fontSize (number; optional)",
                ]
            ),
        ],
        [
            "optionalObjectWithShapeAndNestedDescription",
            "\n".join(
                [
                    "dict with keys:\n",
                    "    - color (string; optional)\n",
                    "    - figure (dict; optional):",
                    "        Figure is a plotly graph object.\n",
                    "        `figure` is a dict with keys:\n",
                    # noqa: E501
                    "        - data (list of dicts; optional):",
                    "            data is a collection of traces.\n",
                    "        - layout (dict; optional):",
                    "            layout describes the rest of the figure.\n",
                    # noqa: E501
                    "    - fontSize (number; optional)",
                ],
            ),
        ],
        ["optionalAny", "boolean | number | string | dict | list"],
        ["customProp", ""],
        ["customArrayProp", "list"],
        ["data-*", "string"],
        ["aria-*", "string"],
        ["in", "string"],
        ["id", "string"],
    ]
)


def test_docstring(load_test_metadata_json):
    docstring = create_docstring(
        "Table",
        load_test_metadata_json["props"],
        load_test_metadata_json["description"],
    )
    prohibit_events(load_test_metadata_json["props"]),
    assert not list(unified_diff(expected_table_component_doc, docstring.splitlines()))


def test_docgen_to_python_args(load_test_metadata_json):
    props = load_test_metadata_json["props"]

    for prop_name, prop in list(props.items()):
        assert js_to_py_type(prop["type"]) == expected_arg_strings[prop_name]
