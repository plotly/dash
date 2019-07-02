% Auto-generated: do not edit by hand
\name{dccChecklist}

\alias{dccChecklist}

\title{Checklist component}

\description{
Checklist is a component that encapsulates several checkboxes. The values and labels of the checklist are specified in the `options` property and the checked items are specified with the `value` property. Each checkbox is rendered as an input with a surrounding label.
}

\usage{
dccChecklist(id=NULL, options=NULL, value=NULL, className=NULL, style=NULL, inputStyle=NULL,
inputClassName=NULL, labelStyle=NULL, labelClassName=NULL, loading_state=NULL)
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{options}{List of lists containing elements 'label', 'value', 'disabled'.
those elements have the following types:
  - label (character | numeric; required): the checkbox's label
  - value (character | numeric; required): the value of the checkbox. this value
corresponds to the items specified in the
`value` property.
  - disabled (logical; optional): if true, this checkbox is disabled and can't be clicked on.s. An array of options}

\item{value}{List of character | numerics. The currently selected value}

\item{className}{Character. The class of the container (div)}

\item{style}{Named list. The style of the container (div)}

\item{inputStyle}{Named list. The style of the <input> checkbox element}

\item{inputClassName}{Character. The class of the <input> checkbox element}

\item{labelStyle}{Named list. The style of the <label> that wraps the checkbox input
 and the option's label}

\item{labelClassName}{Character. The class of the <label> that wraps the checkbox input
 and the option's label}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
