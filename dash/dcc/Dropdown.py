# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Dropdown(Component):
    """A Dropdown component.
    Dropdown is an interactive dropdown element for selecting one or more
    items.
    The values and labels of the dropdown items are specified in the `options`
    property and the selected item(s) are specified with the `value` property.

    Use a dropdown when you have many options (more than 5) or when you are
    constrained for space. Otherwise, you can use RadioItems or a Checklist,
    which have the benefit of showing the users all of the items at once.

    Keyword arguments:

    - options (list of dicts; optional):
        An array of options {label: [string|number], value:
        [string|number]}, an optional disabled field can be used for each
        option.

        `options` is a list of string | number | booleans | dict | list of
        dicts with keys:

        - label (a list of or a singular dash component, string or number; required):
            The option's label.

        - value (string | number | boolean; required):
            The value of the option. This value corresponds to the items
            specified in the `value` property.

        - disabled (boolean; optional):
            If True, this option is disabled and cannot be selected.

        - title (string; optional):
            The HTML 'title' attribute for the option. Allows for
            information on hover. For more information on this attribute,
            see
            https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title.

        - search (string; optional):
            Optional search value for the option, to use if the label is a
            component or provide a custom search value different from the
            label. If no search value and the label is a component, the
            `value` will be used for search.

    - value (string | number | boolean | list of string | number | booleans; optional):
        The value of the input. If `multi` is False (the default) then
        value is just a string that corresponds to the values provided in
        the `options` property. If `multi` is True, then multiple values
        can be selected at once, and `value` is an array of items with
        values corresponding to those in the `options` prop.

    - multi (boolean; default False):
        If True, the user can select multiple values.

    - clearable (boolean; default True):
        Whether or not the dropdown is \"clearable\", that is, whether or
        not a small \"x\" appears on the right of the dropdown that
        removes the selected value.

    - searchable (boolean; default True):
        Whether to enable the searching feature or not.

    - search_value (string; optional):
        The value typed in the DropDown for searching.

    - placeholder (string; optional):
        The grey, default text shown when no option is selected.

    - disabled (boolean; default False):
        If True, this dropdown is disabled and the selection cannot be
        changed.

    - optionHeight (number; default 35):
        height of each option. Can be increased when label lengths would
        wrap around.

    - maxHeight (number; default 200):
        height of the options dropdown.

    - style (dict; optional):
        Defines CSS styles which will override styles previously set.

    - className (string; optional):
        className of the dropdown element.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - loading_state (dict; optional):
        Object that holds the loading state object coming from
        dash-renderer.

        `loading_state` is a dict with keys:

        - is_loading (boolean; optional):
            Determines if the component is loading or not.

        - prop_name (string; optional):
            Holds which property is loading.

        - component_name (string; optional):
            Holds the name of the component that is loading.

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

    _children_props = ["options[].label"]
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Dropdown"

    @_explicitize_args
    def __init__(
        self,
        options=Component.UNDEFINED,
        value=Component.UNDEFINED,
        multi=Component.UNDEFINED,
        clearable=Component.UNDEFINED,
        searchable=Component.UNDEFINED,
        search_value=Component.UNDEFINED,
        placeholder=Component.UNDEFINED,
        disabled=Component.UNDEFINED,
        optionHeight=Component.UNDEFINED,
        maxHeight=Component.UNDEFINED,
        style=Component.UNDEFINED,
        className=Component.UNDEFINED,
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
            "multi",
            "clearable",
            "searchable",
            "search_value",
            "placeholder",
            "disabled",
            "optionHeight",
            "maxHeight",
            "style",
            "className",
            "id",
            "loading_state",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "options",
            "value",
            "multi",
            "clearable",
            "searchable",
            "search_value",
            "placeholder",
            "disabled",
            "optionHeight",
            "maxHeight",
            "style",
            "className",
            "id",
            "loading_state",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Dropdown, self).__init__(**args)
