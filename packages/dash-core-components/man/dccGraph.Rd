% Auto-generated: do not edit by hand
\name{dccGraph}

\alias{dccGraph}

\title{Graph component}

\description{

}

\usage{
dccGraph(id=NULL, clickData=NULL, clickAnnotationData=NULL, hoverData=NULL, clear_on_unhover=NULL, selectedData=NULL, relayoutData=NULL, restyleData=NULL, figure=NULL, style=NULL, className=NULL, animate=NULL, animation_options=NULL, config=NULL, loading_state=NULL, ...)
}

\arguments{
\item{id}{The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{clickData}{Data from latest click event}

\item{clickAnnotationData}{Data from latest click annotation event}

\item{hoverData}{Data from latest hover event}

\item{clear_on_unhover}{If True, `clear_on_unhover` will clear the `hoverData` property
when the user "unhovers" from a point.
If False, then the `hoverData` property will be equal to the
data from the last point that was hovered over.}

\item{selectedData}{Data from latest select event}

\item{relayoutData}{Data from latest relayout event which occurs
when the user zooms or pans on the plot}

\item{restyleData}{Data from latest restyle event which occurs
when the user toggles a legend item}

\item{figure}{Plotly `figure` object. See schema:
https://plot.ly/javascript/reference
Only supports `data` array and `layout` object.
`config` is set separately by the `config` property,
and `frames` is not supported.}

\item{style}{Generic style overrides on the plot div}

\item{className}{className of the parent div}

\item{animate}{Beta: If true, animate between updates using
plotly.js's `animate` function}

\item{animation_options}{Beta: Object containing animation settings.
Only applies if `animate` is `true`}

\item{config}{Plotly.js config options.
See https://plot.ly/javascript/configuration-options/
for more info.}

\item{loading_state}{Object that holds the loading state object coming from dash-renderer}
}
