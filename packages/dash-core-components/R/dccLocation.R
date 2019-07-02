# AUTO GENERATED FILE - DO NOT EDIT

dccLocation <- function(id=NULL, pathname=NULL, search=NULL, hash=NULL, href=NULL, refresh=NULL) {
    
    props <- list(id=id, pathname=pathname, search=search, hash=hash, href=href, refresh=refresh)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Location',
        namespace = 'dash_core_components',
        propNames = c('id', 'pathname', 'search', 'hash', 'href', 'refresh'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
