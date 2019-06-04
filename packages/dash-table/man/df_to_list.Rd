% Auto-generated: do not edit by hand
\name{df_to_list}

\alias{df_to_list}

\title{Convert data.frame objects to list-of-lists format}

\description{
Convert a \code{\link{data.frame}} to a list of lists for compatibility with \code{\link{dashDataTable}}. The function will return a nested list object in which the sublists contain named elements of varying type; the names correspond to the column names in the original \code{\link{data.frame}}.
}

\usage{
df_to_list(df=NULL)
}

\arguments{
\item{df}{A \code{data.frame} object, which will be transformed into a list of lists. Each row will become a single named list, in which the elements are named as the columns from which they were extracted.}
}
