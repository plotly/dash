# AUTO GENERATED FILE - DO NOT EDIT

dccSlider <- function(id=NULL, marks=NULL, value=NULL, className=NULL, disabled=NULL, dots=NULL, included=NULL, min=NULL, max=NULL, tooltip=NULL, step=NULL, vertical=NULL, updatemode=NULL, loading_state=NULL) {
    
    props <- list(id=id, marks=marks, value=value, className=className, disabled=disabled, dots=dots, included=included, min=min, max=max, tooltip=tooltip, step=step, vertical=vertical, updatemode=updatemode, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Slider',
        namespace = 'dash_core_components',
        propNames = c('id', 'marks', 'value', 'className', 'disabled', 'dots', 'included', 'min', 'max', 'tooltip', 'step', 'vertical', 'updatemode', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
