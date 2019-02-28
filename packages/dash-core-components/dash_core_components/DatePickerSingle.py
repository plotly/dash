# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


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
- id (string; optional)
- date (string; optional): Specifies the starting date for the component, best practice is to pass
value via datetime object
- min_date_allowed (string; optional): Specifies the lowest selectable date for the component.
Accepts datetime.datetime objects or strings
in the format 'YYYY-MM-DD'
- max_date_allowed (string; optional): Specifies the highest selectable date for the component.
Accepts datetime.datetime objects or strings
in the format 'YYYY-MM-DD'
- initial_visible_month (string; optional): Specifies the month that is initially presented when the user
opens the calendar. Accepts datetime.datetime objects or strings
in the format 'YYYY-MM-DD'
- day_size (number; optional): Size of rendered calendar days, higher number
means bigger day size and larger calendar overall
- calendar_orientation (a value equal to: 'vertical', 'horizontal'; optional): Orientation of calendar, either vertical or horizontal.
Valid options are 'vertical' or 'horizontal'.
- is_RTL (boolean; optional): Determines whether the calendar and days operate
from left to right or from right to left
- placeholder (string; optional): Text that will be displayed in the input
box of the date picker when no date is selected.
Default value is 'Start Date'
- reopen_calendar_on_clear (boolean; optional): If True, the calendar will automatically open when cleared
- number_of_months_shown (number; optional): Number of calendar months that are shown when calendar is opened
- with_portal (boolean; optional): If True, calendar will open in a screen overlay portal,
not supported on vertical calendar
- with_full_screen_portal (boolean; optional): If True, calendar will open in a full screen overlay portal, will
take precedent over 'withPortal' if both are set to True,
not supported on vertical calendar
- first_day_of_week (a value equal to: 0, 1, 2, 3, 4, 5, 6; optional): Specifies what day is the first day of the week, values must be
from [0, ..., 6] with 0 denoting Sunday and 6 denoting Saturday
- stay_open_on_select (boolean; optional): If True the calendar will not close when the user has selected a value
and will wait until the user clicks off the calendar
- show_outside_days (boolean; optional): If True the calendar will display days that rollover into
the next month
- month_format (string; optional): Specifies the format that the month will be displayed in the calendar,
valid formats are variations of "MM YY". For example:
"MM YY" renders as '05 97' for May 1997
"MMMM, YYYY" renders as 'May, 1997' for May 1997
"MMM, YY" renders as 'Sep, 97' for September 1997
- display_format (string; optional): Specifies the format that the selected dates will be displayed
valid formats are variations of "MM YY DD". For example:
"MM YY DD" renders as '05 10 97' for May 10th 1997
"MMMM, YY" renders as 'May, 1997' for May 10th 1997
"M, D, YYYY" renders as '07, 10, 1997' for September 10th 1997
"MMMM" renders as 'May' for May 10 1997
- disabled (boolean; optional): If True, no dates can be selected.
- clearable (boolean; optional): Whether or not the dropdown is "clearable", that is, whether or
not a small "x" appears on the right of the dropdown that removes
the selected value.
- style (dict; optional): CSS styles appended to wrapper div
- className (string; optional): Appends a CSS class to the wrapper div component.
- loading_state (optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, date=Component.UNDEFINED, min_date_allowed=Component.UNDEFINED, max_date_allowed=Component.UNDEFINED, initial_visible_month=Component.UNDEFINED, day_size=Component.UNDEFINED, calendar_orientation=Component.UNDEFINED, is_RTL=Component.UNDEFINED, placeholder=Component.UNDEFINED, reopen_calendar_on_clear=Component.UNDEFINED, number_of_months_shown=Component.UNDEFINED, with_portal=Component.UNDEFINED, with_full_screen_portal=Component.UNDEFINED, first_day_of_week=Component.UNDEFINED, stay_open_on_select=Component.UNDEFINED, show_outside_days=Component.UNDEFINED, month_format=Component.UNDEFINED, display_format=Component.UNDEFINED, disabled=Component.UNDEFINED, clearable=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'date', 'min_date_allowed', 'max_date_allowed', 'initial_visible_month', 'day_size', 'calendar_orientation', 'is_RTL', 'placeholder', 'reopen_calendar_on_clear', 'number_of_months_shown', 'with_portal', 'with_full_screen_portal', 'first_day_of_week', 'stay_open_on_select', 'show_outside_days', 'month_format', 'display_format', 'disabled', 'clearable', 'style', 'className', 'loading_state']
        self._type = 'DatePickerSingle'
        self._namespace = 'dash_core_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'date', 'min_date_allowed', 'max_date_allowed', 'initial_visible_month', 'day_size', 'calendar_orientation', 'is_RTL', 'placeholder', 'reopen_calendar_on_clear', 'number_of_months_shown', 'with_portal', 'with_full_screen_portal', 'first_day_of_week', 'stay_open_on_select', 'show_outside_days', 'month_format', 'display_format', 'disabled', 'clearable', 'style', 'className', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DatePickerSingle, self).__init__(**args)
