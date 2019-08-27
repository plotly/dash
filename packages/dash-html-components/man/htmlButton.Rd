% Auto-generated: do not edit by hand
\name{htmlButton}

\alias{htmlButton}

\title{Button component}

\description{
Button is a wrapper for the <button> HTML5 element. For detailed attribute info see: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button
}

\usage{
htmlButton(children=NULL, id=NULL, n_clicks=NULL, n_clicks_timestamp=NULL, key=NULL,
role=NULL, autoFocus=NULL, disabled=NULL, form=NULL, formAction=NULL,
formEncType=NULL, formMethod=NULL, formNoValidate=NULL, formTarget=NULL,
name=NULL, type=NULL, value=NULL, accessKey=NULL, className=NULL,
contentEditable=NULL, contextMenu=NULL, dir=NULL, draggable=NULL, hidden=NULL,
lang=NULL, spellCheck=NULL, style=NULL, tabIndex=NULL, title=NULL,
loading_state=NULL, ...)
}

\arguments{
\item{children}{A list of or a singular dash component, string or number. The children of this component}

\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{n_clicks}{Numeric. An integer that represents the number of times
that this element has been clicked on.}

\item{n_clicks_timestamp}{Numeric. An integer that represents the time (in ms since 1970)
at which n_clicks changed. This can be used to tell
which button was changed most recently.}

\item{key}{Character. A unique identifier for the component, used to improve
performance by React.js while rendering components
See https://reactjs.org/docs/lists-and-keys.html for more info}

\item{role}{Character. The ARIA role attribute}

\item{autoFocus}{A value equal to: 'autofocus', 'autofocus', 'autofocus' | logical. The element should be automatically focused after the page loaded.}

\item{disabled}{A value equal to: 'disabled', 'disabled' | logical. Indicates whether the user can interact with the element.}

\item{form}{Character. Indicates the form that is the owner of the element.}

\item{formAction}{Character. Indicates the action of the element, overriding the action defined in the <form>.}

\item{formEncType}{Character. If the button/input is a submit button (type="submit"), this attribute sets the encoding type to use during form submission. If this attribute is specified, it overrides the enctype attribute of the button's form owner.}

\item{formMethod}{Character. If the button/input is a submit button (type="submit"), this attribute sets the submission method to use during form submission (GET, POST, etc.). If this attribute is specified, it overrides the method attribute of the button's form owner.}

\item{formNoValidate}{A value equal to: 'formnovalidate', 'formnovalidate', 'formnovalidate' | logical. If the button/input is a submit button (type="submit"), this boolean attribute specifies that the form is not to be validated when it is submitted. If this attribute is specified, it overrides the novalidate attribute of the button's form owner.}

\item{formTarget}{Character. If the button/input is a submit button (type="submit"), this attribute specifies the browsing context (for example, tab, window, or inline frame) in which to display the response that is received after submitting the form. If this attribute is specified, it overrides the target attribute of the button's form owner.}

\item{name}{Character. Name of the element. For example used by the server to identify the fields in form submits.}

\item{type}{Character. Defines the type of the element.}

\item{value}{Character. Defines a default value which will be displayed in the element on page load.}

\item{accessKey}{Character. Defines a keyboard shortcut to activate or add focus to the element.}

\item{className}{Character. Often used with CSS to style elements with common properties.}

\item{contentEditable}{Character. Indicates whether the element's content is editable.}

\item{contextMenu}{Character. Defines the ID of a <menu> element which will serve as the element's context menu.}

\item{dir}{Character. Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left)}

\item{draggable}{Character. Defines whether the element can be dragged.}

\item{hidden}{A value equal to: 'hidden', 'hidden' | logical. Prevents rendering of given element, while keeping child elements, e.g. script elements, active.}

\item{lang}{Character. Defines the language used in the element.}

\item{spellCheck}{Character. Indicates whether spell checking is allowed for the element.}

\item{style}{Named list. Defines CSS styles which will override styles previously set.}

\item{tabIndex}{Character. Overrides the browser's default tab order and follows the one specified instead.}

\item{title}{Character. Text to be displayed in a tooltip when hovering over the element.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}


\item{...}{wildcards allowed have the form: `'data-*', 'aria-*'`}

}
