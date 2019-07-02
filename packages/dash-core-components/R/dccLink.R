# AUTO GENERATED FILE - DO NOT EDIT

dccLink <- function(children=NULL, id=NULL, href=NULL, refresh=NULL, className=NULL, style=NULL, loading_state=NULL) {
    
    props <- list(children=children, id=id, href=href, refresh=refresh, className=className, style=style, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Link',
        namespace = 'dash_core_components',
        propNames = c('children', 'id', 'href', 'refresh', 'className', 'style', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
