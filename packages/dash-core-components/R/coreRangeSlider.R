# AUTO GENERATED FILE - DO NOT EDIT

coreRangeSlider <- function(id=NULL, marks=NULL, value=NULL, allowCross=NULL, className=NULL, count=NULL, disabled=NULL, dots=NULL, included=NULL, min=NULL, max=NULL, pushable=NULL, step=NULL, vertical=NULL, updatemode=NULL, fireEvent=NULL, dashEvents=NULL, ...) {

    wildcard_names = names(list(...))
    
    component <- list(
        props = list(id=id, marks=marks, value=value, allowCross=allowCross, className=className, count=count, disabled=disabled, dots=dots, included=included, min=min, max=max, pushable=pushable, step=step, vertical=vertical, updatemode=updatemode, fireEvent=fireEvent, dashEvents=dashEvents, ...),
        type = 'RangeSlider',
        namespace = 'dash_core_components',
        propNames = c('id', 'marks', 'value', 'allowCross', 'className', 'count', 'disabled', 'dots', 'included', 'min', 'max', 'pushable', 'step', 'vertical', 'updatemode', wildcard_names),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)
    
    structure(component, class = c('dash_component', 'list'))    
}