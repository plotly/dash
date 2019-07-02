# AUTO GENERATED FILE - DO NOT EDIT

dccMarkdown <- function(children=NULL, id=NULL, className=NULL, dangerously_allow_html=NULL, dedent=NULL, highlight_config=NULL, loading_state=NULL, style=NULL) {
    
    props <- list(children=children, id=id, className=className, dangerously_allow_html=dangerously_allow_html, dedent=dedent, highlight_config=highlight_config, loading_state=loading_state, style=style)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Markdown',
        namespace = 'dash_core_components',
        propNames = c('children', 'id', 'className', 'dangerously_allow_html', 'dedent', 'highlight_config', 'loading_state', 'style'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
