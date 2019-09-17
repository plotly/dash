% Auto-generated: do not edit by hand
\name{dccRadioItems}

\alias{dccRadioItems}

\title{RadioItems component}

\description{
RadioItems is a component that encapsulates several radio item inputs. The values and labels of the RadioItems is specified in the `options` property and the seleced item is specified with the `value` property. Each radio item is rendered as an input with a surrounding label.
}

\usage{
dccRadioItems(id=NULL, options=NULL, value=NULL, style=NULL, className=NULL, inputStyle=NULL,
inputClassName=NULL, labelStyle=NULL, labelClassName=NULL, loading_state=NULL,
persistence=NULL, persisted_props=NULL, persistence_type=NULL)
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{options}{List of lists containing elements 'label', 'value', 'disabled'.
those elements have the following types:
  - label (character | numeric; required): the radio item's label
  - value (character | numeric; required): the value of the radio item. this value
corresponds to the items specified in the
`value` property.
  - disabled (logical; optional): if true, this radio item is disabled and can't be clicked on.s. An array of options}

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

\item{persistence}{Logical | character | numeric. Used to allow user interactions in this component to be persisted when
the component - or the page - is refreshed. If `persisted` is truthy and
hasn't changed from its previous value, a `value` that the user has
changed while using the app will keep that change, as long as
the new `value` also matches what was given originally.
Used in conjunction with `persistence_type`.}

\item{persisted_props}{List of a value equal to: 'value's. Properties whose user interactions will persist after refreshing the
component or the page. Since only `value` is allowed this prop can
normally be ignored.}

\item{persistence_type}{A value equal to: 'local', 'session', 'memory'. Where persisted user changes will be stored:
memory: only kept in memory, reset on page refresh.
local: window.localStorage, data is kept after the browser quit.
session: window.sessionStorage, data is cleared once the browser quit.}
}
