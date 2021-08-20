# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Iframe(Component):
    """An Iframe component.
    Iframe is a wrapper for the <iframe> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The children of this component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - accessKey (string; optional):
        Keyboard shortcut to activate or add focus to the element.

    - allow (string; optional):
        Specifies a feature-policy for the iframe.

    - aria-* (string; optional):
        A wildcard aria attribute.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

    - contentEditable (string; optional):
        Indicates whether the element's content is editable.

    - contextMenu (string; optional):
        Defines the ID of a <menu> element which will serve as the
        element's context menu.

    - data-* (string; optional):
        A wildcard data attribute.

    - dir (string; optional):
        Defines the text direction. Allowed values are ltr (Left-To-Right)
        or rtl (Right-To-Left).

    - draggable (string; optional):
        Defines whether the element can be dragged.

    - height (string | number; optional):
        Specifies the height of elements listed here. For all other
        elements, use the CSS height property.        Note: In some
        instances, such as <div>, this is a legacy attribute, in which
        case the CSS height property should be used instead.

    - hidden (a value equal to: 'hidden', 'HIDDEN' | boolean; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

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

    - name (string; optional):
        Name of the element. For example used by the server to identify
        the fields in form submits.

    - referrerPolicy (string; optional):
        Specifies which referrer is sent when fetching the resource.

    - role (string; optional):
        The ARIA role attribute.

    - sandbox (string; optional):
        Stops a document loaded in an iframe from using certain features
        (such as submitting forms or opening new windows).

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - src (string; optional):
        The URL of the embeddable content.

    - srcDoc (string; optional)

    - style (dict; optional):
        Defines CSS styles which will override styles previously set.

    - tabIndex (string; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element.

    - width (string | number; optional):
        For the elements listed here, this establishes the element's
        width.        Note: For all other instances, such as <div>, this
        is a legacy attribute, in which case the CSS width property should
        be used instead."""

    @_explicitize_args
    def __init__(
        self,
        children=None,
        id=Component.UNDEFINED,
        n_clicks=Component.UNDEFINED,
        n_clicks_timestamp=Component.UNDEFINED,
        key=Component.UNDEFINED,
        role=Component.UNDEFINED,
        allow=Component.UNDEFINED,
        height=Component.UNDEFINED,
        name=Component.UNDEFINED,
        referrerPolicy=Component.UNDEFINED,
        sandbox=Component.UNDEFINED,
        src=Component.UNDEFINED,
        srcDoc=Component.UNDEFINED,
        width=Component.UNDEFINED,
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
            "allow",
            "aria-*",
            "className",
            "contentEditable",
            "contextMenu",
            "data-*",
            "dir",
            "draggable",
            "height",
            "hidden",
            "key",
            "lang",
            "loading_state",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "referrerPolicy",
            "role",
            "sandbox",
            "spellCheck",
            "src",
            "srcDoc",
            "style",
            "tabIndex",
            "title",
            "width",
        ]
        self._type = "Iframe"
        self._namespace = "dash_html_components"
        self._valid_wildcard_attributes = ["data-", "aria-"]
        self.available_properties = [
            "children",
            "id",
            "accessKey",
            "allow",
            "aria-*",
            "className",
            "contentEditable",
            "contextMenu",
            "data-*",
            "dir",
            "draggable",
            "height",
            "hidden",
            "key",
            "lang",
            "loading_state",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "referrerPolicy",
            "role",
            "sandbox",
            "spellCheck",
            "src",
            "srcDoc",
            "style",
            "tabIndex",
            "title",
            "width",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in []:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(Iframe, self).__init__(children=children, **args)
