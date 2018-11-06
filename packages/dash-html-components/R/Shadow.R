# AUTO GENERATED FILE - DO NOT EDIT

#' Shadow component
#' @description See <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/Shadow>
#' @export
#' @param ... The children of this component and/or 'wildcards' of the form: `data-*` or `aria-*`
#' @param children The children of this component
#' @param id The ID of this component, used to identify dash components in callbacks. The ID needs to be unique across all of the components in an app.
#' @param n_clicks An integer that represents the number of times that this element has been clicked on.
#' @param n_clicks_timestamp An integer that represents the time (in ms since 1970) at which n_clicks changed. This can be used to tell which button was changed most recently.
#' @param key A unique identifier for the component, used to improve performance by React.js while rendering components See https://reactjs.org/docs/lists-and-keys.html for more info
#' @param role The ARIA role attribute
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


    htmlShadow <- function(..., children=NULL, id=NULL, n_clicks=0, n_clicks_timestamp=-1, key=NULL, role=NULL, accessKey=NULL, className=NULL, contentEditable=NULL, contextMenu=NULL, dir=NULL, draggable=NULL, hidden=NULL, lang=NULL, spellCheck=NULL, style=NULL, tabIndex=NULL, title=NULL, fireEvent=NULL, dashEvents=NULL) {

    component <- list(
      props = list(
         id=id, children=c(children, assert_valid_children(..., wildcards = c('data-*', 'aria-*'))), n_clicks=n_clicks, n_clicks_timestamp=n_clicks_timestamp, key=key, role=role, accessKey=accessKey, className=className, contentEditable=contentEditable, contextMenu=contextMenu, dir=dir, draggable=draggable, hidden=hidden, lang=lang, spellCheck=spellCheck, style=style, tabIndex=tabIndex, title=title, fireEvent=fireEvent, dashEvents=dashEvents
      ),
      type = 'Shadow',
      namespace = 'dash_html_components',
      propNames = c('children', 'id', 'n_clicks', 'n_clicks_timestamp', 'key', 'role', 'data-*', 'aria-*', 'accessKey', 'className', 'contentEditable', 'contextMenu', 'dir', 'draggable', 'hidden', 'lang', 'spellCheck', 'style', 'tabIndex', 'title'),
      package = 'dashHtmlComponents'
    )

    component$props <- filter_null(component$props)
    component <- append_wildcard_props(component, wildcards = c('data-*', 'aria-*'), ...)

    structure(component, class = c('dash_component', 'list'))
    }
