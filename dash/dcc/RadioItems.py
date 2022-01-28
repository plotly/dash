# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class RadioItems(Component):
    """A RadioItems component.
    RadioItems is a component that encapsulates several radio item inputs.
    The values and labels of the RadioItems is specified in the `options`
    property and the seleced item is specified with the `value` property.
    Each radio item is rendered as an input with a surrounding label.

    Keyword arguments:

    - options (list of dicts; optional):
        An array of options, or inline dictionary of options.

        `options` is a list of string | number | booleans | dict | list of
        dicts with keys:

        - disabled (boolean; optional):
            If True, this option is disabled and cannot be selected.

        - label (string | number | boolean; required):
            The option's label.

        - title (string; optional):
            The HTML 'title' attribute for the option. Allows for
            information on hover. For more information on this attribute,
            see
            https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title.

        - value (string | number | boolean; required):
            The value of the option. This value corresponds to the items
            specified in the `value` property.

    - value (string | number | boolean; optional):
        The currently selected value.

    - inline (boolean; default False):
        Indicates whether labelStyle should be inline or not True:
        Automatically set { 'display': 'inline-block' } to labelStyle
        False: No additional styles are passed into labelStyle.

    - style (dict; optional):
        The style of the container (div).

    - className (string; optional):
        The class of the container (div).

    - inputStyle (dict; optional):
        The style of the <input> radio element.

    - inputClassName (string; default ''):
        The class of the <input> radio element.

    - labelStyle (dict; optional):
        The style of the <label> that wraps the radio input  and the
        option's label.

    - labelClassName (string; default ''):
        The class of the <label> that wraps the radio input  and the
        option's label.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

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

    - persistence (boolean | string | number; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `value` that
        the user has changed while using the app will keep that change, as
        long as the new `value` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (list of a value equal to: 'value's; default ['value']):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `value` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit."""

    @_explicitize_args
    def __init__(
        self,
        options=Component.UNDEFINED,
        value=Component.UNDEFINED,
        inline=Component.UNDEFINED,
        style=Component.UNDEFINED,
        className=Component.UNDEFINED,
        inputStyle=Component.UNDEFINED,
        inputClassName=Component.UNDEFINED,
        labelStyle=Component.UNDEFINED,
        labelClassName=Component.UNDEFINED,
        id=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        persistence=Component.UNDEFINED,
        persisted_props=Component.UNDEFINED,
        persistence_type=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "options",
            "value",
            "inline",
            "style",
            "className",
            "inputStyle",
            "inputClassName",
            "labelStyle",
            "labelClassName",
            "id",
            "loading_state",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self._type = "RadioItems"
        self._namespace = "dash_core_components"
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "options",
            "value",
            "inline",
            "style",
            "className",
            "inputStyle",
            "inputClassName",
            "labelStyle",
            "labelClassName",
            "id",
            "loading_state",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in []:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(RadioItems, self).__init__(**args)
