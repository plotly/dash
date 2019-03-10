% Auto-generated: do not edit by hand
\name{dccSlider}

\alias{dccSlider}

\title{Slider component}

\description{
A slider component with a single handle.
}

\usage{
dccSlider(id=NULL, marks=NULL, value=NULL, className=NULL, disabled=NULL, dots=NULL, included=NULL, min=NULL, max=NULL, step=NULL, vertical=NULL, updatemode=NULL, loading_state=NULL)
}

\arguments{
\item{id}{}

\item{marks}{Marks on the slider.
The key determines the position,
and the value determines what will show.
If you want to set the style of a specific mark point,
the value should be an object which
contains style and label properties.}

\item{value}{The value of the input}

\item{className}{Additional CSS class for the root DOM node}

\item{disabled}{If true, the handles can't be moved.}

\item{dots}{When the step value is greater than 1,
you can set the dots to true if you want to
render the slider with dots.}

\item{included}{If the value is true, it means a continuous
value is included. Otherwise, it is an independent value.}

\item{min}{Minimum allowed value of the slider}

\item{max}{Maximum allowed value of the slider}

\item{step}{Value by which increments or decrements are made}

\item{vertical}{If true, the slider will be vertical}

\item{updatemode}{Determines when the component should update
its value. If `mouseup`, then the slider
will only trigger its value when the user has
finished dragging the slider. If `drag`, then
the slider will update its value continuously
as it is being dragged.
Only use `drag` if your updates are fast.}

\item{loading_state}{Object that holds the loading state object coming from dash-renderer}
}
