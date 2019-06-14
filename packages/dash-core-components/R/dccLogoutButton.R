# AUTO GENERATED FILE - DO NOT EDIT

dccLogoutButton <- function(id=NULL, label=NULL, logout_url=NULL, style=NULL, method=NULL, className=NULL, loading_state=NULL) {
    
    component <- list(
        props = list(id=id, label=label, logout_url=logout_url, style=style, method=method, className=className, loading_state=loading_state),
        type = 'LogoutButton',
        namespace = 'dash_core_components',
        propNames = c('id', 'label', 'logout_url', 'style', 'method', 'className', 'loading_state'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)

    structure(component, class = c('dash_component', 'list'))
}
