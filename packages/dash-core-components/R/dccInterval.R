# AUTO GENERATED FILE - DO NOT EDIT

dccInterval <- function(id=NULL, interval=NULL, disabled=NULL, n_intervals=NULL, max_intervals=NULL) {
    
    component <- list(
        props = list(id=id, interval=interval, disabled=disabled, n_intervals=n_intervals, max_intervals=max_intervals),
        type = 'Interval',
        namespace = 'dash_core_components',
        propNames = c('id', 'interval', 'disabled', 'n_intervals', 'max_intervals'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)

    structure(component, class = c('dash_component', 'list'))
}