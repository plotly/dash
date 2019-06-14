% Auto-generated: do not edit by hand
\name{htmlArea}

\alias{htmlArea}

\title{Area component}

\description{

}

\usage{
htmlArea(htmlArea(children=NULL, id=NULL, n_clicks=NULL, n_clicks_timestamp=NULL,
key=NULL, role=NULL, alt=NULL, coords=NULL, download=NULL, href=NULL,
hrefLang=NULL, media=NULL, rel=NULL, shape=NULL, target=NULL, accessKey=NULL,
className=NULL, contentEditable=NULL, contextMenu=NULL, dir=NULL,
draggable=NULL, hidden=NULL, lang=NULL, spellCheck=NULL, style=NULL,
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

\item{alt}{Character. Alternative text in case an image can't be displayed.}

\item{coords}{Character. A set of values specifying the coordinates of the hot-spot region.}

\item{download}{Character. Indicates that the hyperlink is to be used for downloading a resource.}

\item{href}{Character. The URL of a linked resource.}

\item{hrefLang}{Character. Specifies the language of the linked resource.}

\item{media}{Character. Specifies a hint of the media for which the linked resource was designed.}

\item{rel}{Character. Specifies the relationship of the target object to the link object.}

\item{shape}{Character. }

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

\item{...}{wildcards: `data-*` or `aria-*`}
}
