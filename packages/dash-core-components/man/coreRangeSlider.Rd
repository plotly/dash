% Auto-generated: do not edit by hand
\name{coreRangeSlider}

\alias{coreRangeSlider}

\title{RangeSlider component}

\description{
A double slider with two handles. Used for specifying a range of numerical values.
}

\usage{
coreRangeSlider(id=NULL, marks=NULL, value=NULL, allowCross=NULL, className=NULL, count=NULL, disabled=NULL, dots=NULL, included=NULL, min=NULL, max=NULL, pushable=NULL, step=NULL, vertical=NULL, updatemode=NULL, ...)
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

\item{allowCross}{allowCross could be set as true to allow those handles to cross.}

\item{className}{Additional CSS class for the root DOM node}

\item{count}{Determine how many ranges to render, and multiple handles
will be rendered (number + 1).}

\item{disabled}{If true, the handles can't be moved.}

\item{dots}{When the step value is greater than 1,
you can set the dots to true if you want to
render the slider with dots.}

\item{included}{If the value is true, it means a continuous
value is included. Otherwise, it is an independent value.}

\item{min}{Minimum allowed value of the slider}

\item{max}{Maximum allowed value of the slider}

\item{pushable}{pushable could be set as true to allow pushing of
surrounding handles when moving an handle.
When set to a number, the number will be the
minimum ensured distance between handles.}

\item{step}{Value by which increments or decrements are made}

\item{vertical}{If true, the slider will be vertical}

\item{updatemode}{Determines when the component should update
its value. If `mouseup`, then the slider
will only trigger its value when the user has
finished dragging the slider. If `drag`, then
the slider will update its value continuously
as it is being dragged.
Only use `drag` if your updates are fast.}
}
