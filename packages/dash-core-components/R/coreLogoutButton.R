# AUTO GENERATED FILE - DO NOT EDIT

coreLogoutButton <- function(id=NULL, label=NULL, logout_url=NULL, style=NULL, method=NULL, className=NULL) {
    
    component <- list(
        props = list(id=id, label=label, logout_url=logout_url, style=style, method=method, className=className),
        type = 'LogoutButton',
        namespace = 'dash_core_components',
        propNames = c('id', 'label', 'logout_url', 'style', 'method', 'className'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)

    structure(component, class = c('dash_component', 'list'))
}