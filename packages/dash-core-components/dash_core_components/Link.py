# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Link(Component):
    """A Link component.
Link allows you to create a clickable link within a multi-page app.

For links with destinations outside the current app, `html.A` is a better
component to use.

Keyword arguments:
- children (a list of or a singular dash component, string or number; optional): The children of this component
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- href (string; optional): The URL of a linked resource.
- refresh (boolean; default False): Controls whether or not the page will refresh when the link is clicked
- className (string; optional): Often used with CSS to style elements with common properties.
- style (dict; optional): Defines CSS styles which will override styles previously set.
- loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, href=Component.UNDEFINED, refresh=Component.UNDEFINED, className=Component.UNDEFINED, style=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'href', 'refresh', 'className', 'style', 'loading_state']
        self._type = 'Link'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'href', 'refresh', 'className', 'style', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Link, self).__init__(children=children, **args)
