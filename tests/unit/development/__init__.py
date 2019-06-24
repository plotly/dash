import os

_dir = os.path.dirname(os.path.abspath(__file__))


def assert_no_trailing_spaces(s):
    for line in s.split("\n"):
        assert line == line.rstrip()


def match_lines(val, expected):
    for val1, exp1 in zip(val.splitlines(), expected.splitlines()):
        assert val1 == exp1


def assert_docstring(docstring):
    for i, line in enumerate(docstring.split("\n")):
        assert (
            line
            == (
                [
                    "A Table component.",
                    "This is a description of the component.",
                    "It's multiple lines long.",
                    "",
                    "Keyword arguments:",
                    "- children (a list of or a singular dash component, string or number; optional)",  # noqa: E501
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
                    "  - layout (dict; optional): layout describes "
                    "the rest of the figure",
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
                    "  - layout (dict; optional): layout describes "
                    "the rest of the figure",
                    "- optionalAny (boolean | number | string | dict | "
                    "list; optional)",
                    "- customProp (optional)",
                    "- customArrayProp (list; optional)",
                    "- data-* (string; optional)",
                    "- aria-* (string; optional)",
                    "- in (string; optional)",
                    "- id (string; optional)",
                    "        ",
                ]
            )[i]
        )


def assert_flow_docstring(docstring):
    for i, line in enumerate(docstring.split("\n")):
        assert (
            line
            == (
                [
                    "A Flow_component component.",
                    "This is a test description of the component.",
                    "It's multiple lines long.",
                    "",
                    "Keyword arguments:",
                    "- requiredString (string; required): A required string",
                    "- optionalString (string; default ''): A string that isn't required.",
                    "- optionalBoolean (boolean; default false): A boolean test",
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
            )[i]
        )
