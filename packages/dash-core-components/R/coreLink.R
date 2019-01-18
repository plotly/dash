# AUTO GENERATED FILE - DO NOT EDIT

coreLink <- function(children=NULL, href=NULL, refresh=NULL, className=NULL, style=NULL, id=NULL, ...) {

    wildcard_names = names(list(...))
    
    component <- list(
        props = list(children=children, href=href, refresh=refresh, className=className, style=style, id=id, ...),
        type = 'Link',
        namespace = 'dash_core_components',
        propNames = c('children', 'href', 'refresh', 'className', 'style', 'id', wildcard_names),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)
    
    structure(component, class = c('dash_component', 'list'))    
}