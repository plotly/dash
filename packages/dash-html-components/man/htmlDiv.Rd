% Auto-generated: do not edit by hand
\name{htmlDiv}

\alias{htmlDiv}

\title{Div component}

\description{

}

\usage{
htmlDiv(id=NULL, n_clicks=NULL, n_clicks_timestamp=NULL, key=NULL, role=NULL, accessKey=NULL, className=NULL, contentEditable=NULL, contextMenu=NULL, dir=NULL, draggable=NULL, hidden=NULL, lang=NULL, spellCheck=NULL, style=NULL, tabIndex=NULL, title=NULL, ...)
}

\arguments{
\item{id}{The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{n_clicks}{An integer that represents the number of times
that this element has been clicked on.}

\item{n_clicks_timestamp}{An integer that represents the time (in ms since 1970)
at which n_clicks changed. This can be used to tell
which button was changed most recently.}

\item{key}{A unique identifier for the component, used to improve
performance by React.js while rendering components
See https://reactjs.org/docs/lists-and-keys.html for more info}

\item{role}{The ARIA role attribute}

\item{accessKey}{Defines a keyboard shortcut to activate or add focus to the element.}

\item{className}{Often used with CSS to style elements with common properties.}

\item{contentEditable}{Indicates whether the element's content is editable.}

\item{contextMenu}{Defines the ID of a <menu> element which will serve as the element's context menu.}

\item{dir}{Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl (Right-To-Left)}

\item{draggable}{Defines whether the element can be dragged.}

\item{hidden}{Prevents rendering of given element, while keeping child elements, e.g. script elements, active.}

\item{lang}{Defines the language used in the element.}

\item{spellCheck}{Indicates whether spell checking is allowed for the element.}

\item{style}{Defines CSS styles which will override styles previously set.}

\item{tabIndex}{Overrides the browser's default tab order and follows the one specified instead.}

\item{title}{Text to be displayed in a tooltip when hovering over the element.}

\item{...}{wildcards: `data-*` or `aria-*`}
}
