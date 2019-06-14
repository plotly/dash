% Auto-generated: do not edit by hand
\name{dccGraph}

\alias{dccGraph}

\title{Graph component}

\description{
Graph can be used to render any plotly.js-powered data visualization.  You can define callbacks based on user interaction with Graphs such as hovering, clicking or selecting
}

\usage{
dccGraph(dccGraph(id=NULL, clickData=NULL, clickAnnotationData=NULL, hoverData=NULL,
clear_on_unhover=NULL, selectedData=NULL, relayoutData=NULL, extendData=NULL,
restyleData=NULL, figure=NULL, style=NULL, className=NULL, animate=NULL,
animation_options=NULL, config=NULL, loading_state=NULL))
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{clickData}{Named list. Data from latest click event. Read-only.}

\item{clickAnnotationData}{Named list. Data from latest click annotation event. Read-only.}

\item{hoverData}{Named list. Data from latest hover event. Read-only.}

\item{clear_on_unhover}{Logical. If True, `clear_on_unhover` will clear the `hoverData` property
when the user "unhovers" from a point.
If False, then the `hoverData` property will be equal to the
data from the last point that was hovered over.}

\item{selectedData}{Named list. Data from latest select event. Read-only.}

\item{relayoutData}{Named list. Data from latest relayout event which occurs
when the user zooms or pans on the plot or other
layout-level edits. Has the form `{<attr string>: <value>}`
describing the changes made. Read-only.}

\item{extendData}{Unnamed list | named list. Data that should be appended to existing traces. Has the form
`[updateData, traceIndices, maxPoints]`, where `updateData` is an object
containing the data to extend, `traceIndices` (optional) is an array of
trace indices that should be extended, and `maxPoints` (optional) is
either an integer defining the maximum number of points allowed or an
object with key:value pairs matching `updateData`
Reference the Plotly.extendTraces API for full usage:
https://plot.ly/javascript/plotlyjs-function-reference/#plotlyextendtraces}

\item{restyleData}{Unnamed list. Data from latest restyle event which occurs
when the user toggles a legend item, changes
parcoords selections, or other trace-level edits.
Has the form `[edits, indices]`, where `edits` is an object
`{<attr string>: <value>}` describing the changes made,
and `indices` is an array of trace indices that were edited.
Read-only.}

\item{figure}{Plotly `figure` object. See schema:
https://plot.ly/javascript/reference

`config` is set separately by the `config` property}

\item{style}{Named list. Generic style overrides on the plot div}

\item{className}{Character. className of the parent div}

\item{animate}{Logical. Beta: If true, animate between updates using
plotly.js's `animate` function}

\item{animation_options}{Named list. Beta: Object containing animation settings.
Only applies if `animate` is `true`}

\item{config}{Plotly.js config options.
See https://plot.ly/javascript/configuration-options/
for more info.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
