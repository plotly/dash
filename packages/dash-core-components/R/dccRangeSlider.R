# AUTO GENERATED FILE - DO NOT EDIT

dccRangeSlider <- function(id=NULL, marks=NULL, value=NULL, allowCross=NULL, className=NULL, count=NULL, disabled=NULL, dots=NULL, included=NULL, min=NULL, max=NULL, pushable=NULL, tooltip=NULL, step=NULL, vertical=NULL, updatemode=NULL, loading_state=NULL) {
    
    props <- list(id=id, marks=marks, value=value, allowCross=allowCross, className=className, count=count, disabled=disabled, dots=dots, included=included, min=min, max=max, pushable=pushable, tooltip=tooltip, step=step, vertical=vertical, updatemode=updatemode, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'RangeSlider',
        namespace = 'dash_core_components',
        propNames = c('id', 'marks', 'value', 'allowCross', 'className', 'count', 'disabled', 'dots', 'included', 'min', 'max', 'pushable', 'tooltip', 'step', 'vertical', 'updatemode', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
