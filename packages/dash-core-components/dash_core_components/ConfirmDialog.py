# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ConfirmDialog(Component):
    """A ConfirmDialog component.
ConfirmDialog is used to display the browser's native "confirm" modal,
with an optional message and two buttons ("OK" and "Cancel").
This ConfirmDialog can be used in conjunction with buttons when the user
is performing an action that should require an extra step of verification.

Keyword arguments:
- id (string; optional)
- message (string; optional): Message to show in the popup.
- submit_n_clicks (number; optional): Number of times the submit button was clicked
- submit_n_clicks_timestamp (number; optional): Last time the submit button was clicked.
- cancel_n_clicks (number; optional): Number of times the popup was canceled.
- cancel_n_clicks_timestamp (number; optional): Last time the cancel button was clicked.
- displayed (boolean; optional): Set to true to send the ConfirmDialog.
- key (string; optional)

Available events: """
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, message=Component.UNDEFINED, submit_n_clicks=Component.UNDEFINED, submit_n_clicks_timestamp=Component.UNDEFINED, cancel_n_clicks=Component.UNDEFINED, cancel_n_clicks_timestamp=Component.UNDEFINED, displayed=Component.UNDEFINED, key=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'message', 'submit_n_clicks', 'submit_n_clicks_timestamp', 'cancel_n_clicks', 'cancel_n_clicks_timestamp', 'displayed', 'key']
        self._type = 'ConfirmDialog'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['id', 'message', 'submit_n_clicks', 'submit_n_clicks_timestamp', 'cancel_n_clicks', 'cancel_n_clicks_timestamp', 'displayed', 'key']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(ConfirmDialog, self).__init__(**args)

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
            return ('ConfirmDialog(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'ConfirmDialog(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
