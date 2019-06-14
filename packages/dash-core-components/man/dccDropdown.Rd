% Auto-generated: do not edit by hand
\name{dccDropdown}

\alias{dccDropdown}

\title{Dropdown component}

\description{
Dropdown is an interactive dropdown element for selecting one or more items. The values and labels of the dropdown items are specified in the `options` property and the selected item(s) are specified with the `value` property.  Use a dropdown when you have many options (more than 5) or when you are constrained for space. Otherwise, you can use RadioItems or a Checklist, which have the benefit of showing the users all of the items at once.
}

\usage{
dccDropdown(dccDropdown(id=NULL, options=NULL, value=NULL, optionHeight=NULL,
className=NULL, clearable=NULL, disabled=NULL, multi=NULL, placeholder=NULL,
searchable=NULL, style=NULL, loading_state=NULL))
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{options}{List. An array of options {label: [string|number], value: [string|number]},
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
}
