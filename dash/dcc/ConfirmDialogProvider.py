# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class ConfirmDialogProvider(Component):
    """A ConfirmDialogProvider component.
    A wrapper component that will display a confirmation dialog
    when its child component has been clicked on.

    For example:
    ```
    dcc.ConfirmDialogProvider(
        html.Button('click me', id='btn'),
        message='Danger - Are you sure you want to continue.'
        id='confirm')
    ```

    Keyword arguments:

    - children (boolean | number | string | dict | list; optional):
        The children to hijack clicks from and display the popup.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - cancel_n_clicks (number; default 0):
        Number of times the popup was canceled.

    - cancel_n_clicks_timestamp (number; default -1):
        Last time the cancel button was clicked.

    - displayed (boolean; optional):
        Is the modal currently displayed.

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

    - message (string; optional):
        Message to show in the popup.

    - submit_n_clicks (number; default 0):
        Number of times the submit was clicked.

    - submit_n_clicks_timestamp (number; default -1):
        Last time the submit button was clicked."""

    @_explicitize_args
    def __init__(
        self,
        children=None,
        id=Component.UNDEFINED,
        message=Component.UNDEFINED,
        submit_n_clicks=Component.UNDEFINED,
        submit_n_clicks_timestamp=Component.UNDEFINED,
        cancel_n_clicks=Component.UNDEFINED,
        cancel_n_clicks_timestamp=Component.UNDEFINED,
        displayed=Component.UNDEFINED,
        loading_state=Component.UNDEFINED,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "cancel_n_clicks",
            "cancel_n_clicks_timestamp",
            "displayed",
            "loading_state",
            "message",
            "submit_n_clicks",
            "submit_n_clicks_timestamp",
        ]
        self._type = "ConfirmDialogProvider"
        self._namespace = "dash_core_components"
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "cancel_n_clicks",
            "cancel_n_clicks_timestamp",
            "displayed",
            "loading_state",
            "message",
            "submit_n_clicks",
            "submit_n_clicks_timestamp",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != "children"}
        for k in []:
            if k not in args:
                raise TypeError("Required argument `" + k + "` was not specified.")
        super(ConfirmDialogProvider, self).__init__(children=children, **args)
