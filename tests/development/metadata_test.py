# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args



schema = {'children': {'anyof': [{'type': 'component'},
                        {'type': 'boolean'},
                        {'type': 'number'},
                        {'type': 'string'},
                        {'nullable': True,
                         'schema': {'anyof': [{'type': 'component'},
                                              {'type': 'boolean'},
                                              {'type': 'number'},
                                              {'type': 'string'}]},
                         'type': 'list'}],
              'nullable': True},
 'customArrayProp': {'allow_unknown': False,
                     'nullable': True,
                     'schema': {'nullable': True},
                     'type': 'list'},
 'customProp': {'nullable': True},
 'dashEvents': {'anyof': [{'nullable': True},
                          {'nullable': True},
                          {'nullable': True}],
                'nullable': True},
 'id': {'nullable': True, 'type': 'string'},
 'in': {'nullable': True, 'type': 'string'},
 'optionalAny': {'anyof_type': ['boolean',
                                'number',
                                'string',
                                'dict',
                                'list'],
                 'nullable': True},
 'optionalArray': {'nullable': True, 'type': 'list'},
 'optionalArrayOf': {'allow_unknown': False,
                     'nullable': True,
                     'schema': {'nullable': True, 'type': 'number'},
                     'type': 'list'},
 'optionalBool': {'nullable': True, 'type': 'boolean'},
 'optionalElement': {'nullable': True, 'type': 'component'},
 'optionalEnum': {'anyof': [{'nullable': True}, {'nullable': True}],
                  'nullable': True},
 'optionalFunc': {'nullable': True},
 'optionalMessage': {'nullable': True},
 'optionalNode': {'anyof': [{'type': 'component'},
                            {'type': 'boolean'},
                            {'type': 'number'},
                            {'type': 'string'},
                            {'nullable': True,
                             'schema': {'anyof': [{'type': 'component'},
                                                  {'type': 'boolean'},
                                                  {'type': 'number'},
                                                  {'type': 'string'}]},
                             'type': 'list'}],
                  'nullable': True},
 'optionalNumber': {'nullable': True, 'type': 'number'},
 'optionalObject': {'nullable': True, 'type': 'dict'},
 'optionalObjectOf': {'allow_unknown': False,
                      'nullable': True,
                      'schema': {'nullable': True, 'type': 'number'},
                      'type': 'dict'},
 'optionalObjectWithShapeAndNestedDescription': {'allow_unknown': False,
                                                 'nullable': True,
                                                 'schema': {'color': {'nullable': True,
                                                                      'type': 'string'},
                                                            'figure': {'allow_unknown': False,
                                                                       'nullable': True,
                                                                       'schema': {'data': {'allow_unknown': False,
                                                                                           'nullable': True,
                                                                                           'schema': {'nullable': True,
                                                                                                      'type': 'dict'},
                                                                                           'type': 'list'},
                                                                                  'layout': {'nullable': True,
                                                                                             'type': 'dict'}},
                                                                       'type': 'dict'},
                                                            'fontSize': {'nullable': True,
                                                                         'type': 'number'}},
                                                 'type': 'dict'},
 'optionalString': {'nullable': True, 'type': 'string'},
 'optionalSymbol': {'nullable': True},
 'optionalUnion': {'anyof': [{'nullable': True, 'type': 'string'},
                             {'nullable': True, 'type': 'number'},
                             {'nullable': True}],
                   'nullable': True}}

class Table(Component):
    """A Table component.
This is a description of the component.
It's multiple lines long.

Keyword arguments:
- children (a list of or a singular dash component, string or number; optional)
- data-* (string; optional)
- customArrayProp (list; optional)
- optionalObjectWithShapeAndNestedDescription (optional): . optionalObjectWithShapeAndNestedDescription has the following type: dict containing keys 'color', 'fontSize', 'figure'.
Those keys have the following types: 
  - color (string; optional)
  - fontSize (number; optional)
  - figure (optional): Figure is a plotly graph object. figure has the following type: dict containing keys 'layout', 'data'.
Those keys have the following types: 
  - layout (dict; optional): layout describes the rest of the figure
  - data (list; optional): data is a collection of traces
- aria-* (string; optional)
- optionalBool (boolean; optional)
- in (string; optional)
- customProp (optional)
- id (string; optional)
- optionalNumber (number; optional)
- optionalObject (dict; optional)
- optionalString (string; optional)
- optionalElement (dash component; optional)
- optionalArray (list; optional): Description of optionalArray
- optionalNode (a list of or a singular dash component, string or number; optional)
- optionalObjectOf (dict with strings as keys and values of type number; optional)
- optionalEnum (a value equal to: 'News', 'Photos'; optional)
- optionalArrayOf (list; optional)
- optionalUnion (string | number; optional)
- optionalAny (boolean | number | string | dict | list; optional)

Available events: 'restyle', 'relayout', 'click'"""
    _schema = schema
    @_explicitize_args
    def __init__(self, children=None, customArrayProp=Component.UNDEFINED, optionalObjectWithShapeAndNestedDescription=Component.UNDEFINED, optionalBool=Component.UNDEFINED, optionalFunc=Component.UNDEFINED, optionalSymbol=Component.UNDEFINED, customProp=Component.UNDEFINED, optionalMessage=Component.UNDEFINED, optionalNumber=Component.UNDEFINED, optionalObject=Component.UNDEFINED, id=Component.UNDEFINED, optionalString=Component.UNDEFINED, optionalElement=Component.UNDEFINED, optionalArray=Component.UNDEFINED, optionalNode=Component.UNDEFINED, optionalObjectOf=Component.UNDEFINED, optionalEnum=Component.UNDEFINED, optionalArrayOf=Component.UNDEFINED, optionalUnion=Component.UNDEFINED, optionalAny=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'data-*', 'customArrayProp', 'optionalObjectWithShapeAndNestedDescription', 'aria-*', 'optionalBool', 'in', 'customProp', 'id', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalElement', 'optionalArray', 'optionalNode', 'optionalObjectOf', 'optionalEnum', 'optionalArrayOf', 'optionalUnion', 'optionalAny']
        self._type = 'Table'
        self._namespace = 'TableComponents'
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_events = ['restyle', 'relayout', 'click']
        self.available_properties = ['children', 'data-*', 'customArrayProp', 'optionalObjectWithShapeAndNestedDescription', 'aria-*', 'optionalBool', 'in', 'customProp', 'id', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalElement', 'optionalArray', 'optionalNode', 'optionalObjectOf', 'optionalEnum', 'optionalArrayOf', 'optionalUnion', 'optionalAny']
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
