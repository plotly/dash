% Auto-generated: do not edit by hand
\name{coreTabs}

\alias{coreTabs}

\title{Tabs component}

\description{
A Dash component that lets you render pages with tabs - the Tabs component's children can be dcc.Tab components, which can hold a label that will be displayed as a tab, and can in turn hold children components that will be that tab's content.
}

\usage{
coreTabs(id=NULL, value=NULL, className=NULL, content_className=NULL, parent_className=NULL, style=NULL, parent_style=NULL, content_style=NULL, vertical=NULL, mobile_breakpoint=NULL, colors=NULL, ...)
}

\arguments{
\item{id}{The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{value}{The value of the currently selected Tab}

\item{className}{Appends a class to the Tabs container holding the individual Tab components.}

\item{content_className}{Appends a class to the Tab content container holding the children of the Tab that is selected.}

\item{parent_className}{Appends a class to the top-level parent container holding both the Tabs container and the content container.}

\item{style}{Appends (inline) styles to the Tabs container holding the individual Tab components.}

\item{parent_style}{Appends (inline) styles to the top-level parent container holding both the Tabs container and the content container.}

\item{content_style}{Appends (inline) styles to the tab content container holding the children of the Tab that is selected.}

\item{vertical}{Renders the tabs vertically (on the side)}

\item{mobile_breakpoint}{Breakpoint at which tabs are rendered full width (can be 0 if you don't want full width tabs on mobile)}

\item{colors}{Holds the colors used by the Tabs and Tab components. If you set these, you should specify colors for all properties, so:
colors: {
   border: '#d6d6d6',
   primary: '#1975FA',
   background: '#f9f9f9'
 }}

\item{...}{wildcards of the form: `data-*` or `aria-*`}
}
