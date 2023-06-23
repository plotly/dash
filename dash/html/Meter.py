# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Meter(Component):
    """A Meter component.
    Meter is a wrapper for the <meter> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meter

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The children of this component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - accessKey (string; optional):
        Keyboard shortcut to activate or add focus to the element.

    - aria-* (string; optional):
        A wildcard aria attribute.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

    - contentEditable (string; optional):
        Indicates whether the element's content is editable.

    - data-* (string; optional):
        A wildcard data attribute.

    - dir (string; optional):
        Defines the text direction. Allowed values are ltr (Left-To-Right)
        or rtl (Right-To-Left).

    - disable_n_clicks (boolean; optional):
        When True, this will disable the n_clicks prop.  Use this to
        remove event listeners that may interfere with screen readers.

    - draggable (string; optional):
        Defines whether the element can be dragged.

    - form (string; optional):
        Indicates the form that is the owner of the element.

    - hidden (a value equal to: 'hidden', 'HIDDEN' | boolean; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

    - high (string; optional):
        Indicates the lower bound of the upper range.

    - key (string; optional):
        A unique identifier for the component, used to improve performance
        by React.js while rendering components See
        https://reactjs.org/docs/lists-and-keys.html for more info.

    - lang (string; optional):
        Defines the language used in the element.

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

    - low (string; optional):
        Indicates the upper bound of the lower range.

    - max (string | number; optional):
        Indicates the maximum value allowed.

    - min (string | number; optional):
        Indicates the minimum value allowed.

    - n_clicks (number; default 0):
        An integer that represents the number of times that this element
        has been clicked on.

    - n_clicks_timestamp (number; default -1):
        An integer that represents the time (in ms since 1970) at which
        n_clicks changed. This can be used to tell which button was
        changed most recently.

    - optimum (string; optional):
        Indicates the optimal numeric value.

    - role (string; optional):
        Defines an explicit role for an element for use by assistive
        technologies.

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - style (dict; optional):
        Defines CSS styles which will override styles previously set.

    - tabIndex (string; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element.

    - value (string; optional):
        Defines a default value which will be displayed in the element on
        page load."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_html_components"
    _type = "Meter"

    @_explicitize_args
    def __init__(
        self,
        children=None,
        id=Component.UNDEFINED,
        n_clicks=Component.UNDEFINED,
        n_clicks_timestamp=Component.UNDEFINED,
        disable_n_clicks=Component.UNDEFINED,
        key=Component.UNDEFINED,
        form=Component.UNDEFINED,
        high=Component.UNDEFINED,
        low=Component.UNDEFINED,
        max=Component.UNDEFINED,
        min=Component.UNDEFINED,
        optimum=Component.UNDEFINED,
        value=Component.UNDEFINED,
        accessKey=Component.UNDEFINED,
        className=Component.UNDEFINED,
        contentEditable=Component.UNDEFINED,
        dir=Component.UNDEFINED,
        draggable=Component.UNDEFINED,
        hidden=Component.UNDEFINED,
        lang=Component.UNDEFINED,
        role=Component.UNDEFINED,
        spellCheck=Component.UNDEFINED,
        style=Component.UNDEFINED,
        tabIndex=Component.UNDEFINED,
        title=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "accessKey",
            "aria-*",
            "className",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "form",
            "hidden",
            "high",
            "key",
            "lang",
            "loading_state",
            "low",
            "max",
            "min",
            "n_clicks",
            "n_clicks_timestamp",
            "optimum",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
            "value",
        ]
        self._valid_wildcard_attributes = ["data-", "aria-"]
        self.available_properties = [
            "children",
            "id",
            "accessKey",
            "aria-*",
            "className",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "form",
            "hidden",
            "high",
            "key",
            "lang",
            "loading_state",
            "low",
            "max",
            "min",
            "n_clicks",
            "n_clicks_timestamp",
            "optimum",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
            "value",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Meter, self).__init__(children=children, **args)
