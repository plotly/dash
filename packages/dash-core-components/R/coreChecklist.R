# AUTO GENERATED FILE - DO NOT EDIT

coreChecklist <- function(id=NULL, options=NULL, values=NULL, className=NULL, style=NULL, inputStyle=NULL, inputClassName=NULL, labelStyle=NULL, labelClassName=NULL, fireEvent=NULL, dashEvents=NULL, ...) {

    wildcard_names = names(list(...))
    
    component <- list(
        props = list(id=id, options=options, values=values, className=className, style=style, inputStyle=inputStyle, inputClassName=inputClassName, labelStyle=labelStyle, labelClassName=labelClassName, fireEvent=fireEvent, dashEvents=dashEvents, ...),
        type = 'Checklist',
        namespace = 'dash_core_components',
        propNames = c('id', 'options', 'values', 'className', 'style', 'inputStyle', 'inputClassName', 'labelStyle', 'labelClassName', wildcard_names),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)
    
    structure(component, class = c('dash_component', 'list'))    
}