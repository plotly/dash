# AUTO GENERATED FILE - DO NOT EDIT

dccDropdown <- function(id=NULL, options=NULL, value=NULL, className=NULL, clearable=NULL, disabled=NULL, multi=NULL, placeholder=NULL, searchable=NULL, style=NULL, loading_state=NULL) {
    
    component <- list(
        props = list(id=id, options=options, value=value, className=className, clearable=clearable, disabled=disabled, multi=multi, placeholder=placeholder, searchable=searchable, style=style, loading_state=loading_state),
        type = 'Dropdown',
        namespace = 'dash_core_components',
        propNames = c('id', 'options', 'value', 'className', 'clearable', 'disabled', 'multi', 'placeholder', 'searchable', 'style', 'loading_state'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)

    structure(component, class = c('dash_component', 'list'))
}