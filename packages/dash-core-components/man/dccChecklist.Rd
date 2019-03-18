% Auto-generated: do not edit by hand
\name{dccChecklist}

\alias{dccChecklist}

\title{Checklist component}

\description{
Checklist is a component that encapsulates several checkboxes. The values and labels of the checklist is specified in the `options` property and the checked items are specified with the `values` property. Each checkbox is rendered as an input with a surrounding label.
}

\usage{
dccChecklist(id=NULL, options=NULL, values=NULL, className=NULL, style=NULL, inputStyle=NULL, inputClassName=NULL, labelStyle=NULL, labelClassName=NULL, loading_state=NULL, ...)
}

\arguments{
\item{id}{}

\item{options}{An array of options}

\item{values}{The currently selected value}

\item{className}{The class of the container (div)}

\item{style}{The style of the container (div)}

\item{inputStyle}{The style of the <input> checkbox element}

\item{inputClassName}{The class of the <input> checkbox element}

\item{labelStyle}{The style of the <label> that wraps the checkbox input
 and the option's label}

\item{labelClassName}{The class of the <label> that wraps the checkbox input
 and the option's label}

\item{loading_state}{Object that holds the loading state object coming from dash-renderer}
}
