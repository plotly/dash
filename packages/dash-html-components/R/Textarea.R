# AUTO GENERATED FILE - DO NOT EDIT

#' Textarea component
#' @description See <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/Textarea>
#' @export
#' @param ... The children of this component and/or 'wildcards' of the form: `data-*` or `aria-*`
#' @param children The children of this component
#' @param id The ID of this component, used to identify dash components in callbacks. The ID needs to be unique across all of the components in an app.
#' @param n_clicks An integer that represents the number of times that this element has been clicked on.
#' @param n_clicks_timestamp An integer that represents the time (in ms since 1970) at which n_clicks changed. This can be used to tell which button was changed most recently.
#' @param key A unique identifier for the component, used to improve performance by React.js while rendering components See https://reactjs.org/docs/lists-and-keys.html for more info
#' @param role The ARIA role attribute
#' @param autoComplete Indicates whether controls in this form can by default have their values automatically completed by the browser.
#' @param autoFocus The element should be automatically focused after the page loaded.
#' @param cols Defines the number of columns in a textarea.
#' @param disabled Indicates whether the user can interact with the element.
#' @param form Indicates the form that is the owner of the element.
#' @param maxLength Defines the maximum number of characters allowed in the element.
#' @param minLength Defines the minimum number of characters allowed in the element.
#' @param name Name of the element. For example used by the server to identify the fields in form submits.
#' @param placeholder Provides a hint to the user of what can be entered in the field.
#' @param readOnly Indicates whether the element can be edited.
#' @param required Indicates whether this element is required to fill out or not.
#' @param rows Defines the number of rows in a text area.
#' @param wrap Indicates whether the text should be wrapped.
#' @param accessKey Defines a keyboard shortcut to activate or add focus to the element.
#' @param className Often used with CSS to style elements with common properties.
#' @param contentEditable Indicates whether the element's content is editable.
#' @param contextMenu Defines the ID of a <menu> element which will serve as the element's context menu.
#' @param dir Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left)
#' @param draggable Defines whether the element can be dragged.
#' @param hidden Prevents rendering of given element, while keeping child elements, e.g. script elements, active.
#' @param lang Defines the language used in the element.
#' @param spellCheck Indicates whether spell checking is allowed for the element.
#' @param style Defines CSS styles which will override styles previously set.
#' @param tabIndex Overrides the browser's default tab order and follows the one specified instead.
#' @param title Text to be displayed in a tooltip when hovering over the element.


    htmlTextarea <- function(..., children=NULL, id=NULL, n_clicks=0, n_clicks_timestamp=-1, key=NULL, role=NULL, autoComplete=NULL, autoFocus=NULL, cols=NULL, disabled=NULL, form=NULL, maxLength=NULL, minLength=NULL, name=NULL, placeholder=NULL, readOnly=NULL, required=NULL, rows=NULL, wrap=NULL, accessKey=NULL, className=NULL, contentEditable=NULL, contextMenu=NULL, dir=NULL, draggable=NULL, hidden=NULL, lang=NULL, spellCheck=NULL, style=NULL, tabIndex=NULL, title=NULL, fireEvent=NULL, dashEvents=NULL) {

    component <- list(
      props = list(
         id=id, children=c(children, assert_valid_children(..., wildcards = c('data-*', 'aria-*'))), n_clicks=n_clicks, n_clicks_timestamp=n_clicks_timestamp, key=key, role=role, autoComplete=autoComplete, autoFocus=autoFocus, cols=cols, disabled=disabled, form=form, maxLength=maxLength, minLength=minLength, name=name, placeholder=placeholder, readOnly=readOnly, required=required, rows=rows, wrap=wrap, accessKey=accessKey, className=className, contentEditable=contentEditable, contextMenu=contextMenu, dir=dir, draggable=draggable, hidden=hidden, lang=lang, spellCheck=spellCheck, style=style, tabIndex=tabIndex, title=title, fireEvent=fireEvent, dashEvents=dashEvents
      ),
      type = 'Textarea',
      namespace = 'dash_html_components',
      propNames = c('children', 'id', 'n_clicks', 'n_clicks_timestamp', 'key', 'role', 'data-*', 'aria-*', 'autoComplete', 'autoFocus', 'cols', 'disabled', 'form', 'maxLength', 'minLength', 'name', 'placeholder', 'readOnly', 'required', 'rows', 'wrap', 'accessKey', 'className', 'contentEditable', 'contextMenu', 'dir', 'draggable', 'hidden', 'lang', 'spellCheck', 'style', 'tabIndex', 'title'),
      package = 'dashHtmlComponents'
    )

    component$props <- filter_null(component$props)
    component <- append_wildcard_props(component, wildcards = c('data-*', 'aria-*'), ...)

    structure(component, class = c('dash_component', 'list'))
    }
