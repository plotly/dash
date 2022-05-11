# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


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

    @_explicitize_args
    def __init__(
        self,
        id=Component.REQUIRED,
        storage_type=Component.UNDEFINED,
        data=Component.UNDEFINED,
        clear_data=Component.UNDEFINED,
        modified_timestamp=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "id",
            "clear_data",
            "data",
            "modified_timestamp",
            "storage_type",
        ]
        self._type = "Store"
        self._namespace = "dash_core_components"
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
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in ["id"]:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(Store, self).__init__(**args)
