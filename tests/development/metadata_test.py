# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args



schema = {'customArrayProp': {'schema': {'nullable': True}, 'type': 'list', 'allow_unknown': False, 'nullable': True}, 'optionalObjectWithShapeAndNestedDescription': {'schema': {'color': {'type': 'string', 'nullable': True}, 'fontSize': {'type': 'number', 'nullable': True}, 'figure': {'nullable': True, 'type': 'dict', 'allow_unknown': False, 'schema': {'layout': {'type': 'dict', 'nullable': True}, 'data': {'nullable': True, 'type': 'list', 'allow_unknown': False, 'schema': {'type': 'dict', 'nullable': True}}}}}, 'type': 'dict', 'allow_unknown': False, 'nullable': True}, 'optionalBool': {'type': 'boolean', 'nullable': True}, 'optionalFunc': {'nullable': True}, 'optionalSymbol': {'nullable': True}, 'in': {'type': 'string', 'nullable': True}, 'customProp': {'nullable': True}, 'children': {'anyof': [{'type': 'component'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'string'}, {'schema': {'type': ('component', 'boolean', 'number', 'string'), 'nullable': True}, 'type': 'list', 'nullable': True}], 'nullable': True}, 'optionalMessage': {'nullable': True}, 'optionalNumber': {'type': 'number', 'nullable': True}, 'optionalObject': {'type': 'dict', 'nullable': True}, 'dashEvents': {'allowed': [None, 'restyle', 'relayout', 'click'], 'nullable': True}, 'id': {'type': 'string', 'nullable': True}, 'optionalString': {'type': 'string', 'nullable': True}, 'optionalElement': {'type': 'component', 'nullable': True}, 'optionalArray': {'type': 'list', 'nullable': True}, 'optionalNode': {'anyof': [{'type': 'component'}, {'type': 'boolean'}, {'type': 'number'}, {'type': 'string'}, {'schema': {'type': ('component', 'boolean', 'number', 'string'), 'nullable': True}, 'type': 'list', 'nullable': True}], 'nullable': True}, 'optionalObjectOf': {'type': 'dict', 'valueschema': {'type': 'number', 'nullable': True}, 'nullable': True}, 'optionalEnum': {'allowed': [None, 'News', 'Photos'], 'nullable': True}, 'optionalArrayOf': {'schema': {'type': 'number', 'nullable': True}, 'type': 'list', 'allow_unknown': False, 'nullable': True}, 'optionalUnion': {'anyof': [{'type': 'string', 'nullable': True}, {'type': 'number', 'nullable': True}, {'nullable': True}], 'nullable': True}, 'optionalAny': {'type': ('boolean', 'number', 'string', 'dict', 'list'), 'nullable': True}}

class Table(Component):
    """A Table component.
This is a description of the component.
It's multiple lines long.

Keyword arguments:
- children (a list of or a singular dash component, string or number; optional)
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
- customProp (optional)
- customArrayProp (list; optional)
- data-* (string; optional)
- aria-* (string; optional)
- in (string; optional)
- id (string; optional)

Available events: 'restyle', 'relayout', 'click'"""
    _schema = schema
    @_explicitize_args
    def __init__(self, children=None, optionalArray=Component.UNDEFINED, optionalBool=Component.UNDEFINED, optionalFunc=Component.UNDEFINED, optionalNumber=Component.UNDEFINED, optionalObject=Component.UNDEFINED, optionalString=Component.UNDEFINED, optionalSymbol=Component.UNDEFINED, optionalNode=Component.UNDEFINED, optionalElement=Component.UNDEFINED, optionalMessage=Component.UNDEFINED, optionalEnum=Component.UNDEFINED, optionalUnion=Component.UNDEFINED, optionalArrayOf=Component.UNDEFINED, optionalObjectOf=Component.UNDEFINED, optionalObjectWithShapeAndNestedDescription=Component.UNDEFINED, optionalAny=Component.UNDEFINED, customProp=Component.UNDEFINED, customArrayProp=Component.UNDEFINED, id=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'optionalArray', 'optionalBool', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalNode', 'optionalElement', 'optionalEnum', 'optionalUnion', 'optionalArrayOf', 'optionalObjectOf', 'optionalObjectWithShapeAndNestedDescription', 'optionalAny', 'customProp', 'customArrayProp', 'data-*', 'aria-*', 'in', 'id']
        self._type = 'Table'
        self._namespace = 'TableComponents'
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_events = ['restyle', 'relayout', 'click']
        self.available_properties = ['children', 'optionalArray', 'optionalBool', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalNode', 'optionalElement', 'optionalEnum', 'optionalUnion', 'optionalArrayOf', 'optionalObjectOf', 'optionalObjectWithShapeAndNestedDescription', 'optionalAny', 'customProp', 'customArrayProp', 'data-*', 'aria-*', 'in', 'id']
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
