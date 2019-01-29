# AUTO GENERATED FILE - DO NOT EDIT

coreConfirmDialog <- function(id=NULL, message=NULL, submit_n_clicks=NULL, submit_n_clicks_timestamp=NULL, cancel_n_clicks=NULL, cancel_n_clicks_timestamp=NULL, displayed=NULL, key=NULL) {
    
    component <- list(
        props = list(id=id, message=message, submit_n_clicks=submit_n_clicks, submit_n_clicks_timestamp=submit_n_clicks_timestamp, cancel_n_clicks=cancel_n_clicks, cancel_n_clicks_timestamp=cancel_n_clicks_timestamp, displayed=displayed, key=key),
        type = 'ConfirmDialog',
        namespace = 'dash_core_components',
        propNames = c('id', 'message', 'submit_n_clicks', 'submit_n_clicks_timestamp', 'cancel_n_clicks', 'cancel_n_clicks_timestamp', 'displayed', 'key'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)
    
    structure(component, class = c('dash_component', 'list'))    
}