# AUTO GENERATED FILE - DO NOT EDIT

dccRadioItems <- function(id=NULL, options=NULL, value=NULL, style=NULL, className=NULL, inputStyle=NULL, inputClassName=NULL, labelStyle=NULL, labelClassName=NULL, loading_state=NULL) {
    
    props <- list(id=id, options=options, value=value, style=style, className=className, inputStyle=inputStyle, inputClassName=inputClassName, labelStyle=labelStyle, labelClassName=labelClassName, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'RadioItems',
        namespace = 'dash_core_components',
        propNames = c('id', 'options', 'value', 'style', 'className', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
