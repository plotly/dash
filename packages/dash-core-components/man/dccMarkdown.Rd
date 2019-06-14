% Auto-generated: do not edit by hand
\name{dccMarkdown}

\alias{dccMarkdown}

\title{Markdown component}

\description{
A component that renders Markdown text as specified by the GitHub Markdown spec. These component uses [react-markdown](https://rexxars.github.io/react-markdown/) under the hood.
}

\usage{
dccMarkdown(dccMarkdown(children=NULL, id=NULL, className=NULL, containerProps=NULL,
dangerously_allow_html=NULL, highlight_config=NULL, loading_state=NULL,
style=NULL))
}

\arguments{
\item{children}{Character | list of characters. A markdown string (or array of strings) that adhreres to the CommonMark spec}

\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{className}{Character. Class name of the container element}

\item{containerProps}{Named list. An object containing custom element props to put on the container
element such as id or style}

\item{dangerously_allow_html}{Logical. A boolean to control raw HTML escaping.
Setting HTML from code is risky because it's easy to
inadvertently expose your users to a cross-site scripting (XSS)
(https://en.wikipedia.org/wiki/Cross-site_scripting) attack.}

\item{highlight_config}{Config options for syntax highlighting.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}

\item{style}{Named list. User-defined inline styles for the rendered Markdown}
}
