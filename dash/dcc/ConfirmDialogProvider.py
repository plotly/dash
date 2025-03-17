# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


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

    - message (string; optional):
        Message to show in the popup.

    - submit_n_clicks (number; default 0):
        Number of times the submit was clicked.

    - submit_n_clicks_timestamp (number; default -1):
        Last time the submit button was clicked."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "ConfirmDialogProvider"

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
        message: typing.Optional[str] = None,
        submit_n_clicks: typing.Optional[
            typing.Union[int, float, numbers.Number]
        ] = None,
        submit_n_clicks_timestamp: typing.Optional[
            typing.Union[int, float, numbers.Number]
        ] = None,
        cancel_n_clicks: typing.Optional[
            typing.Union[int, float, numbers.Number]
        ] = None,
        cancel_n_clicks_timestamp: typing.Optional[
            typing.Union[int, float, numbers.Number]
        ] = None,
        displayed: typing.Optional[bool] = None,
        **kwargs
    ):
        self._prop_names = [
            "children",
            "id",
            "cancel_n_clicks",
            "cancel_n_clicks_timestamp",
            "displayed",
            "message",
            "submit_n_clicks",
            "submit_n_clicks_timestamp",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "children",
            "id",
            "cancel_n_clicks",
            "cancel_n_clicks_timestamp",
            "displayed",
            "message",
            "submit_n_clicks",
            "submit_n_clicks_timestamp",
        ]
        self.available_wildcard_properties = []
        _explicit_args = kwargs.pop("_explicit_args")
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != "children"}

        super(ConfirmDialogProvider, self).__init__(children=children, **args)
