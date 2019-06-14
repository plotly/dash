% Auto-generated: do not edit by hand
\name{htmlTextarea}

\alias{htmlTextarea}

\title{Textarea component}

\description{

}

\usage{
htmlTextarea(htmlTextarea(children=NULL, id=NULL, n_clicks=NULL, n_clicks_timestamp=NULL,
key=NULL, role=NULL, autoComplete=NULL, autoFocus=NULL, cols=NULL,
disabled=NULL, form=NULL, inputMode=NULL, maxLength=NULL, minLength=NULL,
name=NULL, placeholder=NULL, readOnly=NULL, required=NULL, rows=NULL, wrap=NULL,
accessKey=NULL, className=NULL, contentEditable=NULL, contextMenu=NULL,
dir=NULL, draggable=NULL, hidden=NULL, lang=NULL, spellCheck=NULL, style=NULL,
tabIndex=NULL, title=NULL, loading_state=NULL, ...))
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

\item{autoComplete}{Character. Indicates whether controls in this form can by default have their values automatically completed by the browser.}

\item{autoFocus}{A value equal to: 'autofocus', 'autofocus', 'autofocus' | logical. The element should be automatically focused after the page loaded.}

\item{cols}{Character | numeric. Defines the number of columns in a textarea.}

\item{disabled}{A value equal to: 'disabled', 'disabled' | logical. Indicates whether the user can interact with the element.}

\item{form}{Character. Indicates the form that is the owner of the element.}

\item{inputMode}{Character. Provides a hint as to the type of data that might be entered by the user while editing the element or its contents. The attribute can be used with form controls (such as the value of textarea elements), or in elements in an editing host (e.g., using contenteditable attribute).}

\item{maxLength}{Character | numeric. Defines the maximum number of characters allowed in the element.}

\item{minLength}{Character | numeric. Defines the minimum number of characters allowed in the element.}

\item{name}{Character. Name of the element. For example used by the server to identify the fields in form submits.}

\item{placeholder}{Character. Provides a hint to the user of what can be entered in the field.}

\item{readOnly}{Character. Indicates whether the element can be edited.}

\item{required}{A value equal to: 'required', 'required' | logical. Indicates whether this element is required to fill out or not.}

\item{rows}{Character | numeric. Defines the number of rows in a text area.}

\item{wrap}{Character. Indicates whether the text should be wrapped.}

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

\item{...}{wildcards: `data-*` or `aria-*`}
}
