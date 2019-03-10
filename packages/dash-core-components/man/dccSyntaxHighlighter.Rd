% Auto-generated: do not edit by hand
\name{dccSyntaxHighlighter}

\alias{dccSyntaxHighlighter}

\title{SyntaxHighlighter component}

\description{
A component for pretty printing code.
}

\usage{
dccSyntaxHighlighter(children=NULL, id=NULL, language=NULL, theme=NULL, customStyle=NULL, codeTagProps=NULL, useInlineStyles=NULL, showLineNumbers=NULL, startingLineNumber=NULL, lineNumberContainerStyle=NULL, lineNumberStyle=NULL, wrapLines=NULL, lineStyle=NULL, loading_state=NULL)
}

\arguments{
\item{children}{The text to display and highlight}

\item{id}{}

\item{language}{the language to highlight code in.}

\item{theme}{theme: light or dark}

\item{customStyle}{prop that will be combined with the top level style on the pre tag, styles here will overwrite earlier styles.}

\item{codeTagProps}{props that will be spread into the <code> tag that is the direct parent of the highlighted code elements. Useful for styling/assigning classNames.}

\item{useInlineStyles}{if this prop is passed in as false, react syntax highlighter will not add style objects to elements, and will instead append classNames. You can then style the code block by using one of the CSS files provided by highlight.js.}

\item{showLineNumbers}{if this is enabled line numbers will be shown next to the code block.}

\item{startingLineNumber}{if showLineNumbers is enabled the line numbering will start from here.}

\item{lineNumberContainerStyle}{the line numbers container default to appearing to the left with 10px of right padding. You can use this to override those styles.}

\item{lineNumberStyle}{inline style to be passed to the span wrapping each number. Can be either an object or a function that recieves current line number as argument and returns style object.}

\item{wrapLines}{a boolean value that determines whether or not each line of code should be wrapped in a parent element. defaults to false, when false one can not take action on an element on the line level. You can see an example of what this enables here}

\item{lineStyle}{inline style to be passed to the span wrapping each line if wrapLines is true. Can be either an object or a function that recieves current line number as argument and returns style object.}

\item{loading_state}{Object that holds the loading state object coming from dash-renderer}
}
