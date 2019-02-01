# AUTO GENERATED FILE - DO NOT EDIT

coreDatePickerSingle <- function(id=NULL, date=NULL, min_date_allowed=NULL, max_date_allowed=NULL, initial_visible_month=NULL, day_size=NULL, calendar_orientation=NULL, is_RTL=NULL, placeholder=NULL, reopen_calendar_on_clear=NULL, number_of_months_shown=NULL, with_portal=NULL, with_full_screen_portal=NULL, first_day_of_week=NULL, stay_open_on_select=NULL, show_outside_days=NULL, month_format=NULL, display_format=NULL, disabled=NULL, clearable=NULL) {
    
    component <- list(
        props = list(id=id, date=date, min_date_allowed=min_date_allowed, max_date_allowed=max_date_allowed, initial_visible_month=initial_visible_month, day_size=day_size, calendar_orientation=calendar_orientation, is_RTL=is_RTL, placeholder=placeholder, reopen_calendar_on_clear=reopen_calendar_on_clear, number_of_months_shown=number_of_months_shown, with_portal=with_portal, with_full_screen_portal=with_full_screen_portal, first_day_of_week=first_day_of_week, stay_open_on_select=stay_open_on_select, show_outside_days=show_outside_days, month_format=month_format, display_format=display_format, disabled=disabled, clearable=clearable),
        type = 'DatePickerSingle',
        namespace = 'dash_core_components',
        propNames = c('id', 'date', 'min_date_allowed', 'max_date_allowed', 'initial_visible_month', 'day_size', 'calendar_orientation', 'is_RTL', 'placeholder', 'reopen_calendar_on_clear', 'number_of_months_shown', 'with_portal', 'with_full_screen_portal', 'first_day_of_week', 'stay_open_on_select', 'show_outside_days', 'month_format', 'display_format', 'disabled', 'clearable'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)

    structure(component, class = c('dash_component', 'list'))
}