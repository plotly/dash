# AUTO GENERATED FILE - DO NOT EDIT

dccTabs <- function(children=NULL, id=NULL, value=NULL, className=NULL, content_className=NULL, parent_className=NULL, style=NULL, parent_style=NULL, content_style=NULL, vertical=NULL, mobile_breakpoint=NULL, colors=NULL, loading_state=NULL) {
    
    props <- list(children=children, id=id, value=value, className=className, content_className=content_className, parent_className=parent_className, style=style, parent_style=parent_style, content_style=content_style, vertical=vertical, mobile_breakpoint=mobile_breakpoint, colors=colors, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Tabs',
        namespace = 'dash_core_components',
        propNames = c('children', 'id', 'value', 'className', 'content_className', 'parent_className', 'style', 'parent_style', 'content_style', 'vertical', 'mobile_breakpoint', 'colors', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
