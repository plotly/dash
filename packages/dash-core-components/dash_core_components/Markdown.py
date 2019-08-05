# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Markdown(Component):
    """A Markdown component.
A component that renders Markdown text as specified by the
GitHub Markdown spec. These component uses
[react-markdown](https://rexxars.github.io/react-markdown/) under the hood.

Keyword arguments:
- children (string | list of strings; optional): A markdown string (or array of strings) that adhreres to the CommonMark spec
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- className (string; optional): Class name of the container element
- dangerously_allow_html (boolean; default False): A boolean to control raw HTML escaping.
Setting HTML from code is risky because it's easy to
inadvertently expose your users to a cross-site scripting (XSS)
(https://en.wikipedia.org/wiki/Cross-site_scripting) attack.
- dedent (boolean; default True): Remove matching leading whitespace from all lines.
Lines that are empty, or contain *only* whitespace, are ignored.
Both spaces and tab characters are removed, but only if they match;
we will not convert tabs to spaces or vice versa.
- highlight_config (dict; optional): Config options for syntax highlighting. highlight_config has the following type: dict containing keys 'theme'.
Those keys have the following types:
  - theme (a value equal to: 'dark', 'light'; optional): Color scheme; default 'light'
- loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading
- style (dict; optional): User-defined inline styles for the rendered Markdown"""
    @_explicitize_args
    def __init__(self, children=None, id=Component.UNDEFINED, className=Component.UNDEFINED, dangerously_allow_html=Component.UNDEFINED, dedent=Component.UNDEFINED, highlight_config=Component.UNDEFINED, loading_state=Component.UNDEFINED, style=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'dangerously_allow_html', 'dedent', 'highlight_config', 'loading_state', 'style']
        self._type = 'Markdown'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'dangerously_allow_html', 'dedent', 'highlight_config', 'loading_state', 'style']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Markdown, self).__init__(children=children, **args)
