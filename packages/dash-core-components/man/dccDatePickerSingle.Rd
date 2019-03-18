% Auto-generated: do not edit by hand
\name{dccDatePickerSingle}

\alias{dccDatePickerSingle}

\title{DatePickerSingle component}

\description{
DatePickerSingle is a tailor made component designed for selecting a single day off of a calendar.  The DatePicker integrates well with the Python datetime module with the startDate and endDate being returned in a string format suitable for creating datetime objects.  This component is based off of Airbnb's react-dates react component which can be found here: https://github.com/airbnb/react-dates
}

\usage{
dccDatePickerSingle(id=NULL, date=NULL, min_date_allowed=NULL, max_date_allowed=NULL, initial_visible_month=NULL, day_size=NULL, calendar_orientation=NULL, is_RTL=NULL, placeholder=NULL, reopen_calendar_on_clear=NULL, number_of_months_shown=NULL, with_portal=NULL, with_full_screen_portal=NULL, first_day_of_week=NULL, stay_open_on_select=NULL, show_outside_days=NULL, month_format=NULL, display_format=NULL, disabled=NULL, clearable=NULL, style=NULL, className=NULL, loading_state=NULL, ...)
}

\arguments{
\item{id}{}

\item{date}{Specifies the starting date for the component, best practice is to pass
value via datetime object}

\item{min_date_allowed}{Specifies the lowest selectable date for the component.
Accepts datetime.datetime objects or strings
in the format 'YYYY-MM-DD'}

\item{max_date_allowed}{Specifies the highest selectable date for the component.
Accepts datetime.datetime objects or strings
in the format 'YYYY-MM-DD'}

\item{initial_visible_month}{Specifies the month that is initially presented when the user
opens the calendar. Accepts datetime.datetime objects or strings
in the format 'YYYY-MM-DD'}

\item{day_size}{Size of rendered calendar days, higher number
means bigger day size and larger calendar overall}

\item{calendar_orientation}{Orientation of calendar, either vertical or horizontal.
Valid options are 'vertical' or 'horizontal'.}

\item{is_RTL}{Determines whether the calendar and days operate
from left to right or from right to left}

\item{placeholder}{Text that will be displayed in the input
box of the date picker when no date is selected.
Default value is 'Start Date'}

\item{reopen_calendar_on_clear}{If True, the calendar will automatically open when cleared}

\item{number_of_months_shown}{Number of calendar months that are shown when calendar is opened}

\item{with_portal}{If True, calendar will open in a screen overlay portal,
not supported on vertical calendar}

\item{with_full_screen_portal}{If True, calendar will open in a full screen overlay portal, will
take precedent over 'withPortal' if both are set to True,
not supported on vertical calendar}

\item{first_day_of_week}{Specifies what day is the first day of the week, values must be
from [0, ..., 6] with 0 denoting Sunday and 6 denoting Saturday}

\item{stay_open_on_select}{If True the calendar will not close when the user has selected a value
and will wait until the user clicks off the calendar}

\item{show_outside_days}{If True the calendar will display days that rollover into
the next month}

\item{month_format}{Specifies the format that the month will be displayed in the calendar,
valid formats are variations of "MM YY". For example:
"MM YY" renders as '05 97' for May 1997
"MMMM, YYYY" renders as 'May, 1997' for May 1997
"MMM, YY" renders as 'Sep, 97' for September 1997}

\item{display_format}{Specifies the format that the selected dates will be displayed
valid formats are variations of "MM YY DD". For example:
"MM YY DD" renders as '05 10 97' for May 10th 1997
"MMMM, YY" renders as 'May, 1997' for May 10th 1997
"M, D, YYYY" renders as '07, 10, 1997' for September 10th 1997
"MMMM" renders as 'May' for May 10 1997}

\item{disabled}{If True, no dates can be selected.}

\item{clearable}{Whether or not the dropdown is "clearable", that is, whether or
not a small "x" appears on the right of the dropdown that removes
the selected value.}

\item{style}{CSS styles appended to wrapper div}

\item{className}{Appends a CSS class to the wrapper div component.}

\item{loading_state}{Object that holds the loading state object coming from dash-renderer}
}
