% Auto-generated: do not edit by hand
\name{dccDropdown}

\alias{dccDropdown}

\title{Dropdown component}

\description{
Dropdown is an interactive dropdown element for selecting one or more items. The values and labels of the dropdown items are specified in the `options` property and the selected item(s) are specified with the `value` property.  Use a dropdown when you have many options (more than 5) or when you are constrained for space. Otherwise, you can use RadioItems or a Checklist, which have the benefit of showing the users all of the items at once.
}

\usage{
dccDropdown(id=NULL, options=NULL, value=NULL, optionHeight=NULL, className=NULL,
clearable=NULL, disabled=NULL, multi=NULL, placeholder=NULL, searchable=NULL,
style=NULL, loading_state=NULL, persistence=NULL, persisted_props=NULL,
persistence_type=NULL)
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{options}{List of lists containing elements 'label', 'value', 'disabled'.
those elements have the following types:
  - label (character | numeric; required): the dropdown's label
  - value (character | numeric; required): the value of the dropdown. this value
corresponds to the items specified in the
`value` property.
  - disabled (logical; optional): if true, this option is disabled and cannot be selected.s. An array of options {label: [string|number], value: [string|number]},
an optional disabled field can be used for each option}

\item{value}{Character | numeric | list of character | numerics. The value of the input. If `multi` is false (the default)
then value is just a string that corresponds to the values
provided in the `options` property. If `multi` is true, then
multiple values can be selected at once, and `value` is an
array of items with values corresponding to those in the
`options` prop.}

\item{optionHeight}{Numeric. height of each option. Can be increased when label lengths would wrap around}

\item{className}{Character. className of the dropdown element}

\item{clearable}{Logical. Whether or not the dropdown is "clearable", that is, whether or
not a small "x" appears on the right of the dropdown that removes
the selected value.}

\item{disabled}{Logical. If true, this dropdown is disabled and the selection cannot be changed.}

\item{multi}{Logical. If true, the user can select multiple values}

\item{placeholder}{Character. The grey, default text shown when no option is selected}

\item{searchable}{Logical. Whether to enable the searching feature or not}

\item{style}{Named list. Defines CSS styles which will override styles previously set.}

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
