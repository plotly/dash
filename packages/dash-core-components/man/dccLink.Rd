% Auto-generated: do not edit by hand
\name{dccLink}

\alias{dccLink}

\title{Link component}

\description{
Link allows you to create a clickable link within a multi-page app.  For links with destinations outside the current app, `html.A` is a better component to use.
}

\usage{
dccLink(dccLink(children=NULL, id=NULL, href=NULL, refresh=NULL, className=NULL,
style=NULL, loading_state=NULL))
}

\arguments{
\item{children}{A list of or a singular dash component, string or number. The children of this component}

\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{href}{Character. The URL of a linked resource.}

\item{refresh}{Logical. Controls whether or not the page will refresh when the link is clicked}

\item{className}{Character. Often used with CSS to style elements with common properties.}

\item{style}{Named list. Defines CSS styles which will override styles previously set.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
