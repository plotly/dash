# AUTO GENERATED FILE - DO NOT EDIT

coreInterval <- function(id=NULL, interval=NULL, disabled=NULL, n_intervals=NULL, max_intervals=NULL, fireEvent=NULL, dashEvents=NULL, ...) {

    wildcard_names = names(list(...))
    
    component <- list(
        props = list(id=id, interval=interval, disabled=disabled, n_intervals=n_intervals, max_intervals=max_intervals, fireEvent=fireEvent, dashEvents=dashEvents, ...),
        type = 'Interval',
        namespace = 'dash_core_components',
        propNames = c('id', 'interval', 'disabled', 'n_intervals', 'max_intervals', wildcard_names),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)
    
    structure(component, class = c('dash_component', 'list'))    
}