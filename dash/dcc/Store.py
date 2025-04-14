# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


class Store(Component):
    """A Store component.
    Easily keep data on the client side with this component.
    The data is not inserted in the DOM.
    Data can be in memory, localStorage or sessionStorage.
    The data will be kept with the id as key.

    Keyword arguments:

    - id (string; required):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - clear_data (boolean; default False):
        Set to True to remove the data contained in `data_key`.

    - data (dict | list | number | string | boolean; optional):
        The stored data for the id.

    - modified_timestamp (number; default -1):
        The last time the storage was modified.

    - storage_type (a value equal to: 'local', 'session', 'memory'; default 'memory'):
        The type of the web storage.  memory: only kept in memory, reset
        on page refresh. local: window.localStorage, data is kept after
        the browser quit. session: window.sessionStorage, data is cleared
        once the browser quit."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "Store"

    _explicitize_dash_init = True

    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        storage_type: typing.Optional[Literal["local", "session", "memory"]] = None,
        data: typing.Optional[
            typing.Union[
                dict,
                typing.Sequence,
                typing.Union[
                    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
                ],
                str,
                bool,
            ]
        ] = None,
        clear_data: typing.Optional[bool] = None,
        modified_timestamp: typing.Optional[
            typing.Union[
                typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
            ]
        ] = None,
        **kwargs
    ):
        self._prop_names = [
            "id",
            "clear_data",
            "data",
            "modified_timestamp",
            "storage_type",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "id",
            "clear_data",
            "data",
            "modified_timestamp",
            "storage_type",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ["id"]:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")

        super(Store, self).__init__(**args)
