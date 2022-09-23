# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Select(Component):
    """A Select component.
    Select is a wrapper for the <select> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select

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

    - autoComplete (string; optional):
        Indicates whether controls in this form can by default have their
        values automatically completed by the browser.

    - autoFocus (a value equal to: 'autoFocus', 'autofocus', 'AUTOFOCUS' | boolean; optional):
        The element should be automatically focused after the page loaded.

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

    - disabled (a value equal to: 'disabled', 'DISABLED' | boolean; optional):
        Indicates whether the user can interact with the element.

    - draggable (string; optional):
        Defines whether the element can be dragged.

    - form (string; optional):
        Indicates the form that is the owner of the element.

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

    - multiple (a value equal to: 'multiple', 'MULTIPLE' | boolean; optional):
        Indicates whether multiple values can be entered in an input of
        the type email or file.

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

    - required (a value equal to: 'required', 'REQUIRED' | boolean; optional):
        Indicates whether this element is required to fill out or not.

    - role (string; optional):
        Defines an explicit role for an element for use by assistive
        technologies.

    - size (string | number; optional):
        Defines the width of the element (in pixels). If the element's
        type attribute is text or password then it's the number of
        characters.

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - style (dict; optional):
        Defines CSS styles which will override styles previously set.

    - tabIndex (string; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_html_components"
    _type = "Select"

    @_explicitize_args
    def __init__(
        self,
        children=None,
        id=Component.UNDEFINED,
        n_clicks=Component.UNDEFINED,
        n_clicks_timestamp=Component.UNDEFINED,
        key=Component.UNDEFINED,
        autoComplete=Component.UNDEFINED,
        autoFocus=Component.UNDEFINED,
        disabled=Component.UNDEFINED,
        form=Component.UNDEFINED,
        multiple=Component.UNDEFINED,
        name=Component.UNDEFINED,
        required=Component.UNDEFINED,
        size=Component.UNDEFINED,
        accessKey=Component.UNDEFINED,
        className=Component.UNDEFINED,
        contentEditable=Component.UNDEFINED,
        contextMenu=Component.UNDEFINED,
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
            "autoComplete",
            "autoFocus",
            "className",
            "contentEditable",
            "contextMenu",
            "data-*",
            "dir",
            "disabled",
            "draggable",
            "form",
            "hidden",
            "key",
            "lang",
            "loading_state",
            "multiple",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "required",
            "role",
            "size",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
        ]
        self._valid_wildcard_attributes = ["data-", "aria-"]
        self.available_properties = [
            "children",
            "id",
            "accessKey",
            "aria-*",
            "autoComplete",
            "autoFocus",
            "className",
            "contentEditable",
            "contextMenu",
            "data-*",
            "dir",
            "disabled",
            "draggable",
            "form",
            "hidden",
            "key",
            "lang",
            "loading_state",
            "multiple",
            "n_clicks",
            "n_clicks_timestamp",
            "name",
            "required",
            "role",
            "size",
            "spellCheck",
            "style",
            "tabIndex",
            "title",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Select, self).__init__(children=children, **args)
