% Auto-generated: do not edit by hand
\name{dccSlider}

\alias{dccSlider}

\title{Slider component}

\description{
A slider component with a single handle.
}

\usage{
dccSlider(id=NULL, marks=NULL, value=NULL, className=NULL, disabled=NULL, dots=NULL,
included=NULL, min=NULL, max=NULL, tooltip=NULL, step=NULL, vertical=NULL,
updatemode=NULL, loading_state=NULL)
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{marks}{List with named elements and values of type character | lists containing elements 'label', 'style'.
those elements have the following types:
  - label (character; optional)
  - style (named list; optional). Marks on the slider.
The key determines the position (a number),
and the value determines what will show.
If you want to set the style of a specific mark point,
the value should be an object which
contains style and label properties.}

\item{value}{Numeric. The value of the input}

\item{className}{Character. Additional CSS class for the root DOM node}

\item{disabled}{Logical. If true, the handles can't be moved.}

\item{dots}{Logical. When the step value is greater than 1,
you can set the dots to true if you want to
render the slider with dots.}

\item{included}{Logical. If the value is true, it means a continuous
value is included. Otherwise, it is an independent value.}

\item{min}{Numeric. Minimum allowed value of the slider}

\item{max}{Numeric. Maximum allowed value of the slider}

\item{tooltip}{Lists containing elements 'always_visible', 'placement'.
those elements have the following types:
  - always_visible (logical; optional): determines whether tooltips should always be visible
(as opposed to the default, visible on hover)
  - placement (a value equal to: 'left', 'right', 'top', 'bottom', 'topleft', 'topright', 'bottomleft', 'bottomright'; optional): determines the placement of tooltips
see https://github.com/react-component/tooltip#api
top/bottom{*} sets the _origin_ of the tooltip, so e.g. `topleft` will
in reality appear to be on the top right of the handle. }

\item{step}{Numeric. Value by which increments or decrements are made}

\item{vertical}{Logical. If true, the slider will be vertical}

\item{updatemode}{A value equal to: 'mouseup', 'drag'. Determines when the component should update
its value. If `mouseup`, then the slider
will only trigger its value when the user has
finished dragging the slider. If `drag`, then
the slider will update its value continuously
as it is being dragged.
Only use `drag` if your updates are fast.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
