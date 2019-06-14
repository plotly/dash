% Auto-generated: do not edit by hand
\name{dccStore}

\alias{dccStore}

\title{Store component}

\description{
Easily keep data on the client side with this component. The data is not inserted in the DOM. Data can be in memory, localStorage or sessionStorage. The data will be kept with the id as key.
}

\usage{
dccStore(dccStore(id=NULL, storage_type=NULL, data=NULL, clear_data=NULL,
modified_timestamp=NULL))
}

\arguments{
\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{storage_type}{A value equal to: 'local', 'session', 'memory'. The type of the web storage.

memory: only kept in memory, reset on page refresh.
local: window.localStorage, data is kept after the browser quit.
session: window.sessionStorage, data is cleared once the browser quit.}

\item{data}{Named list | unnamed list | numeric | character | logical. The stored data for the id.}

\item{clear_data}{Logical. Set to true to remove the data contained in `data_key`.}

\item{modified_timestamp}{Numeric. The last time the storage was modified.}
}
