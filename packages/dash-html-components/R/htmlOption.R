# AUTO GENERATED FILE - DO NOT EDIT

htmlOption <- function(children=NULL, id=NULL, n_clicks=NULL, n_clicks_timestamp=NULL, key=NULL, role=NULL, disabled=NULL, selected=NULL, value=NULL, accessKey=NULL, className=NULL, contentEditable=NULL, contextMenu=NULL, dir=NULL, draggable=NULL, hidden=NULL, lang=NULL, spellCheck=NULL, style=NULL, tabIndex=NULL, title=NULL, ...) {
    
    wildcard_names = names(assert_valid_wildcards(...))

    component <- list(
        props = list(children=children, id=id, n_clicks=n_clicks, n_clicks_timestamp=n_clicks_timestamp, key=key, role=role, disabled=disabled, selected=selected, value=value, accessKey=accessKey, className=className, contentEditable=contentEditable, contextMenu=contextMenu, dir=dir, draggable=draggable, hidden=hidden, lang=lang, spellCheck=spellCheck, style=style, tabIndex=tabIndex, title=title, ...),
        type = 'Option',
        namespace = 'dash_html_components',
        propNames = c('children', 'id', 'n_clicks', 'n_clicks_timestamp', 'key', 'role', 'disabled', 'selected', 'value', 'accessKey', 'className', 'contentEditable', 'contextMenu', 'dir', 'draggable', 'hidden', 'lang', 'spellCheck', 'style', 'tabIndex', 'title', wildcard_names),
        package = 'dashHtmlComponents'
        )

    component$props <- filter_null(component$props)
    
    structure(component, class = c('dash_component', 'list'))    
}