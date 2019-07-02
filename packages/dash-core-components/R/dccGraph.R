# AUTO GENERATED FILE - DO NOT EDIT

dccGraph <- function(id=NULL, clickData=NULL, clickAnnotationData=NULL, hoverData=NULL, clear_on_unhover=NULL, selectedData=NULL, relayoutData=NULL, extendData=NULL, restyleData=NULL, figure=NULL, style=NULL, className=NULL, animate=NULL, animation_options=NULL, config=NULL, loading_state=NULL) {
    
    props <- list(id=id, clickData=clickData, clickAnnotationData=clickAnnotationData, hoverData=hoverData, clear_on_unhover=clear_on_unhover, selectedData=selectedData, relayoutData=relayoutData, extendData=extendData, restyleData=restyleData, figure=figure, style=style, className=className, animate=animate, animation_options=animation_options, config=config, loading_state=loading_state)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Graph',
        namespace = 'dash_core_components',
        propNames = c('id', 'clickData', 'clickAnnotationData', 'hoverData', 'clear_on_unhover', 'selectedData', 'relayoutData', 'extendData', 'restyleData', 'figure', 'style', 'className', 'animate', 'animation_options', 'config', 'loading_state'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
