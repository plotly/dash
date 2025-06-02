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
        ["optionalArray", "list"],
        ["optionalBool", "boolean"],
        ["optionalFunc", ""],
        ["optionalNumber", "number"],
        ["optionalObject", "dict"],
        ["optionalString", "string"],
        ["optionalSymbol", ""],
        ["optionalNode", "a list of or a singular dash component, string or number"],
        ["optionalElement", "dash component"],
        ["optionalMessage", ""],
        ["optionalEnum", "a value equal to: 'News', 'Photos'"],
        ["optionalUnion", "string | number"],
        ["optionalArrayOf", "list of numbers"],
        ["optionalObjectOf", "dict with strings as keys and values of type number"],
        [
            "optionalObjectWithExactAndNestedDescription",
            "dict with keys:\n\n    - color (string; optional)\n\n    - fontSize (number; optional)\n\n    - figure (dict; optional):\n        Figure is a plotly graph object.\n\n        `figure` is a dict with keys:\n\n        - data (list of dicts; optional):\n            data is a collection of traces.\n\n        - layout (dict; optional):\n            layout describes the rest of the figure.",
        ],
        [
            "optionalObjectWithShapeAndNestedDescription",
            "dict with keys:\n\n    - color (string; optional)\n\n    - fontSize (number; optional)\n\n    - figure (dict; optional):\n        Figure is a plotly graph object.\n\n        `figure` is a dict with keys:\n\n        - data (list of dicts; optional):\n            data is a collection of traces.\n\n        - layout (dict; optional):\n            layout describes the rest of the figure.",
        ],
        ["optionalAny", "boolean | number | string | dict | list"],
        ["customProp", ""],
        ["customArrayProp", "list"],
        ["children", "a list of or a singular dash component, string or number"],
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
    (prohibit_events(load_test_metadata_json["props"]),)
    assert not list(unified_diff(expected_table_component_doc, docstring.splitlines()))


def test_docgen_to_python_args(load_test_metadata_json):
    props = load_test_metadata_json["props"]
    for prop_name, prop in list(props.items()):
        assert js_to_py_type(prop["type"]) == expected_arg_strings[prop_name]
