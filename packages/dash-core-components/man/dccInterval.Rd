% Auto-generated: do not edit by hand
\name{dccInterval}

\alias{dccInterval}

\title{Interval component}

\description{
A component that repeatedly increments a counter `n_intervals` with a fixed time delay between each increment. Interval is good for triggering a component on a recurring basis. The time delay is set with the property "interval" in milliseconds.
}

\usage{
dccInterval(id=NULL, interval=NULL, disabled=NULL, n_intervals=NULL, max_intervals=NULL, ...)
}

\arguments{
\item{id}{}

\item{interval}{This component will increment the counter `n_intervals` every
`interval` milliseconds}

\item{disabled}{If True, the counter will no longer update}

\item{n_intervals}{Number of times the interval has passed}

\item{max_intervals}{Number of times the interval will be fired.
If -1, then the interval has no limit (the default)
and if 0 then the interval stops running.}
}
