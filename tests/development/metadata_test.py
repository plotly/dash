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
- id (string; optional)

Available events: 'restyle', 'relayout', 'click'"""
    def __init__(self, children=None, **kwargs):
        self._prop_names = ['children', 'optionalArray', 'optionalBool', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalNode', 'optionalElement', 'optionalEnum', 'optionalUnion', 'optionalArrayOf', 'optionalObjectOf', 'optionalObjectWithShapeAndNestedDescription', 'optionalAny', 'customProp', 'customArrayProp', 'data-*', 'aria-*', 'id']
        self._type = 'Table'
        self._namespace = 'TableComponents'
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_events = ['restyle', 'relayout', 'click']
        self.available_properties = ['children', 'optionalArray', 'optionalBool', 'optionalNumber', 'optionalObject', 'optionalString', 'optionalNode', 'optionalElement', 'optionalEnum', 'optionalUnion', 'optionalArrayOf', 'optionalObjectOf', 'optionalObjectWithShapeAndNestedDescription', 'optionalAny', 'customProp', 'customArrayProp', 'data-*', 'aria-*', 'id']
        self.available_wildcard_properties =            ['data-', 'aria-']

        for k in []:
            if k not in kwargs:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Table, self).__init__(children=children, **kwargs)

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
