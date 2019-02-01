# AUTO GENERATED FILE - DO NOT EDIT

coreStore <- function(id=NULL, storage_type=NULL, data=NULL, clear_data=NULL, modified_timestamp=NULL) {
    
    component <- list(
        props = list(id=id, storage_type=storage_type, data=data, clear_data=clear_data, modified_timestamp=modified_timestamp),
        type = 'Store',
        namespace = 'dash_core_components',
        propNames = c('id', 'storage_type', 'data', 'clear_data', 'modified_timestamp'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)

    structure(component, class = c('dash_component', 'list'))
}