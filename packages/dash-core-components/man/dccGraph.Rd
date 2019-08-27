% Auto-generated: do not edit by hand
\name{dccGraph}

\alias{dccGraph}

\title{Graph component}

\description{
Graph can be used to render any plotly.js-powered data visualization.  You can define callbacks based on user interaction with Graphs such as hovering, clicking or selecting
}

\usage{
dccGraph(id=NULL, clickData=NULL, clickAnnotationData=NULL, hoverData=NULL,
clear_on_unhover=NULL, selectedData=NULL, relayoutData=NULL, extendData=NULL,
restyleData=NULL, figure=NULL, style=NULL, className=NULL, animate=NULL,
animation_options=NULL, config=NULL, loading_state=NULL)
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

\item{figure}{Lists containing elements 'data', 'layout', 'frames'.
those elements have the following types:
  - data (list of named lists; optional)
  - layout (named list; optional)
  - frames (list of named lists; optional). Plotly `figure` object. See schema:
https://plot.ly/javascript/reference

`config` is set separately by the `config` property}

\item{style}{Named list. Generic style overrides on the plot div}

\item{className}{Character. className of the parent div}

\item{animate}{Logical. Beta: If true, animate between updates using
plotly.js's `animate` function}

\item{animation_options}{Named list. Beta: Object containing animation settings.
Only applies if `animate` is `true`}

\item{config}{Lists containing elements 'staticplot', 'plotlyserverurl', 'editable', 'edits', 'autosizable', 'responsive', 'queuelength', 'fillframe', 'framemargins', 'scrollzoom', 'doubleclick', 'doubleclickdelay', 'showtips', 'showaxisdraghandles', 'showaxisrangeentryboxes', 'showlink', 'senddata', 'linktext', 'displaymodebar', 'showsendtocloud', 'showeditinchartstudio', 'modebarbuttonstoremove', 'modebarbuttonstoadd', 'modebarbuttons', 'toimagebuttonoptions', 'displaylogo', 'watermark', 'plotglpixelratio', 'topojsonurl', 'mapboxaccesstoken', 'locale', 'locales'.
those elements have the following types:
  - staticplot (logical; optional): no interactivity, for export or image generation
  - plotlyserverurl (character; optional): base url for a plotly cloud instance, if `showsendtocloud` is enabled
  - editable (logical; optional): we can edit titles, move annotations, etc - sets all pieces of `edits`
unless a separate `edits` config item overrides individual parts
  - edits (optional): a set of editable properties. edits has the following type: lists containing elements 'annotationposition', 'annotationtail', 'annotationtext', 'axistitletext', 'colorbarposition', 'colorbartitletext', 'legendposition', 'legendtext', 'shapeposition', 'titletext'.
those elements have the following types:
  - annotationposition (logical; optional): the main anchor of the annotation, which is the
text (if no arrow) or the arrow (which drags the whole thing leaving
the arrow length & direction unchanged)
  - annotationtail (logical; optional): just for annotations with arrows, change the length and direction of the arrow
  - annotationtext (logical; optional)
  - axistitletext (logical; optional)
  - colorbarposition (logical; optional)
  - colorbartitletext (logical; optional)
  - legendposition (logical; optional)
  - legendtext (logical; optional): edit the trace name fields from the legend
  - shapeposition (logical; optional)
  - titletext (logical; optional): the global `layout.title`
  - autosizable (logical; optional): do autosize once regardless of layout.autosize
(use default width or height values otherwise)
  - responsive (logical; optional): whether to change layout size when the window size changes
  - queuelength (numeric; optional): set the length of the undo/redo queue
  - fillframe (logical; optional): if we do autosize, do we fill the container or the screen?
  - framemargins (numeric; optional): if we do autosize, set the frame margins in percents of plot size
  - scrollzoom (logical; optional): mousewheel or two-finger scroll zooms the plot
  - doubleclick (a value equal to: false, 'reset', 'autosize', 'reset+autosize'; optional): double click interaction (false, 'reset', 'autosize' or 'reset+autosize')
  - doubleclickdelay (numeric; optional): delay for registering a double-click event in ms. the
minimum value is 100 and the maximum value is 1000. by
default this is 300.
  - showtips (logical; optional): new users see some hints about interactivity
  - showaxisdraghandles (logical; optional): enable axis pan/zoom drag handles
  - showaxisrangeentryboxes (logical; optional): enable direct range entry at the pan/zoom drag points
(drag handles must be enabled above)
  - showlink (logical; optional): link to open this plot in plotly
  - senddata (logical; optional): if we show a link, does it contain data or just link to a plotly file?
  - linktext (character; optional): text appearing in the senddata link
  - displaymodebar (a value equal to: true, false, 'hover'; optional): display the mode bar (true, false, or 'hover')
  - showsendtocloud (logical; optional): should we include a modebar button to send this data to a
plotly cloud instance, linked by `plotlyserverurl`.
by default this is false.
  - showeditinchartstudio (logical; optional): should we show a modebar button to send this data to a
plotly chart studio plot. if both this and showsendtocloud
are selected, only showeditinchartstudio will be
honored. by default this is false.
  - modebarbuttonstoremove (unnamed list; optional): remove mode bar button by name.
all modebar button names at https://github.com/plotly/plotly.js/blob/master/src/components/modebar/buttons.js
common names include:
senddatatocloud;
(2d) zoom2d, pan2d, select2d, lasso2d, zoomin2d, zoomout2d, autoscale2d, resetscale2d;
(cartesian) hoverclosestcartesian, hovercomparecartesian;
(3d) zoom3d, pan3d, orbitrotation, tablerotation, handledrag3d, resetcameradefault3d, resetcameralastsave3d, hoverclosest3d;
(geo) zoomingeo, zoomoutgeo, resetgeo, hoverclosestgeo;
hoverclosestgl2d, hoverclosestpie, togglehover, resetviews.
  - modebarbuttonstoadd (unnamed list; optional): add mode bar button using config objects
  - modebarbuttons (logical | numeric | character | named list | unnamed list; optional): fully custom mode bar buttons as nested array,
where the outer arrays represents button groups, and
the inner arrays have buttons config objects or names of default buttons
  - toimagebuttonoptions (optional): modifications to how the toimage modebar button works. toimagebuttonoptions has the following type: lists containing elements 'format', 'filename', 'width', 'height', 'scale'.
those elements have the following types:
  - format (a value equal to: 'jpeg', 'png', 'webp', 'svg'; optional): the file format to create
  - filename (character; optional): the name given to the downloaded file
  - width (numeric; optional): width of the downloaded file, in px
  - height (numeric; optional): height of the downloaded file, in px
  - scale (numeric; optional): extra resolution to give the file after
rendering it with the given width and height
  - displaylogo (logical; optional): add the plotly logo on the end of the mode bar
  - watermark (logical; optional): add the plotly logo even with no modebar
  - plotglpixelratio (numeric; optional): increase the pixel ratio for gl plot images
  - topojsonurl (character; optional): url to topojson files used in geo charts
  - mapboxaccesstoken (logical | numeric | character | named list | unnamed list; optional): mapbox access token (required to plot mapbox trace types)
if using an mapbox atlas server, set this option to '',
so that plotly.js won't attempt to authenticate to the public mapbox server.
  - locale (character; optional): the locale to use. locales may be provided with the plot
(`locales` below) or by loading them on the page, see:
https://github.com/plotly/plotly.js/blob/master/dist/readme.md#to-include-localization
  - locales (named list; optional): localization definitions, if you choose to provide them with the
plot rather than registering them globally.. Plotly.js config options.
See https://plot.ly/javascript/configuration-options/
for more info.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
