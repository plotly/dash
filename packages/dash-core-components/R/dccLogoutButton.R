# AUTO GENERATED FILE - DO NOT EDIT

dccLogoutButton <- function(id=NULL, label=NULL, logout_url=NULL, style=NULL, method=NULL, className=NULL, loading_state=NULL) {
    
    props <- list(id=id, label=label, logout_url=logout_url, style=style, method=method, className=className, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'LogoutButton',
        namespace = 'dash_core_components',
        propNames = c('id', 'label', 'logout_url', 'style', 'method', 'className', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
