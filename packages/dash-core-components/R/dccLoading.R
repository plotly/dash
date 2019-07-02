# AUTO GENERATED FILE - DO NOT EDIT

dccLoading <- function(children=NULL, id=NULL, type=NULL, fullscreen=NULL, debug=NULL, className=NULL, style=NULL, color=NULL, loading_state=NULL) {
    
    props <- list(children=children, id=id, type=type, fullscreen=fullscreen, debug=debug, className=className, style=style, color=color, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Loading',
        namespace = 'dash_core_components',
        propNames = c('children', 'id', 'type', 'fullscreen', 'debug', 'className', 'style', 'color', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
