# AUTO GENERATED FILE - DO NOT EDIT

dccDatePickerRange <- function(id=NULL, start_date=NULL, start_date_id=NULL, end_date_id=NULL, end_date=NULL, min_date_allowed=NULL, max_date_allowed=NULL, initial_visible_month=NULL, start_date_placeholder_text=NULL, end_date_placeholder_text=NULL, day_size=NULL, calendar_orientation=NULL, is_RTL=NULL, reopen_calendar_on_clear=NULL, number_of_months_shown=NULL, with_portal=NULL, with_full_screen_portal=NULL, first_day_of_week=NULL, minimum_nights=NULL, stay_open_on_select=NULL, show_outside_days=NULL, month_format=NULL, display_format=NULL, disabled=NULL, clearable=NULL, style=NULL, className=NULL, updatemode=NULL, loading_state=NULL) {
    
    props <- list(id=id, start_date=start_date, start_date_id=start_date_id, end_date_id=end_date_id, end_date=end_date, min_date_allowed=min_date_allowed, max_date_allowed=max_date_allowed, initial_visible_month=initial_visible_month, start_date_placeholder_text=start_date_placeholder_text, end_date_placeholder_text=end_date_placeholder_text, day_size=day_size, calendar_orientation=calendar_orientation, is_RTL=is_RTL, reopen_calendar_on_clear=reopen_calendar_on_clear, number_of_months_shown=number_of_months_shown, with_portal=with_portal, with_full_screen_portal=with_full_screen_portal, first_day_of_week=first_day_of_week, minimum_nights=minimum_nights, stay_open_on_select=stay_open_on_select, show_outside_days=show_outside_days, month_format=month_format, display_format=display_format, disabled=disabled, clearable=clearable, style=style, className=className, updatemode=updatemode, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'DatePickerRange',
        namespace = 'dash_core_components',
        propNames = c('id', 'start_date', 'start_date_id', 'end_date_id', 'end_date', 'min_date_allowed', 'max_date_allowed', 'initial_visible_month', 'start_date_placeholder_text', 'end_date_placeholder_text', 'day_size', 'calendar_orientation', 'is_RTL', 'reopen_calendar_on_clear', 'number_of_months_shown', 'with_portal', 'with_full_screen_portal', 'first_day_of_week', 'minimum_nights', 'stay_open_on_select', 'show_outside_days', 'month_format', 'display_format', 'disabled', 'clearable', 'style', 'className', 'updatemode', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
