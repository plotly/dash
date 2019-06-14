% Auto-generated: do not edit by hand
\name{dccTextarea}

\alias{dccTextarea}

\title{Textarea component}

\description{
A basic HTML textarea for entering multiline text.
}

\usage{
dccTextarea(dccTextarea(id=NULL, value=NULL, autoFocus=NULL, cols=NULL, disabled=NULL,
form=NULL, maxLength=NULL, minLength=NULL, name=NULL, placeholder=NULL,
readOnly=NULL, required=NULL, rows=NULL, wrap=NULL, accessKey=NULL,
className=NULL, contentEditable=NULL, contextMenu=NULL, dir=NULL,
draggable=NULL, hidden=NULL, lang=NULL, spellCheck=NULL, style=NULL,
tabIndex=NULL, title=NULL, n_blur=NULL, n_blur_timestamp=NULL, n_clicks=NULL,
n_clicks_timestamp=NULL, loading_state=NULL))
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{value}{Character. The value of the textarea}

\item{autoFocus}{Character. The element should be automatically focused after the page loaded.}

\item{cols}{Character | numeric. Defines the number of columns in a textarea.}

\item{disabled}{Character | logical. Indicates whether the user can interact with the element.}

\item{form}{Character. Indicates the form that is the owner of the element.}

\item{maxLength}{Character | numeric. Defines the maximum number of characters allowed in the element.}

\item{minLength}{Character | numeric. Defines the minimum number of characters allowed in the element.}

\item{name}{Character. Name of the element. For example used by the server to identify the fields in form submits.}

\item{placeholder}{Character. Provides a hint to the user of what can be entered in the field.}

\item{readOnly}{Logical | a value equal to: 'readonly', 'readonly', 'readonly'. Indicates whether the element can be edited.
readOnly is an HTML boolean attribute - it is enabled by a boolean or
'readOnly'. Alternative capitalizations `readonly` & `READONLY`
are also acccepted.}

\item{required}{A value equal to: 'required', 'required' | logical. Indicates whether this element is required to fill out or not.
required is an HTML boolean attribute - it is enabled by a boolean or
'required'. Alternative capitalizations `REQUIRED`
are also acccepted.}

\item{rows}{Character | numeric. Defines the number of rows in a text area.}

\item{wrap}{Character. Indicates whether the text should be wrapped.}

\item{accessKey}{Character. Defines a keyboard shortcut to activate or add focus to the element.}

\item{className}{Character. Often used with CSS to style elements with common properties.}

\item{contentEditable}{Character | logical. Indicates whether the element's content is editable.}

\item{contextMenu}{Character. Defines the ID of a <menu> element which will serve as the element's context menu.}

\item{dir}{Character. Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left)}

\item{draggable}{A value equal to: 'true', 'false' | logical. Defines whether the element can be dragged.}

\item{hidden}{Character. Prevents rendering of given element, while keeping child elements, e.g. script elements, active.}

\item{lang}{Character. Defines the language used in the element.}

\item{spellCheck}{A value equal to: 'true', 'false' | logical. Indicates whether spell checking is allowed for the element.}

\item{style}{Named list. Defines CSS styles which will override styles previously set.}

\item{tabIndex}{Character | numeric. Overrides the browser's default tab order and follows the one specified instead.}

\item{title}{Character. Text to be displayed in a tooltip when hovering over the element.}

\item{n_blur}{Numeric. Number of times the textarea lost focus.}

\item{n_blur_timestamp}{Numeric. Last time the textarea lost focus.}

\item{n_clicks}{Numeric. Number of times the textarea has been clicked.}

\item{n_clicks_timestamp}{Numeric. Last time the textarea was clicked.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
