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


class ProgressBar(Component):
    """A ProgressBar component.
A ProgressBar component. 
 Used as a part of Upload component.

Keyword arguments:

- isUploading (boolean; default False):
    The upload status (boolean).

- progressBar (number; default 0):
    The progressbar value."""
    _children_props: typing.List[str] = []
    _base_nodes = ['children']
    _namespace = 'dash_uploader'
    _type = 'ProgressBar'


    def __init__(
        self,
        progressBar: typing.Optional[NumberType] = None,
        isUploading: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = ['isUploading', 'progressBar']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['isUploading', 'progressBar']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(ProgressBar, self).__init__(**args)

setattr(ProgressBar, "__init__", _explicitize_args(ProgressBar.__init__))
