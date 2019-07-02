# AUTO GENERATED FILE - DO NOT EDIT

dccChecklist <- function(id=NULL, options=NULL, value=NULL, className=NULL, style=NULL, inputStyle=NULL, inputClassName=NULL, labelStyle=NULL, labelClassName=NULL, loading_state=NULL) {
    
    props <- list(id=id, options=options, value=value, className=className, style=style, inputStyle=inputStyle, inputClassName=inputClassName, labelStyle=labelStyle, labelClassName=labelClassName, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Checklist',
        namespace = 'dash_core_components',
        propNames = c('id', 'options', 'value', 'className', 'style', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
