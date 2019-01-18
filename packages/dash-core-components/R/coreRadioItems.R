# AUTO GENERATED FILE - DO NOT EDIT

coreRadioItems <- function(id=NULL, options=NULL, value=NULL, style=NULL, className=NULL, inputStyle=NULL, inputClassName=NULL, labelStyle=NULL, labelClassName=NULL, fireEvent=NULL, dashEvents=NULL, ...) {

    wildcard_names = names(list(...))
    
    component <- list(
        props = list(id=id, options=options, value=value, style=style, className=className, inputStyle=inputStyle, inputClassName=inputClassName, labelStyle=labelStyle, labelClassName=labelClassName, fireEvent=fireEvent, dashEvents=dashEvents, ...),
        type = 'RadioItems',
        namespace = 'dash_core_components',
        propNames = c('id', 'options', 'value', 'style', 'className', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName', wildcard_names),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)
    
    structure(component, class = c('dash_component', 'list'))    
}