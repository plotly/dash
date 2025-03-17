# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
import numbers  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal  # noqa: F401
from dash.development.base_component import Component, _explicitize_args

try:
    from dash.development.base_component import ComponentType  # noqa: F401
except ImportError:
    ComponentType = typing.TypeVar("ComponentType", bound=Component)


import datetime


class DatePickerSingle(Component):
    """A DatePickerSingle component.
    DatePickerSingle is a tailor made component designed for selecting
    a single day off of a calendar.

    The DatePicker integrates well with the Python datetime module with the
    startDate and endDate being returned in a string format suitable for
    creating datetime objects.

    This component is based off of Airbnb's react-dates react component
    which can be found here: https://github.com/airbnb/react-dates

    Keyword arguments:

    - date (string; optional):
        Specifies the starting date for the component, best practice is to
        pass value via datetime object.

    - min_date_allowed (string; optional):
        Specifies the lowest selectable date for the component. Accepts
        datetime.datetime objects or strings in the format 'YYYY-MM-DD'.

    - max_date_allowed (string; optional):
        Specifies the highest selectable date for the component. Accepts
        datetime.datetime objects or strings in the format 'YYYY-MM-DD'.

    - disabled_days (list of strings; optional):
        Specifies additional days between min_date_allowed and
        max_date_allowed that should be disabled. Accepted
        datetime.datetime objects or strings in the format 'YYYY-MM-DD'.

    - placeholder (string; optional):
        Text that will be displayed in the input box of the date picker
        when no date is selected. Default value is 'Start Date'.

    - initial_visible_month (string; optional):
        Specifies the month that is initially presented when the user
        opens the calendar. Accepts datetime.datetime objects or strings
        in the format 'YYYY-MM-DD'.

    - clearable (boolean; default False):
        Whether or not the dropdown is \"clearable\", that is, whether or
        not a small \"x\" appears on the right of the dropdown that
        removes the selected value.

    - reopen_calendar_on_clear (boolean; default False):
        If True, the calendar will automatically open when cleared.

    - display_format (string; optional):
        Specifies the format that the selected dates will be displayed
        valid formats are variations of \"MM YY DD\". For example: \"MM YY
        DD\" renders as '05 10 97' for May 10th 1997 \"MMMM, YY\" renders
        as 'May, 1997' for May 10th 1997 \"M, D, YYYY\" renders as '07,
        10, 1997' for September 10th 1997 \"MMMM\" renders as 'May' for
        May 10 1997.

    - month_format (string; optional):
        Specifies the format that the month will be displayed in the
        calendar, valid formats are variations of \"MM YY\". For example:
        \"MM YY\" renders as '05 97' for May 1997 \"MMMM, YYYY\" renders
        as 'May, 1997' for May 1997 \"MMM, YY\" renders as 'Sep, 97' for
        September 1997.

    - first_day_of_week (a value equal to: 0, 1, 2, 3, 4, 5, 6; default 0):
        Specifies what day is the first day of the week, values must be
        from [0, ..., 6] with 0 denoting Sunday and 6 denoting Saturday.

    - show_outside_days (boolean; default True):
        If True the calendar will display days that rollover into the next
        month.

    - stay_open_on_select (boolean; default False):
        If True the calendar will not close when the user has selected a
        value and will wait until the user clicks off the calendar.

    - calendar_orientation (a value equal to: 'vertical', 'horizontal'; default 'horizontal'):
        Orientation of calendar, either vertical or horizontal. Valid
        options are 'vertical' or 'horizontal'.

    - number_of_months_shown (number; default 1):
        Number of calendar months that are shown when calendar is opened.

    - with_portal (boolean; default False):
        If True, calendar will open in a screen overlay portal, not
        supported on vertical calendar.

    - with_full_screen_portal (boolean; default False):
        If True, calendar will open in a full screen overlay portal, will
        take precedent over 'withPortal' if both are set to True, not
        supported on vertical calendar.

    - day_size (number; default 39):
        Size of rendered calendar days, higher number means bigger day
        size and larger calendar overall.

    - is_RTL (boolean; default False):
        Determines whether the calendar and days operate from left to
        right or from right to left.

    - disabled (boolean; default False):
        If True, no dates can be selected.

    - className (string; optional):
        Appends a CSS class to the wrapper div component.

    - id (string; optional):
        The ID of this component, used to identify dash components in
        callbacks. The ID needs to be unique across all of the components
        in an app.

    - persistence (boolean | string | number; optional):
        Used to allow user interactions in this component to be persisted
        when the component - or the page - is refreshed. If `persisted` is
        truthy and hasn't changed from its previous value, a `date` that
        the user has changed while using the app will keep that change, as
        long as the new `date` also matches what was given originally.
        Used in conjunction with `persistence_type`.

    - persisted_props (list of a value equal to: 'date's; default ['date']):
        Properties whose user interactions will persist after refreshing
        the component or the page. Since only `date` is allowed this prop
        can normally be ignored.

    - persistence_type (a value equal to: 'local', 'session', 'memory'; default 'local'):
        Where persisted user changes will be stored: memory: only kept in
        memory, reset on page refresh. local: window.localStorage, data is
        kept after the browser quit. session: window.sessionStorage, data
        is cleared once the browser quit."""

    _children_props = []
    _base_nodes = ["children"]
    _namespace = "dash_core_components"
    _type = "DatePickerSingle"

    @_explicitize_args
    def __init__(
        self,
        date: typing.Optional[typing.Union[str, datetime.datetime]] = None,
        min_date_allowed: typing.Optional[typing.Union[str, datetime.datetime]] = None,
        max_date_allowed: typing.Optional[typing.Union[str, datetime.datetime]] = None,
        disabled_days: typing.Optional[
            typing.Sequence[typing.Union[str, datetime.datetime]]
        ] = None,
        placeholder: typing.Optional[str] = None,
        initial_visible_month: typing.Optional[
            typing.Union[str, datetime.datetime]
        ] = None,
        clearable: typing.Optional[bool] = None,
        reopen_calendar_on_clear: typing.Optional[bool] = None,
        display_format: typing.Optional[str] = None,
        month_format: typing.Optional[str] = None,
        first_day_of_week: typing.Optional[Literal[0, 1, 2, 3, 4, 5, 6]] = None,
        show_outside_days: typing.Optional[bool] = None,
        stay_open_on_select: typing.Optional[bool] = None,
        calendar_orientation: typing.Optional[Literal["vertical", "horizontal"]] = None,
        number_of_months_shown: typing.Optional[
            typing.Union[int, float, numbers.Number]
        ] = None,
        with_portal: typing.Optional[bool] = None,
        with_full_screen_portal: typing.Optional[bool] = None,
        day_size: typing.Optional[typing.Union[int, float, numbers.Number]] = None,
        is_RTL: typing.Optional[bool] = None,
        disabled: typing.Optional[bool] = None,
        style: typing.Optional[typing.Any] = None,
        className: typing.Optional[str] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        persistence: typing.Optional[
            typing.Union[bool, str, typing.Union[int, float, numbers.Number]]
        ] = None,
        persisted_props: typing.Optional[typing.Sequence[Literal["date"]]] = None,
        persistence_type: typing.Optional[Literal["local", "session", "memory"]] = None,
        **kwargs
    ):
        self._prop_names = [
            "date",
            "min_date_allowed",
            "max_date_allowed",
            "disabled_days",
            "placeholder",
            "initial_visible_month",
            "clearable",
            "reopen_calendar_on_clear",
            "display_format",
            "month_format",
            "first_day_of_week",
            "show_outside_days",
            "stay_open_on_select",
            "calendar_orientation",
            "number_of_months_shown",
            "with_portal",
            "with_full_screen_portal",
            "day_size",
            "is_RTL",
            "disabled",
            "style",
            "className",
            "id",
            "persistence",
            "persisted_props",
            "persistence_type",
        ]
        self._valid_wildcard_attributes = []
        self.available_properties = [
            "date",
            "min_date_allowed",
            "max_date_allowed",
            "disabled_days",
            "placeholder",
            "initial_visible_month",
            "clearable",
            "reopen_calendar_on_clear",
            "display_format",
            "month_format",
            "first_day_of_week",
            "show_outside_days",
            "stay_open_on_select",
            "calendar_orientation",
            "number_of_months_shown",
            "with_portal",
            "with_full_screen_portal",
            "day_size",
            "is_RTL",
            "disabled",
            "style",
            "className",
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

        super(DatePickerSingle, self).__init__(**args)
