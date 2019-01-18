% Auto-generated: do not edit by hand
\name{coreInterval}

\alias{coreInterval}

\title{Interval component}

\description{
A component that repeatedly fires an event ("interval") with a fixed time delay between each event. Interval is good for triggering a component on a recurring basis. The time delay is set with the property "interval" in milliseconds.
}

\usage{
coreInterval(id=NULL, interval=NULL, disabled=NULL, n_intervals=NULL, max_intervals=NULL, setProps=NULL, ...)
}

\arguments{
\item{id}{}

\item{interval}{This component will fire an event every `interval`
milliseconds with the event name `setInterval`}

\item{disabled}{If True, the interval will no longer trigger
an event.}

\item{n_intervals}{Number of times the interval has passed}

\item{max_intervals}{Number of times the interval will be fired. If -1, then the interval has no limit (the default) and if 0 then the interval stops running.}

\item{setProps}{Dash assigned callback}

\item{...}{wildcards of the form: `data-*` or `aria-*`}
}
