# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Checklist(Component):
    """A Checklist component.
    Checklist is a component that encapsulates several checkboxes.
    The values and labels of the checklist are specified in the `options`
    property and the checked items are specified with the `value` property.
    Each checkbox is rendered as an input with a surrounding label.

    Keyword arguments:

    - options (list of dicts; optional):
        An array of options.

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

    - value (list of string | number | booleans; optional):
        The currently selected value.

    - inline (boolean; default False):
        Indicates whether the options labels should be displayed inline
        (True=horizontal) or in a block (False=vertical).

    - className (string; optional):
        The class of the container (div).

    - inputStyle (dict; optional):
        The style of the <input> checkbox element.

    - inputClassName (string; default ''):
        The class of the <input> checkbox element.

    - labelStyle (dict; optional):
        The style of the <label> that wraps the checkbox input  and the
        option's label.

    - labelClassName (string; default ''):
        The class of the <label> that wraps the checkbox input  and the
        option's label.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

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
    _type = "Checklist"
    Options = TypedDict(
        "Options",
        {
            "label": typing.Union[
                str,
                int,
                float,
                ComponentType,
                typing.Sequence[typing.Union[str, int, float, ComponentType]],
            ],
            "value": typing.Union[
                str,
                typing.Union[
                    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
                ],
                bool,
            ],
            "disabled": NotRequired[bool],
            "title": NotRequired[str],
        },
    )

    _explicitize_dash_init = True

    def __init__(
        self,
        options: typing.Optional[
            typing.Union[
                typing.Sequence[
                    typing.Union[
                        str,
                        typing.Union[
                            typing.SupportsFloat,
                            typing.SupportsInt,
                            typing.SupportsComplex,
                        ],
                        bool,
                    ]
                ],
                dict,
                typing.Sequence["Options"],
            ]
        ] = None,
        value: typing.Optional[
            typing.Sequence[
                typing.Union[
                    str,
                    typing.Union[
                        typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
                    ],
                    bool,
                ]
            ]
        ] = None,
        inline: typing.Optional[bool] = None,
        className: typing.Optional[str] = None,
        style: typing.Optional[typing.Any] = None,
        inputStyle: typing.Optional[dict] = None,
        inputClassName: typing.Optional[str] = None,
        labelStyle: typing.Optional[dict] = None,
        labelClassName: typing.Optional[str] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        persistence: typing.Optional[
            typing.Union[
                bool,
                str,
                typing.Union[
                    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
                ],
            ]
        ] = None,
        persisted_props: typing.Optional[typing.Sequence[Literal["value"]]] = None,
        persistence_type: typing.Optional[Literal["local", "session", "memory"]] = None,
        **kwargs
    ):
        self._prop_names = [
            "options",
            "value",
            "inline",
            "className",
            "style",
            "inputStyle",
            "inputClassName",
            "labelStyle",
            "labelClassName",
            "id",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "options",
            "value",
            "inline",
            "className",
            "style",
            "inputStyle",
            "inputClassName",
            "labelStyle",
            "labelClassName",
            "id",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Checklist, self).__init__(**args)
