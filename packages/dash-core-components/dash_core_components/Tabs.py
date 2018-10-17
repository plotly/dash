# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Tabs(Component):
    """A Tabs component.
A Dash component that lets you render pages with tabs - the Tabs component's children
can be dcc.Tab components, which can hold a label that will be displayed as a tab, and can in turn hold
children components that will be that tab's content.

Keyword arguments:
- children (list | a list of or a singular dash component, string or number; optional): Array that holds Tab components
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- value (string; optional): The value of the currently selected Tab
- className (string; optional): Appends a class to the Tabs container holding the individual Tab components.
- content_className (string; optional): Appends a class to the Tab content container holding the children of the Tab that is selected.
- parent_className (string; optional): Appends a class to the top-level parent container holding both the Tabs container and the content container.
- style (dict; optional): Appends (inline) styles to the Tabs container holding the individual Tab components.
- parent_style (dict; optional): Appends (inline) styles to the top-level parent container holding both the Tabs container and the content container.
- content_style (dict; optional): Appends (inline) styles to the tab content container holding the children of the Tab that is selected.
- vertical (boolean; optional): Renders the tabs vertically (on the side)
- mobile_breakpoint (number; optional): Breakpoint at which tabs are rendered full width (can be 0 if you don't want full width tabs on mobile)
- colors (optional): Holds the colors used by the Tabs and Tab components. If you set these, you should specify colors for all properties, so:
colors: {
   border: '#d6d6d6',
   primary: '#1975FA',
   background: '#f9f9f9'
 }. colors has the following type: dict containing keys 'border', 'primary', 'background'.
Those keys have the following types: 
  - border (string; optional)
  - primary (string; optional)
  - background (string; optional)

Available events: """
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, value=Component.UNDEFINED, className=Component.UNDEFINED, content_className=Component.UNDEFINED, parent_className=Component.UNDEFINED, style=Component.UNDEFINED, parent_style=Component.UNDEFINED, content_style=Component.UNDEFINED, vertical=Component.UNDEFINED, mobile_breakpoint=Component.UNDEFINED, colors=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'value', 'className', 'content_className', 'parent_className', 'style', 'parent_style', 'content_style', 'vertical', 'mobile_breakpoint', 'colors']
        self._type = 'Tabs'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['children', 'id', 'value', 'className', 'content_className', 'parent_className', 'style', 'parent_style', 'content_style', 'vertical', 'mobile_breakpoint', 'colors']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Tabs, self).__init__(children=children, **args)

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
            return ('Tabs(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'Tabs(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
