# AUTO GENERATED FILE - DO NOT EDIT

dccInput <- function(id=NULL, value=NULL, style=NULL, className=NULL, debounce=NULL, type=NULL, autoComplete=NULL, autoFocus=NULL, disabled=NULL, inputMode=NULL, list=NULL, max=NULL, maxLength=NULL, min=NULL, minLength=NULL, multiple=NULL, name=NULL, pattern=NULL, placeholder=NULL, readOnly=NULL, required=NULL, selectionDirection=NULL, selectionEnd=NULL, selectionStart=NULL, size=NULL, spellCheck=NULL, step=NULL, n_submit=NULL, n_submit_timestamp=NULL, n_blur=NULL, n_blur_timestamp=NULL, loading_state=NULL, persistence=NULL, persisted_props=NULL, persistence_type=NULL) {
    
    props <- list(id=id, value=value, style=style, className=className, debounce=debounce, type=type, autoComplete=autoComplete, autoFocus=autoFocus, disabled=disabled, inputMode=inputMode, list=list, max=max, maxLength=maxLength, min=min, minLength=minLength, multiple=multiple, name=name, pattern=pattern, placeholder=placeholder, readOnly=readOnly, required=required, selectionDirection=selectionDirection, selectionEnd=selectionEnd, selectionStart=selectionStart, size=size, spellCheck=spellCheck, step=step, n_submit=n_submit, n_submit_timestamp=n_submit_timestamp, n_blur=n_blur, n_blur_timestamp=n_blur_timestamp, loading_state=loading_state, persistence=persistence, persisted_props=persisted_props, persistence_type=persistence_type)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'Input',
        namespace = 'dash_core_components',
        propNames = c('id', 'value', 'style', 'className', 'debounce', 'type', 'autoComplete', 'autoFocus', 'disabled', 'inputMode', 'list', 'max', 'maxLength', 'min', 'minLength', 'multiple', 'name', 'pattern', 'placeholder', 'readOnly', 'required', 'selectionDirection', 'selectionEnd', 'selectionStart', 'size', 'spellCheck', 'step', 'n_submit', 'n_submit_timestamp', 'n_blur', 'n_blur_timestamp', 'loading_state', 'persistence', 'persisted_props', 'persistence_type'),
        package = 'dashCoreComponents'
        )

    structure(component, class = c('dash_component', 'list'))
}
