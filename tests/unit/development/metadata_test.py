# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
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
    def __init__(
        self,
        children: typing.Union[str, int, float, Component, typing.List[typing.Union[str, int, float, Component]]] = None,
        optionalArray: typing.List = Component.UNDEFINED,
        optionalBool: bool = Component.UNDEFINED,
        optionalFunc: typing.Any = Component.UNDEFINED,
        optionalNumber: typing.Union[float, int] = Component.UNDEFINED,
        optionalObject: typing.Dict = Component.UNDEFINED,
        optionalString: str = Component.UNDEFINED,
        optionalSymbol: typing.Any = Component.UNDEFINED,
        optionalNode: typing.Union[str, int, float, Component, typing.List[typing.Union[str, int, float, Component]]] = Component.UNDEFINED,
        optionalElement: Component = Component.UNDEFINED,
        optionalMessage: typing.Any = Component.UNDEFINED,
        optionalEnum: typing.Any = Component.UNDEFINED,
        optionalUnion: typing.Union[str, typing.Union[float, int], typing.Any] = Component.UNDEFINED,
        optionalArrayOf: typing.List[typing.Union[float, int]] = Component.UNDEFINED,
        optionalObjectOf: typing.Dict[str, typing.Union[float, int]] = Component.UNDEFINED,
        optionalObjectWithExactAndNestedDescription: typing.Dict[str, typing.Union[str, typing.Union[float, int], typing.Dict[str, typing.Union[typing.List[typing.Dict], typing.Dict]]]] = Component.UNDEFINED,
        optionalObjectWithShapeAndNestedDescription: typing.Dict[str, typing.Union[str, typing.Union[float, int], typing.Dict[str, typing.Union[typing.List[typing.Dict], typing.Dict]]]] = Component.UNDEFINED,
        optionalAny: typing.Any = Component.UNDEFINED,
        customProp: typing.Any = Component.UNDEFINED,
        customArrayProp: typing.List[typing.Any] = Component.UNDEFINED,
        id: str = Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'aria-*', 'customArrayProp', 'customProp', 'data-*', 'in', 'optionalAny', 'optionalArray', 'optionalArrayOf', 'optionalBool', 'optionalElement', 'optionalEnum', 'optionalNode', 'optionalNumber', 'optionalObject', 'optionalObjectOf', 'optionalObjectWithExactAndNestedDescription', 'optionalObjectWithShapeAndNestedDescription', 'optionalString', 'optionalUnion']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'aria-*', 'customArrayProp', 'customProp', 'data-*', 'in', 'optionalAny', 'optionalArray', 'optionalArrayOf', 'optionalBool', 'optionalElement', 'optionalEnum', 'optionalNode', 'optionalNumber', 'optionalObject', 'optionalObjectOf', 'optionalObjectWithExactAndNestedDescription', 'optionalObjectWithShapeAndNestedDescription', 'optionalString', 'optionalUnion']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Table, self).__init__(children=children, **args)
