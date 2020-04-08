# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Table(Component):
    """A Table component.
This is a description of the component.
It's multiple lines long.

Keyword arguments:
- children (a list of or a singular dash component, string or number; optional)
- optionalArray (list; optional): Description of optionalArray
- optionalBool (boolean; optional)
- optionalNumber (number; default 42)
- optionalObject (dict; optional)
- optionalString (string; default 'hello world')
- optionalNode (a list of or a singular dash component, string or number; optional)
- optionalElement (dash component; optional)
- optionalEnum (a value equal to: 'News', 'Photos'; optional)
- optionalUnion (string | number; optional)
- optionalArrayOf (list of numbers; optional)
- optionalObjectOf (dict with strings as keys and values of type number; optional)
- optionalObjectWithExactAndNestedDescription (dict; optional): optionalObjectWithExactAndNestedDescription has the following type: dict containing keys 'color', 'fontSize', 'figure'.
Those keys have the following types:
  - color (string; optional)
  - fontSize (number; optional)
  - figure (dict; optional): Figure is a plotly graph object. figure has the following type: dict containing keys 'data', 'layout'.
Those keys have the following types:
  - data (list of dicts; optional): data is a collection of traces
  - layout (dict; optional): layout describes the rest of the figure
- optionalObjectWithShapeAndNestedDescription (dict; optional): optionalObjectWithShapeAndNestedDescription has the following type: dict containing keys 'color', 'fontSize', 'figure'.
Those keys have the following types:
  - color (string; optional)
  - fontSize (number; optional)
  - figure (dict; optional): Figure is a plotly graph object. figure has the following type: dict containing keys 'data', 'layout'.
Those keys have the following types:
  - data (list of dicts; optional): data is a collection of traces
  - layout (dict; optional): layout describes the rest of the figure
- optionalAny (boolean | number | string | dict | list; optional)
- customProp (optional)
- customArrayProp (list; optional)
- data-* (string; optional)
- aria-* (string; optional)
- in (string; optional)
- id (string; optional)"""
    @_explicitize_args
    def __init__(self, children=None, optionalArray=Component.UNDEFINED, optionalBool=Component.UNDEFINED, optionalFunc=Component.UNDEFINED, optionalNumber=Component.UNDEFINED, optionalObject=Component.UNDEFINED, optionalString=Component.UNDEFINED, optionalSymbol=Component.UNDEFINED, optionalNode=Component.UNDEFINED, optionalElement=Component.UNDEFINED, optionalMessage=Component.UNDEFINED, optionalEnum=Component.UNDEFINED, optionalUnion=Component.UNDEFINED, optionalArrayOf=Component.UNDEFINED, optionalObjectOf=Component.UNDEFINED, optionalObjectWithExactAndNestedDescription=Component.UNDEFINED, optionalObjectWithShapeAndNestedDescription=Component.UNDEFINED, optionalAny=Component.UNDEFINED, customProp=Component.UNDEFINED, customArrayProp=Component.UNDEFINED, id=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'optionalArray', 'optionalBool', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalNode', 'optionalElement', 'optionalEnum', 'optionalUnion', 'optionalArrayOf', 'optionalObjectOf', 'optionalObjectWithExactAndNestedDescription', 'optionalObjectWithShapeAndNestedDescription', 'optionalAny', 'customProp', 'customArrayProp', 'data-*', 'aria-*', 'in', 'id']
        self._type = 'Table'
        self._namespace = 'TableComponents'
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'optionalArray', 'optionalBool', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalNode', 'optionalElement', 'optionalEnum', 'optionalUnion', 'optionalArrayOf', 'optionalObjectOf', 'optionalObjectWithExactAndNestedDescription', 'optionalObjectWithShapeAndNestedDescription', 'optionalAny', 'customProp', 'customArrayProp', 'data-*', 'aria-*', 'in', 'id']
        self.available_wildcard_properties =            ['data-', 'aria-']

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Table, self).__init__(children=children, **args)