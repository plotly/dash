# AUTO GENERATED FILE - DO NOT EDIT

dccConfirmDialogProvider <- function(children=NULL, id=NULL, message=NULL, submit_n_clicks=NULL, submit_n_clicks_timestamp=NULL, cancel_n_clicks=NULL, cancel_n_clicks_timestamp=NULL, displayed=NULL, loading_state=NULL) {
    
    component <- list(
        props = list(children=children, id=id, message=message, submit_n_clicks=submit_n_clicks, submit_n_clicks_timestamp=submit_n_clicks_timestamp, cancel_n_clicks=cancel_n_clicks, cancel_n_clicks_timestamp=cancel_n_clicks_timestamp, displayed=displayed, loading_state=loading_state),
        type = 'ConfirmDialogProvider',
        namespace = 'dash_core_components',
        propNames = c('children', 'id', 'message', 'submit_n_clicks', 'submit_n_clicks_timestamp', 'cancel_n_clicks', 'cancel_n_clicks_timestamp', 'displayed', 'loading_state'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)

    structure(component, class = c('dash_component', 'list'))
}
