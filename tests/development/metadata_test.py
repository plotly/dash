# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args



schema = {'optionalArray': {'type': 'list'}, 'optionalBool': {'type': 'boolean'}, 'optionalFunc': {}, 'optionalNumber': {'type': 'number'}, 'optionalObject': {'type': 'dict'}, 'optionalString': {'type': 'string'}, 'optionalSymbol': {}, 'optionalNode': {'anyof': [{'type': 'component'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'string'}, {'type': 'list', 'schema': {'type': ('component', 'boolean', 'number', 'string')}}]}, 'optionalElement': {'type': 'component'}, 'optionalMessage': {}, 'optionalEnum': {'allowed': ['News', 'Photos'], 'type': ('string', 'number')}, 'optionalUnion': {'anyof': [{'type': 'string'}, {'type': 'number'}, {}]}, 'optionalArrayOf': {'type': 'list', 'schema': {'type': 'number', 'nullable': False}}, 'optionalObjectOf': {'type': 'dict', 'nullable': False, 'valueschema': {'type': 'number'}}, 'optionalObjectWithShapeAndNestedDescription': {'type': 'dict', 'allow_unknown': False, 'nullable': False, 'schema': {'color': {'type': 'string'}, 'fontSize': {'type': 'number'}, 'figure': {'type': 'dict', 'allow_unknown': False, 'nullable': False, 'schema': {'data': {'type': 'list', 'schema': {'type': 'dict', 'nullable': False}}, 'layout': {'type': 'dict'}}}}}, 'optionalAny': {'type': ('boolean', 'number', 'string', 'dict', 'list')}, 'customProp': {}, 'customArrayProp': {'type': 'list', 'schema': {'nullable': False}}, 'children': {'anyof': [{'type': 'string'}, {'type': 'number'}, {'type': 'boolean'}, {'type': 'component'}, {'allowed': [None], 'type': ('string', 'number'), 'nullable': True}, {'type': 'list', 'schema': {'anyof': [{'type': 'string'}, {'type': 'number'}, {'type': 'boolean'}, {'type': 'component'}, {'allowed': [None], 'type': ('string', 'number'), 'nullable': True}], 'nullable': True}}], 'nullable': True}, 'in': {'type': 'string'}, 'id': {'type': 'string'}, 'dashEvents': {'allowed': ['restyle', 'relayout', 'click'], 'type': ('string', 'number')}}

class Table(Component):
    """A Table component.
This is a description of the component.
It's multiple lines long.

Keyword arguments:
- children (string | number | boolean | dash component | a value equal to: null | list; optional)
- optionalArray (list; optional): Description of optionalArray
- optionalBool (boolean; optional)
- optionalNumber (number; optional)
- optionalObject (dict; optional)
- optionalString (string; optional)
- optionalNode (a list of or a singular dash component, string or number; optional)
- optionalElement (dash component; optional)
- optionalEnum (a value equal to: 'News', 'Photos'; optional)
- optionalUnion (string | number; optional)
- optionalArrayOf (list; optional)
- optionalObjectOf (dict with strings as keys and values of type number; optional)
- optionalObjectWithShapeAndNestedDescription (optional): . optionalObjectWithShapeAndNestedDescription has the following type: dict containing keys 'color', 'fontSize', 'figure'.
Those keys have the following types: 
  - color (string; optional)
  - fontSize (number; optional)
  - figure (optional): Figure is a plotly graph object. figure has the following type: dict containing keys 'data', 'layout'.
Those keys have the following types: 
  - data (list; optional): data is a collection of traces
  - layout (dict; optional): layout describes the rest of the figure
- optionalAny (boolean | number | string | dict | list; optional)
- data-* (string; optional)
- aria-* (string; optional)
- customProp (optional)
- customArrayProp (list; optional)
- in (string; optional)
- id (string; optional)

Available events: 'restyle', 'relayout', 'click'"""
    _schema = schema
    @_explicitize_args
    def __init__(self, children=None, optionalArray=Component.UNDEFINED, optionalBool=Component.UNDEFINED, optionalFunc=Component.UNDEFINED, optionalNumber=Component.UNDEFINED, optionalObject=Component.UNDEFINED, optionalString=Component.UNDEFINED, optionalSymbol=Component.UNDEFINED, optionalNode=Component.UNDEFINED, optionalElement=Component.UNDEFINED, optionalMessage=Component.UNDEFINED, optionalEnum=Component.UNDEFINED, optionalUnion=Component.UNDEFINED, optionalArrayOf=Component.UNDEFINED, optionalObjectOf=Component.UNDEFINED, optionalObjectWithShapeAndNestedDescription=Component.UNDEFINED, optionalAny=Component.UNDEFINED, customProp=Component.UNDEFINED, customArrayProp=Component.UNDEFINED, id=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'optionalArray', 'optionalBool', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalNode', 'optionalElement', 'optionalEnum', 'optionalUnion', 'optionalArrayOf', 'optionalObjectOf', 'optionalObjectWithShapeAndNestedDescription', 'optionalAny', 'data-*', 'aria-*', 'customProp', 'customArrayProp', 'in', 'id']
        self._type = 'Table'
        self._namespace = 'TableComponents'
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_events = ['restyle', 'relayout', 'click']
        self.available_properties = ['children', 'optionalArray', 'optionalBool', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalNode', 'optionalElement', 'optionalEnum', 'optionalUnion', 'optionalArrayOf', 'optionalObjectOf', 'optionalObjectWithShapeAndNestedDescription', 'optionalAny', 'data-*', 'aria-*', 'customProp', 'customArrayProp', 'in', 'id']
        self.available_wildcard_properties =            ['data-', 'aria-']

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        args.pop('children', None)
        super(Table, self).__init__(children=children, **args)

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('Table(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'Table(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
