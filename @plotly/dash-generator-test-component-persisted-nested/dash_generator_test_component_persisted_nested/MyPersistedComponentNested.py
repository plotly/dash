# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class MyPersistedComponentNested(Component):
    """A MyPersistedComponentNested component.
A basic HTML input control for entering text, numbers, or passwords.

Note that checkbox and radio types are supported through
the Checklist and RadioItems component. Dates, times, and file uploads
are also supported through separate components.

Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- value (string | number; optional): The value of the input
- style (dict; optional): The input's inline styles
- className (string; optional): The class of the input element
- debounce (boolean; default False): If true, changes to input will be sent back to the Dash server only on enter or when losing focus.
If it's false, it will sent the value back on every change.
- type (a value equal to: "text", 'number', 'password', 'email', 'range', 'search', 'tel', 'url', 'hidden'; default 'text'): The type of control to render.
- name (string; optional): The name of the control, which is submitted with the form data.
- pattern (string; optional): A regular expression that the control's value is checked against. The pattern must match the entire value, not just some subset. Use the title attribute to describe the pattern to help the user. This attribute applies when the value of the type attribute is text, search, tel, url, email, or password, otherwise it is ignored. The regular expression language is the same as JavaScript RegExp algorithm, with the 'u' parameter that makes it treat the pattern as a sequence of unicode code points. The pattern is not surrounded by forward slashes.
- placeholder (string | number; optional): A hint to the user of what can be entered in the control . The placeholder text must not contain carriage returns or line-feeds. Note: Do not use the placeholder attribute instead of a <label> element, their purposes are different. The <label> attribute describes the role of the form element (i.e. it indicates what kind of information is expected), and the placeholder attribute is a hint about the format that the content should take. There are cases in which the placeholder attribute is never displayed to the user, so the form must be understandable without it.
- n_submit (number; default 0): Number of times the `Enter` key was pressed while the input had focus.
- n_submit_timestamp (number; default -1): Last time that `Enter` was pressed.
- loading_state (dict; optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading
- persistence (boolean | string | number; optional): Used to allow user interactions in this component to be persisted when
the component - or the page - is refreshed. If `persisted` is truthy and
hasn't changed from its previous value, a `value` that the user has
changed while using the app will keep that change, as long as
the new `value` also matches what was given originally.
Used in conjunction with `persistence_type`.
- persisted_props (list of a value equal to: 'value.nested_value's; default ['value.nested_value']): Properties whose user interactions will persist after refreshing the
component or the page. Since only `value` is allowed this prop can
normally be ignored.
- persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'): Where persisted user changes will be stored:
memory: only kept in memory, reset on page refresh.
local: window.localStorage, data is kept after the browser quit.
session: window.sessionStorage, data is cleared once the browser quit."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, value=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, debounce=Component.UNDEFINED, type=Component.UNDEFINED, name=Component.UNDEFINED, pattern=Component.UNDEFINED, placeholder=Component.UNDEFINED, n_submit=Component.UNDEFINED, n_submit_timestamp=Component.UNDEFINED, loading_state=Component.UNDEFINED, persistence=Component.UNDEFINED, persisted_props=Component.UNDEFINED, persistence_type=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'value', 'style', 'className', 'debounce', 'type', 'name', 'pattern', 'placeholder', 'n_submit', 'n_submit_timestamp', 'loading_state', 'persistence', 'persisted_props', 'persistence_type']
        self._type = 'MyPersistedComponentNested'
        self._namespace = 'dash_generator_test_component_persisted_nested'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'value', 'style', 'className', 'debounce', 'type', 'name', 'pattern', 'placeholder', 'n_submit', 'n_submit_timestamp', 'loading_state', 'persistence', 'persisted_props', 'persistence_type']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(MyPersistedComponentNested, self).__init__(**args)
