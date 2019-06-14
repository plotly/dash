% Auto-generated: do not edit by hand
\name{dccRadioItems}

\alias{dccRadioItems}

\title{RadioItems component}

\description{
RadioItems is a component that encapsulates several radio item inputs. The values and labels of the RadioItems is specified in the `options` property and the seleced item is specified with the `value` property. Each radio item is rendered as an input with a surrounding label.
}

\usage{
dccRadioItems(dccRadioItems(id=NULL, options=NULL, value=NULL, style=NULL, className=NULL,
inputStyle=NULL, inputClassName=NULL, labelStyle=NULL, labelClassName=NULL,
loading_state=NULL))
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{options}{List. An array of options}

\item{value}{Character | numeric. The currently selected value}

\item{style}{Named list. The style of the container (div)}

\item{className}{Character. The class of the container (div)}

\item{inputStyle}{Named list. The style of the <input> radio element}

\item{inputClassName}{Character. The class of the <input> radio element}

\item{labelStyle}{Named list. The style of the <label> that wraps the radio input
 and the option's label}

\item{labelClassName}{Character. The class of the <label> that wraps the radio input
 and the option's label}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
