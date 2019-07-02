% Auto-generated: do not edit by hand
\name{dccTab}

\alias{dccTab}

\title{Tab component}

\description{
Part of dcc.Tabs - this is the child Tab component used to render a tabbed page. Its children will be set as the content of that tab, which if clicked will become visible.
}

\usage{
dccTab(children=NULL, id=NULL, label=NULL, value=NULL, disabled=NULL,
disabled_style=NULL, disabled_className=NULL, className=NULL,
selected_className=NULL, style=NULL, selected_style=NULL, loading_state=NULL)
}

\arguments{
\item{children}{A list of or a singular dash component, string or number. The content of the tab - will only be displayed if this tab is selected}

\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{label}{Character. The tab's label}

\item{value}{Character. Value for determining which Tab is currently selected}

\item{disabled}{Logical. Determines if tab is disabled or not - defaults to false}

\item{disabled_style}{Named list. Overrides the default (inline) styles when disabled}

\item{disabled_className}{Character. Appends a class to the Tab component when it is disabled.}

\item{className}{Character. Appends a class to the Tab component.}

\item{selected_className}{Character. Appends a class to the Tab component when it is selected.}

\item{style}{Named list. Overrides the default (inline) styles for the Tab component.}

\item{selected_style}{Named list. Overrides the default (inline) styles for the Tab component when it is selected.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
