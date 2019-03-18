% Auto-generated: do not edit by hand
\name{dccLoading}

\alias{dccLoading}

\title{Loading component}

\description{
A Loading component that wraps any other component and displays a spinner until the wrapped component has rendered.
}

\usage{
dccLoading(children=NULL, id=NULL, type=NULL, fullscreen=NULL, debug=NULL, className=NULL, style=NULL, color=NULL, loading_state=NULL, ...)
}

\arguments{
\item{children}{Array that holds components to render}

\item{id}{}

\item{type}{Property that determines which spinner to show - one of 'graph', 'cube', 'circle', 'dot', or 'default'.}

\item{fullscreen}{Boolean that determines if the loading spinner will be displayed full-screen or not}

\item{debug}{Boolean that determines if the loading spinner will display the status.prop_name and component_name}

\item{className}{Additional CSS class for the root DOM node}

\item{style}{Additional CSS styling for the root DOM node}

\item{color}{Primary colour used for the loading spinners}

\item{loading_state}{Object that holds the loading state object coming from dash-renderer}
}
