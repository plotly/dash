% Auto-generated: do not edit by hand
\name{dccLoading}

\alias{dccLoading}

\title{Loading component}

\description{
A Loading component that wraps any other component and displays a spinner until the wrapped component has rendered.
}

\usage{
dccLoading(children=NULL, id=NULL, type=NULL, fullscreen=NULL, debug=NULL, className=NULL,
style=NULL, color=NULL, loading_state=NULL)
}

\arguments{
\item{children}{List of a list of or a singular dash component, string or numbers | a list of or a singular dash component, string or number. Array that holds components to render}

\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{type}{A value equal to: 'graph', 'cube', 'circle', 'dot', 'default'. Property that determines which spinner to show - one of 'graph', 'cube', 'circle', 'dot', or 'default'.}

\item{fullscreen}{Logical. Boolean that determines if the loading spinner will be displayed full-screen or not}

\item{debug}{Logical. Boolean that determines if the loading spinner will display the status.prop_name and component_name}

\item{className}{Character. Additional CSS class for the root DOM node}

\item{style}{Named list. Additional CSS styling for the root DOM node}

\item{color}{Character. Primary colour used for the loading spinners}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
