# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Audio(Component):
    """An Audio component.
    Audio is a wrapper for the <audio> HTML5 element.
    For detailed attribute info see:
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio

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

    - autoPlay (a value equal to: 'autoPlay', 'autoplay', 'AUTOPLAY' | boolean; optional):
        The audio or video should play as soon as possible.

    - className (string; optional):
        Often used with CSS to style elements with common properties.

    - contentEditable (string; optional):
        Indicates whether the element's content is editable.

    - controls (a value equal to: 'controls', 'CONTROLS' | boolean; optional):
        Indicates whether the browser should show playback controls to the
        user.

    - crossOrigin (string; optional):
        How the element handles cross-origin requests.

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

    - hidden (a value equal to: 'hidden', 'HIDDEN' | boolean; optional):
        Prevents rendering of given element, while keeping child elements,
        e.g. script elements, active.

    - key (string; optional):
        A unique identifier for the component, used to improve performance
        by React.js while rendering components See
        https://reactjs.org/docs/lists-and-keys.html for more info.

    - lang (string; optional):
        Defines the language used in the element.

    - loop (a value equal to: 'loop', 'LOOP' | boolean; optional):
        Indicates whether the media should start playing from the start
        when it's finished.

    - muted (a value equal to: 'muted', 'MUTED' | boolean; optional):
        Indicates whether the audio will be initially silenced on page
        load.

    - n_clicks (number; default 0):
        An integer that represents the number of times that this element
        has been clicked on.

    - n_clicks_timestamp (number; default -1):
        An integer that represents the time (in ms since 1970) at which
        n_clicks changed. This can be used to tell which button was
        changed most recently.

    - preload (string; optional):
        Indicates whether the whole resource, parts of it or nothing
        should be preloaded.

    - role (string; optional):
        Defines an explicit role for an element for use by assistive
        technologies.

    - spellCheck (string; optional):
        Indicates whether spell checking is allowed for the element.

    - src (string; optional):
        The URL of the embeddable content.

    - tabIndex (string | number; optional):
        Overrides the browser's default tab order and follows the one
        specified instead.

    - title (string; optional):
        Text to be displayed in a tooltip when hovering over the element."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_html_components"
    _type = "Audio"

    @_explicitize_args
    def __init__(
        self,
        children: typing.Optional[
            typing.Union[
                str,
                int,
                float,
                ComponentType,
                typing.Sequence[typing.Union[str, int, float, ComponentType]],
            ]
        ] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        n_clicks: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        n_clicks_timestamp: typing.Optional[
            typing.Union[int, float, numbers.Number]
        ] = None,
        disable_n_clicks: typing.Optional[bool] = None,
        key: typing.Optional[str] = None,
        autoPlay: typing.Optional[
            typing.Union[Literal["autoPlay", "autoplay", "AUTOPLAY"], bool]
        ] = None,
        controls: typing.Optional[
            typing.Union[Literal["controls", "CONTROLS"], bool]
        ] = None,
        crossOrigin: typing.Optional[str] = None,
        loop: typing.Optional[typing.Union[Literal["loop", "LOOP"], bool]] = None,
        muted: typing.Optional[typing.Union[Literal["muted", "MUTED"], bool]] = None,
        preload: typing.Optional[str] = None,
        src: typing.Optional[str] = None,
        accessKey: typing.Optional[str] = None,
        className: typing.Optional[str] = None,
        contentEditable: typing.Optional[str] = None,
        dir: typing.Optional[str] = None,
        draggable: typing.Optional[str] = None,
        hidden: typing.Optional[typing.Union[Literal["hidden", "HIDDEN"], bool]] = None,
        lang: typing.Optional[str] = None,
        role: typing.Optional[str] = None,
        spellCheck: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        tabIndex: typing.Optional[
            typing.Union[str, typing.Union[int, float, numbers.Number]]
        ] = None,
        title: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "accessKey",
            "aria-*",
            "autoPlay",
            "className",
            "contentEditable",
            "controls",
            "crossOrigin",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "hidden",
            "key",
            "lang",
            "loop",
            "muted",
            "n_clicks",
            "n_clicks_timestamp",
            "preload",
            "role",
            "spellCheck",
            "src",
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
            "autoPlay",
            "className",
            "contentEditable",
            "controls",
            "crossOrigin",
            "data-*",
            "dir",
            "disable_n_clicks",
            "draggable",
            "hidden",
            "key",
            "lang",
            "loop",
            "muted",
            "n_clicks",
            "n_clicks_timestamp",
            "preload",
            "role",
            "spellCheck",
            "src",
            "style",
            "tabIndex",
            "title",
        ]
        self.available_wildcard_properties = ["data-", "aria-"]
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(Audio, self).__init__(children=children, **args)
