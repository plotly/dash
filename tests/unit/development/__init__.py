import os

_dir = os.path.dirname(os.path.abspath(__file__))


def has_trailing_space(s):
    return any(line != line.rstrip() for line in s.splitlines())


expected_table_component_doc = [
    "A Table component.",
    "This is a description of the component.",
    "It's multiple lines long.",
    "",
    "Keyword arguments:",
    "- children (a list of or a singular dash component, string or number; optional)",
    "- optionalArray (list; optional): Description of optionalArray",
    "- optionalBool (boolean; optional)",
    "- optionalNumber (number; default 42)",
    "- optionalObject (dict; optional)",
    "- optionalString (string; default 'hello world')",
    "- optionalNode (a list of or a singular dash component, "
    "string or number; optional)",
    "- optionalElement (dash component; optional)",
    "- optionalEnum (a value equal to: 'News', 'Photos'; optional)",
    "- optionalUnion (string | number; optional)",
    "- optionalArrayOf (list of numbers; optional)",
    "- optionalObjectOf (dict with strings as keys and values "
    "of type number; optional)",
    "- optionalObjectWithExactAndNestedDescription (dict; optional): "
    "optionalObjectWithExactAndNestedDescription has the "
    "following type: dict containing keys "
    "'color', 'fontSize', 'figure'.",
    "Those keys have the following types:",
    "  - color (string; optional)",
    "  - fontSize (number; optional)",
    "  - figure (dict; optional): Figure is a plotly graph object. "
    "figure has the following type: dict containing "
    "keys 'data', 'layout'.",
    "Those keys have the following types:",
    "  - data (list of dicts; optional): data is a collection of traces",
    "  - layout (dict; optional): layout describes " "the rest of the figure",
    "- optionalObjectWithShapeAndNestedDescription (dict; optional): "
    "optionalObjectWithShapeAndNestedDescription has the "
    "following type: dict containing keys "
    "'color', 'fontSize', 'figure'.",
    "Those keys have the following types:",
    "  - color (string; optional)",
    "  - fontSize (number; optional)",
    "  - figure (dict; optional): Figure is a plotly graph object. "
    "figure has the following type: dict containing "
    "keys 'data', 'layout'.",
    "Those keys have the following types:",
    "  - data (list of dicts; optional): data is a collection of traces",
    "  - layout (dict; optional): layout describes " "the rest of the figure",
    "- optionalAny (boolean | number | string | dict | " "list; optional)",
    "- customProp (optional)",
    "- customArrayProp (list; optional)",
    "- data-* (string; optional)",
    "- aria-* (string; optional)",
    "- in (string; optional)",
    "- id (string; optional)",
]
