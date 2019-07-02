# AUTO GENERATED FILE - DO NOT EDIT

dccInterval <- function(id=NULL, interval=NULL, disabled=NULL, n_intervals=NULL, max_intervals=NULL) {
    
    props <- list(id=id, interval=interval, disabled=disabled, n_intervals=n_intervals, max_intervals=max_intervals)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Interval',
        namespace = 'dash_core_components',
        propNames = c('id', 'interval', 'disabled', 'n_intervals', 'max_intervals'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
