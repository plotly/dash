# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Table(Component):
    """A Table component.
This is a description of the component.
It's multiple lines long.

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional)

- id (string; optional)

- aria-* (string; optional)

- customArrayProp (list; optional)

- customProp (optional)

- data-* (string; optional)

- in (string; optional)

- optionalAny (boolean | number | string | dict | list; optional)

- optionalArray (list; optional):
    Description of optionalArray.

- optionalArrayOf (list of numbers; optional)

- optionalBool (boolean; optional)

- optionalElement (dash component; optional)

- optionalEnum (a value equal to: 'News', 'Photos'; optional)

- optionalNode (a list of or a singular dash component, string or number; optional)

- optionalNumber (number; default 42)

- optionalObject (dict; optional)

- optionalObjectOf (dict with strings as keys and values of type number; optional)

- optionalObjectWithExactAndNestedDescription (dict; optional)

    `optionalObjectWithExactAndNestedDescription` is a dict with keys:

    - color (string; optional)

    - figure (dict; optional):
        Figure is a plotly graph object.

        `figure` is a dict with keys:

        - data (list of dicts; optional):
            data is a collection of traces.

        - layout (dict; optional):
            layout describes the rest of the figure.

    - fontSize (number; optional)

- optionalObjectWithShapeAndNestedDescription (dict; optional)

    `optionalObjectWithShapeAndNestedDescription` is a dict with keys:

    - color (string; optional)

    - figure (dict; optional):
        Figure is a plotly graph object.

        `figure` is a dict with keys:

        - data (list of dicts; optional):
            data is a collection of traces.

        - layout (dict; optional):
            layout describes the rest of the figure.

    - fontSize (number; optional)

- optionalString (string; default 'hello world')

- optionalUnion (string | number; optional)"""
    _children_props = ['optionalNode', 'optionalElement']
    _base_nodes = ['optionalNode', 'optionalElement', 'children']
    _namespace = 'TableComponents'
    _type = 'Table'
    @_explicitize_args
    def __init__(self, children=None, optionalArray=Component.UNDEFINED, optionalBool=Component.UNDEFINED, optionalFunc=Component.UNDEFINED, optionalNumber=Component.UNDEFINED, optionalObject=Component.UNDEFINED, optionalString=Component.UNDEFINED, optionalSymbol=Component.UNDEFINED, optionalNode=Component.UNDEFINED, optionalElement=Component.UNDEFINED, optionalMessage=Component.UNDEFINED, optionalEnum=Component.UNDEFINED, optionalUnion=Component.UNDEFINED, optionalArrayOf=Component.UNDEFINED, optionalObjectOf=Component.UNDEFINED, optionalObjectWithExactAndNestedDescription=Component.UNDEFINED, optionalObjectWithShapeAndNestedDescription=Component.UNDEFINED, optionalAny=Component.UNDEFINED, customProp=Component.UNDEFINED, customArrayProp=Component.UNDEFINED, id=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'aria-*', 'customArrayProp', 'customProp', 'data-*', 'in', 'optionalAny', 'optionalArray', 'optionalArrayOf', 'optionalBool', 'optionalElement', 'optionalEnum', 'optionalNode', 'optionalNumber', 'optionalObject', 'optionalObjectOf', 'optionalObjectWithExactAndNestedDescription', 'optionalObjectWithShapeAndNestedDescription', 'optionalString', 'optionalUnion']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'aria-*', 'customArrayProp', 'customProp', 'data-*', 'in', 'optionalAny', 'optionalArray', 'optionalArrayOf', 'optionalBool', 'optionalElement', 'optionalEnum', 'optionalNode', 'optionalNumber', 'optionalObject', 'optionalObjectOf', 'optionalObjectWithExactAndNestedDescription', 'optionalObjectWithShapeAndNestedDescription', 'optionalString', 'optionalUnion']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Table, self).__init__(children=children, **args)
