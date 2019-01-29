# AUTO GENERATED FILE - DO NOT EDIT

coreDropdown <- function(id=NULL, options=NULL, value=NULL, className=NULL, clearable=NULL, disabled=NULL, multi=NULL, placeholder=NULL, searchable=NULL, style=NULL) {
    
    component <- list(
        props = list(id=id, options=options, value=value, className=className, clearable=clearable, disabled=disabled, multi=multi, placeholder=placeholder, searchable=searchable, style=style),
        type = 'Dropdown',
        namespace = 'dash_core_components',
        propNames = c('id', 'options', 'value', 'className', 'clearable', 'disabled', 'multi', 'placeholder', 'searchable', 'style'),
        package = 'dashCoreComponents'
        )

    component$props <- filter_null(component$props)
    
    structure(component, class = c('dash_component', 'list'))    
}