# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Script(Component):
    """A Script component.
    Script is a wrapper for the <script> HTML5 element.

    CAUTION: <script> is included for completeness, but you cannot execute
    JavaScript code by providing it to a <script> element. Use a clientside
    callback for this purpose instead.

    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script

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

    - async (a value equal to: 'async', 'ASYNC' | boolean; optional):
        Executes the script asynchronously.

    - charSet (string; optional):
        Declares the character encoding of the page or script.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

    - contentEditable (string; optional):
        Indicates whether the element's content is editable.

    - contextMenu (string; optional):
        Defines the ID of a <menu> element which will serve as the
        element's context menu.

    - crossOrigin (string; optional):
        How the element handles cross-origin requests.

    - data-* (string; optional):
        A wildcard data attribute.

    - defer (a value equal to: 'defer', 'DEFER' | boolean; optional):
        Indicates that the script should be executed after the page has
        been parsed.

    - dir (string; optional):
        Defines the text direction. Allowed values are ltr (Left-To-Right)
        or rtl (Right-To-Left).

    - draggable (string; optional):
        Defines whether the element can be dragged.

    - hidden (a value equal to: 'hidden', 'HIDDEN' | boolean; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

    - integrity (string; optional):
        Specifies a Subresource Integrity value that allows browsers to
        verify what they fetch.

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

    - n_clicks (number; default 0):
        An integer that represents the number of times that this element
        has been clicked on.

    - n_clicks_timestamp (number; default -1):
        An integer that represents the time (in ms since 1970) at which
        n_clicks changed. This can be used to tell which button was
        changed most recently.

    - referrerPolicy (string; optional):
        Specifies which referrer is sent when fetching the resource.

    - role (string; optional):
        The ARIA role attribute.

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - src (string; optional):
        The URL of the embeddable content.

    - style (dict; optional):
        Defines CSS styles which will override styles previously set.

    - tabIndex (string; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element.

    - type (string; optional):
        Defines the type of the element."""

    @_explicitize_args
    def __init__(
        self,
        children=None,
        id=Component.UNDEFINED,
        n_clicks=Component.UNDEFINED,
        n_clicks_timestamp=Component.UNDEFINED,
        key=Component.UNDEFINED,
        role=Component.UNDEFINED,
        charSet=Component.UNDEFINED,
        crossOrigin=Component.UNDEFINED,
        defer=Component.UNDEFINED,
        integrity=Component.UNDEFINED,
        referrerPolicy=Component.UNDEFINED,
        src=Component.UNDEFINED,
        type=Component.UNDEFINED,
        accessKey=Component.UNDEFINED,
        className=Component.UNDEFINED,
        contentEditable=Component.UNDEFINED,
        contextMenu=Component.UNDEFINED,
        dir=Component.UNDEFINED,
        draggable=Component.UNDEFINED,
        hidden=Component.UNDEFINED,
        lang=Component.UNDEFINED,
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
            "async",
            "charSet",
            "className",
            "contentEditable",
            "contextMenu",
            "crossOrigin",
            "data-*",
            "defer",
            "dir",
            "draggable",
            "hidden",
            "integrity",
            "key",
            "lang",
            "loading_state",
            "n_clicks",
            "n_clicks_timestamp",
            "referrerPolicy",
            "role",
            "spellCheck",
            "src",
            "style",
            "tabIndex",
            "title",
            "type",
        ]
        self._type = "Script"
        self._namespace = "dash_html_components"
        self._valid_wildcard_attributes = ["data-", "aria-"]
        self.available_properties = [
            "children",
            "id",
            "accessKey",
            "aria-*",
            "async",
            "charSet",
            "className",
            "contentEditable",
            "contextMenu",
            "crossOrigin",
            "data-*",
            "defer",
            "dir",
            "draggable",
            "hidden",
            "integrity",
            "key",
            "lang",
            "loading_state",
            "n_clicks",
            "n_clicks_timestamp",
            "referrerPolicy",
            "role",
            "spellCheck",
            "src",
            "style",
            "tabIndex",
            "title",
            "type",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in []:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(Script, self).__init__(children=children, **args)
