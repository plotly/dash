# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Form(Component):
    """A Form component.
    Form is a wrapper for the <form> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form

    Keyword arguments:

    - children (a list of or a singular dash component, string or number; optional):
        The children of this component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - accept (string; optional):
        List of types the server accepts, typically a file type.

    - acceptCharset (string; optional):
        List of supported charsets.

    - accessKey (string; optional):
        Keyboard shortcut to activate or add focus to the element.

    - action (string; optional):
        The URI of a program that processes the information submitted via
        the form.

    - aria-* (string; optional):
        A wildcard aria attribute.

    - autoComplete (string; optional):
        Indicates whether controls in this form can by default have their
        values automatically completed by the browser.

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

    - encType (string; optional):
        Defines the content type of the form data when the method is POST.

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

    - method (string; optional):
        Defines which HTTP method to use when submitting the form. Can be
        GET (default) or POST.

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

    - noValidate (a value equal to: 'noValidate', 'novalidate', 'NOVALIDATE' | boolean; optional):
        This attribute indicates that the form shouldn't be validated when
        submitted.

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

    - target (string; optional):
        Specifies where to open the linked document (in the case of an <a>
        element) or where to display the response received (in the case of
        a <form> element).

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_html_components"
    _type = "Form"

    @_explicitize_args
    def __init__(
        self,
        children=None,
        id=Component.UNDEFINED,
        n_clicks=Component.UNDEFINED,
        n_clicks_timestamp=Component.UNDEFINED,
        disable_n_clicks=Component.UNDEFINED,
        key=Component.UNDEFINED,
        accept=Component.UNDEFINED,
        acceptCharset=Component.UNDEFINED,
        action=Component.UNDEFINED,
        autoComplete=Component.UNDEFINED,
        encType=Component.UNDEFINED,
        method=Component.UNDEFINED,
        name=Component.UNDEFINED,
        noValidate=Component.UNDEFINED,
        target=Component.UNDEFINED,
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
            "accept",
            "acceptCharset",
            "accessKey",
            "action",
            "aria-*",
            "autoComplete",
            "className",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "encType",
            "hidden",
            "key",
            "lang",
            "loading_state",
            "method",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "noValidate",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "target",
            "title",
        ]
        self._valid_wildcard_attributes = ["data-", "aria-"]
        self.available_properties = [
            "children",
            "id",
            "accept",
            "acceptCharset",
            "accessKey",
            "action",
            "aria-*",
            "autoComplete",
            "className",
            "contentEditable",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "encType",
            "hidden",
            "key",
            "lang",
            "loading_state",
            "method",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "noValidate",
            "role",
            "spellCheck",
            "style",
            "tabIndex",
            "target",
            "title",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Form, self).__init__(children=children, **args)
