# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Store(Component):
    """A Store component.
Easily keep data on the client side with this component.
The data is not inserted in the DOM.
Data can be in memory, localStorage or sessionStorage.
The data will be kept with the id as key.

Keyword arguments:
- id (string; required): The key of the storage.
- storage_type (a value equal to: 'local', 'session', 'memory'; optional): The type of the web storage.

memory: only kept in memory, reset on page refresh.
local: window.localStorage, data is kept after the browser quit.
session: window.sessionStorage, data is cleared once the browser quit.
- data (dict | list | number | string; optional): The stored data for the id.
- clear_data (boolean; optional): Set to true to remove the data contained in `data_key`.
- modified_timestamp (number; optional): The last time the storage was modified.

Available events: """
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, storage_type=Component.UNDEFINED, data=Component.UNDEFINED, clear_data=Component.UNDEFINED, modified_timestamp=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'storage_type', 'data', 'clear_data', 'modified_timestamp']
        self._type = 'Store'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['id', 'storage_type', 'data', 'clear_data', 'modified_timestamp']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Store, self).__init__(**args)

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
            return ('Store(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'Store(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
