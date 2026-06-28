# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args
try:
    from dash.types import NumberType  # noqa: F401
except ImportError:
    # Backwards compatibility for dash<=4.1.0
    if typing.TYPE_CHECKING:
        raise
    NumberType = typing.Union[  # noqa: F401
        typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
    ]

ComponentSingleType = typing.Union[str, int, float, Component, None]
ComponentType = typing.Union[
    ComponentSingleType,
    typing.Sequence[ComponentSingleType],
]


class Button(Component):
    """A Button component.
A Button component. 
 Used as a part of Upload component.

Keyword arguments:

- btnClass (default 'dash-uploader-btn'):
    The CSS class for the button.

- disabled (default False):
    Is disabled, the component  is not shown.

- isUploading (default False):
    Is True, the parent component   has upload in progress.

- onClick (default () => { }):
    Function to call when clicked.

- text (default ''):
    The text on the button."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_uploader'
    _type = 'Button'


    def __init__(
        self,
        text: typing.Optional[typing.Any] = None,
        btnClass: typing.Optional[typing.Any] = None,
        onClick: typing.Optional[typing.Any] = None,
        disabled: typing.Optional[typing.Any] = None,
        isUploading: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['btnClass', 'disabled', 'isUploading', 'onClick', 'text']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['btnClass', 'disabled', 'isUploading', 'onClick', 'text']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Button, self).__init__(**args)

setattr(Button, "__init__", _explicitize_args(Button.__init__))
