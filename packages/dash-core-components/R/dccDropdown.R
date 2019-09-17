# AUTO GENERATED FILE - DO NOT EDIT

dccDropdown <- function(id=NULL, options=NULL, value=NULL, optionHeight=NULL, className=NULL, clearable=NULL, disabled=NULL, multi=NULL, placeholder=NULL, searchable=NULL, style=NULL, loading_state=NULL, persistence=NULL, persisted_props=NULL, persistence_type=NULL) {
    
    props <- list(id=id, options=options, value=value, optionHeight=optionHeight, className=className, clearable=clearable, disabled=disabled, multi=multi, placeholder=placeholder, searchable=searchable, style=style, loading_state=loading_state, persistence=persistence, persisted_props=persisted_props, persistence_type=persistence_type)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Dropdown',
        namespace = 'dash_core_components',
        propNames = c('id', 'options', 'value', 'optionHeight', 'className', 'clearable', 'disabled', 'multi', 'placeholder', 'searchable', 'style', 'loading_state', 'persistence', 'persisted_props', 'persistence_type'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
