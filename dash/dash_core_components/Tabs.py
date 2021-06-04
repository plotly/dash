# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Tabs(Component):
    """A Tabs component.
A Dash component that lets you render pages with tabs - the Tabs component's children
can be dcc.Tab components, which can hold a label that will be displayed as a tab, and can in turn hold
children components that will be that tab's content.

Keyword arguments:

- children (list of a list of or a singular dash component, string or numbers | a list of or a singular dash component, string or number; optional):
    Array that holds Tab components.

- id (string; optional):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- className (string; optional):
    Appends a class to the Tabs container holding the individual Tab
    components.

- colors (dict; default {    border: '#d6d6d6',    primary: '#1975FA',    background: '#f9f9f9',}):
    Holds the colors used by the Tabs and Tab components. If you set
    these, you should specify colors for all properties, so: colors: {
    border: '#d6d6d6',    primary: '#1975FA',    background: '#f9f9f9'
    }.

    `colors` is a dict with keys:

    - background (string; optional)

    - border (string; optional)

    - primary (string; optional)

- content_className (string; optional):
    Appends a class to the Tab content container holding the children
    of the Tab that is selected.

- content_style (dict; optional):
    Appends (inline) styles to the tab content container holding the
    children of the Tab that is selected.

- loading_state (dict; optional):
    Object that holds the loading state object coming from
    dash-renderer.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- mobile_breakpoint (number; default 800):
    Breakpoint at which tabs are rendered full width (can be 0 if you
    don't want full width tabs on mobile).

- parent_className (string; optional):
    Appends a class to the top-level parent container holding both the
    Tabs container and the content container.

- parent_style (dict; optional):
    Appends (inline) styles to the top-level parent container holding
    both the Tabs container and the content container.

- persisted_props (list of a value equal to: 'value's; default ['value']):
    Properties whose user interactions will persist after refreshing
    the component or the page. Since only `value` is allowed this prop
    can normally be ignored.

- persistence (boolean | string | number; optional):
    Used to allow user interactions in this component to be persisted
    when the component - or the page - is refreshed. If `persisted` is
    truthy and hasn't changed from its previous value, a `value` that
    the user has changed while using the app will keep that change, as
    long as the new `value` also matches what was given originally.
    Used in conjunction with `persistence_type`.

- persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
    Where persisted user changes will be stored: memory: only kept in
    memory, reset on page refresh. local: window.localStorage, data is
    kept after the browser quit. session: window.sessionStorage, data
    is cleared once the browser quit.

- style (dict; optional):
    Appends (inline) styles to the Tabs container holding the
    individual Tab components.

- value (string; optional):
    The value of the currently selected Tab.

- vertical (boolean; default False):
    Renders the tabs vertically (on the side)."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, value=Component.UNDEFINED, className=Component.UNDEFINED, content_className=Component.UNDEFINED, parent_className=Component.UNDEFINED, style=Component.UNDEFINED, parent_style=Component.UNDEFINED, content_style=Component.UNDEFINED, vertical=Component.UNDEFINED, mobile_breakpoint=Component.UNDEFINED, colors=Component.UNDEFINED, loading_state=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'colors', 'content_className', 'content_style', 'loading_state', 'mobile_breakpoint', 'parent_className', 'parent_style', 'persisted_props', 'persistence', 'persistence_type', 'style', 'value', 'vertical']
        self._type = 'Tabs'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'colors', 'content_className', 'content_style', 'loading_state', 'mobile_breakpoint', 'parent_className', 'parent_style', 'persisted_props', 'persistence', 'persistence_type', 'style', 'value', 'vertical']
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
