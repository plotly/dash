# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Download(Component):
    """A Download component.
    The Download component opens a download dialog when the data property changes.

    Keyword arguments:

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks.

    - base64 (boolean; default False):
        Default value for base64, used when not set as part of the data
        property.

    - data (dict; optional):
        On change, a download is invoked.

        `data` is a dict with keys:

        - filename (string; required):
            Suggested filename in the download dialogue.

        - content (string; required):
            File content.

        - base64 (boolean; optional):
            Set to True, when data is base64 encoded.

        - type (string; optional):
            Blob type, usually a MIME-type.

    - type (string; default 'text/plain'):
        Default value for type, used when not set as part of the data
        property."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Download"
    Data = TypedDict(
        "Data",
        {
            "filename": str,
            "content": str,
            "base64": NotRequired[bool],
            "type": NotRequired[str],
        },
    )

    @_explicitize_args
    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        data: typing.Optional["Data"] = None,
        base64: typing.Optional[bool] = None,
        type: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ["id", "base64", "data", "type"]
        self._valid_wildcard_attributes = []
        self.available_properties = ["id", "base64", "data", "type"]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(Download, self).__init__(**args)
