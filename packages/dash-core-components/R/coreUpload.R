# AUTO GENERATED FILE - DO NOT EDIT

coreUpload <- function(children=NULL, id=NULL, contents=NULL, filename=NULL, last_modified=NULL, accept=NULL, disabled=NULL, disable_click=NULL, max_size=NULL, min_size=NULL, multiple=NULL, className=NULL, className_active=NULL, className_reject=NULL, className_disabled=NULL, style=NULL, style_active=NULL, style_reject=NULL, style_disabled=NULL, ...) {

    wildcard_names = names(list(...))
    
    component <- list(
        props = list(children=children, id=id, contents=contents, filename=filename, last_modified=last_modified, accept=accept, disabled=disabled, disable_click=disable_click, max_size=max_size, min_size=min_size, multiple=multiple, className=className, className_active=className_active, className_reject=className_reject, className_disabled=className_disabled, style=style, style_active=style_active, style_reject=style_reject, style_disabled=style_disabled, ...),
        type = 'Upload',
        namespace = 'dash_core_components',
        propNames = c('children', 'id', 'contents', 'filename', 'last_modified', 'accept', 'disabled', 'disable_click', 'max_size', 'min_size', 'multiple', 'className', 'className_active', 'className_reject', 'className_disabled', 'style', 'style_active', 'style_reject', 'style_disabled', wildcard_names),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)
    
    structure(component, class = c('dash_component', 'list'))    
}