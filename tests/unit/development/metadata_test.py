# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers # noqa: F401
import enum # noqa: F401
from typing_extensions import TypedDict, NotRequired # noqa: F401
from dash.development.base_component import Component, _explicitize_args


class OptionalEnumEnum(enum.Enum):
    News = "News"
    Photos = "Photos"

    def to_plotly_json(self):
        return self.value


class OptionalObjectWithExactAndNestedDescriptionFigure(TypedDict):
    data: NotRequired[typing.List[dict]]
    layout: NotRequired[dict]


class OptionalObjectWithExactAndNestedDescription(TypedDict):
    color: NotRequired[str]
    fontSize: NotRequired[typing.Union[int, float, numbers.Number]]
    figure: NotRequired[OptionalObjectWithExactAndNestedDescriptionFigure]


class OptionalObjectWithShapeAndNestedDescriptionFigure(TypedDict):
    data: NotRequired[typing.List[dict]]
    layout: NotRequired[dict]


class OptionalObjectWithShapeAndNestedDescription(TypedDict):
    color: NotRequired[str]
    fontSize: NotRequired[typing.Union[int, float, numbers.Number]]
    figure: NotRequired[OptionalObjectWithShapeAndNestedDescriptionFigure]


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
    OptionalEnumEnum = OptionalEnumEnum
    OptionalObjectWithExactAndNestedDescriptionFigure = OptionalObjectWithExactAndNestedDescriptionFigure
    OptionalObjectWithExactAndNestedDescription = OptionalObjectWithExactAndNestedDescription
    OptionalObjectWithShapeAndNestedDescriptionFigure = OptionalObjectWithShapeAndNestedDescriptionFigure
    OptionalObjectWithShapeAndNestedDescription = OptionalObjectWithShapeAndNestedDescription
    @_explicitize_args
    def __init__(
        self,
        children: typing.Union[str, int, float, Component, typing.List[typing.Union[str, int, float, Component]]] = None,
        optionalArray: typing.List = Component.UNDEFINED,
        optionalBool: bool = Component.UNDEFINED,
        optionalFunc: typing.Any = Component.UNDEFINED,
        optionalNumber: typing.Union[int, float, numbers.Number] = Component.UNDEFINED,
        optionalObject: dict = Component.UNDEFINED,
        optionalString: str = Component.UNDEFINED,
        optionalSymbol: typing.Any = Component.UNDEFINED,
        optionalNode: typing.Union[str, int, float, Component, typing.List[typing.Union[str, int, float, Component]]] = Component.UNDEFINED,
        optionalElement: Component = Component.UNDEFINED,
        optionalMessage: typing.Any = Component.UNDEFINED,
        optionalEnum: typing.Union[str, OptionalEnumEnum] = Component.UNDEFINED,
        optionalUnion: typing.Union[str, typing.Union[int, float, numbers.Number], typing.Any] = Component.UNDEFINED,
        optionalArrayOf: typing.List[typing.Union[int, float, numbers.Number]] = Component.UNDEFINED,
        optionalObjectOf: typing.Dict[typing.Union[str, float, int], typing.Union[int, float, numbers.Number]] = Component.UNDEFINED,
        optionalObjectWithExactAndNestedDescription: OptionalObjectWithExactAndNestedDescription = Component.UNDEFINED,
        optionalObjectWithShapeAndNestedDescription: OptionalObjectWithShapeAndNestedDescription = Component.UNDEFINED,
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
