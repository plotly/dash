# AUTO GENERATED FILE - DO NOT EDIT

dccStore <- function(id=NULL, storage_type=NULL, data=NULL, clear_data=NULL, modified_timestamp=NULL) {
    
    props <- list(id=id, storage_type=storage_type, data=data, clear_data=clear_data, modified_timestamp=modified_timestamp)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Store',
        namespace = 'dash_core_components',
        propNames = c('id', 'storage_type', 'data', 'clear_data', 'modified_timestamp'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
