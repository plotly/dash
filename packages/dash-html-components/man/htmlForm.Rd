% Auto-generated: do not edit by hand
\name{htmlForm}

\alias{htmlForm}

\title{Form component}

\description{
Form is a wrapper for the <form> HTML5 element. For detailed attribute info see: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form
}

\usage{
htmlForm(children=NULL, id=NULL, n_clicks=NULL, n_clicks_timestamp=NULL, key=NULL,
role=NULL, accept=NULL, acceptCharset=NULL, action=NULL, autoComplete=NULL,
encType=NULL, method=NULL, name=NULL, noValidate=NULL, target=NULL,
accessKey=NULL, className=NULL, contentEditable=NULL, contextMenu=NULL,
dir=NULL, draggable=NULL, hidden=NULL, lang=NULL, spellCheck=NULL, style=NULL,
tabIndex=NULL, title=NULL, loading_state=NULL, ...)
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

\item{accept}{Character. List of types the server accepts, typically a file type.}

\item{acceptCharset}{Character. List of supported charsets.}

\item{action}{Character. The URI of a program that processes the information submitted via the form.}

\item{autoComplete}{Character. Indicates whether controls in this form can by default have their values automatically completed by the browser.}

\item{encType}{Character. Defines the content type of the form date when the method is POST.}

\item{method}{Character. Defines which HTTP method to use when submitting the form. Can be GET (default) or POST.}

\item{name}{Character. Name of the element. For example used by the server to identify the fields in form submits.}

\item{noValidate}{A value equal to: 'novalidate', 'novalidate', 'novalidate' | logical. This attribute indicates that the form shouldn't be validated when submitted.}

\item{target}{Character. }

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
