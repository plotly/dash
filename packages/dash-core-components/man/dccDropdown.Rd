% Auto-generated: do not edit by hand
\name{dccDropdown}

\alias{dccDropdown}

\title{Dropdown component}

\description{
Dropdown is an interactive dropdown element for selecting one or more items. The values and labels of the dropdown items are specified in the `options` property and the selected item(s) are specified with the `value` property.  Use a dropdown when you have many options (more than 5) or when you are constrained for space. Otherwise, you can use RadioItems or a Checklist, which have the benefit of showing the users all of the items at once.
}

\usage{
dccDropdown(id=NULL, options=NULL, value=NULL, className=NULL, clearable=NULL, disabled=NULL, multi=NULL, placeholder=NULL, searchable=NULL, style=NULL, loading_state=NULL, ...)
}

\arguments{
\item{id}{}

\item{options}{An array of options}

\item{value}{The value of the input. If `multi` is false (the default)
then value is just a string that corresponds to the values
provided in the `options` property. If `multi` is true, then
multiple values can be selected at once, and `value` is an
array of items with values corresponding to those in the
`options` prop.}

\item{className}{className of the dropdown element}

\item{clearable}{Whether or not the dropdown is "clearable", that is, whether or
not a small "x" appears on the right of the dropdown that removes
the selected value.}

\item{disabled}{If true, the option is disabled}

\item{multi}{If true, the user can select multiple values}

\item{placeholder}{The grey, default text shown when no option is selected}

\item{searchable}{Whether to enable the searching feature or not}

\item{style}{}

\item{loading_state}{Object that holds the loading state object coming from dash-renderer}
}
