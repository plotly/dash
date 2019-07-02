% Auto-generated: do not edit by hand
\name{dccMarkdown}

\alias{dccMarkdown}

\title{Markdown component}

\description{
A component that renders Markdown text as specified by the GitHub Markdown spec. These component uses [react-markdown](https://rexxars.github.io/react-markdown/) under the hood.
}

\usage{
dccMarkdown(children=NULL, id=NULL, className=NULL, dangerously_allow_html=NULL,
dedent=NULL, highlight_config=NULL, loading_state=NULL, style=NULL)
}

\arguments{
\item{children}{Character | list of characters. A markdown string (or array of strings) that adhreres to the CommonMark spec}

\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{className}{Character. Class name of the container element}

\item{dangerously_allow_html}{Logical. A boolean to control raw HTML escaping.
Setting HTML from code is risky because it's easy to
inadvertently expose your users to a cross-site scripting (XSS)
(https://en.wikipedia.org/wiki/Cross-site_scripting) attack.}

\item{dedent}{Logical. Remove matching leading whitespace from all lines.
Lines that are empty, or contain *only* whitespace, are ignored.
Both spaces and tab characters are removed, but only if they match;
we will not convert tabs to spaces or vice versa.}

\item{highlight_config}{Lists containing elements 'theme'.
those elements have the following types:
  - theme (a value equal to: 'dark', 'light'; optional): color scheme; default 'light'. Config options for syntax highlighting.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}

\item{style}{Named list. User-defined inline styles for the rendered Markdown}
}
