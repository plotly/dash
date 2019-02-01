# AUTO GENERATED FILE - DO NOT EDIT

coreSlider <- function(id=NULL, marks=NULL, value=NULL, className=NULL, disabled=NULL, dots=NULL, included=NULL, min=NULL, max=NULL, step=NULL, vertical=NULL, updatemode=NULL) {
    
    component <- list(
        props = list(id=id, marks=marks, value=value, className=className, disabled=disabled, dots=dots, included=included, min=min, max=max, step=step, vertical=vertical, updatemode=updatemode),
        type = 'Slider',
        namespace = 'dash_core_components',
        propNames = c('id', 'marks', 'value', 'className', 'disabled', 'dots', 'included', 'min', 'max', 'step', 'vertical', 'updatemode'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)

    structure(component, class = c('dash_component', 'list'))
}