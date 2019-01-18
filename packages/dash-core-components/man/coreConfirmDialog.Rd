% Auto-generated: do not edit by hand
\name{coreConfirmDialog}

\alias{coreConfirmDialog}

\title{ConfirmDialog component}

\description{
ConfirmDialog is used to display the browser's native "confirm" modal, with an optional message and two buttons ("OK" and "Cancel"). This ConfirmDialog can be used in conjunction with buttons when the user is performing an action that should require an extra step of verification.
}

\usage{
coreConfirmDialog(id=NULL, message=NULL, submit_n_clicks=NULL, submit_n_clicks_timestamp=NULL, cancel_n_clicks=NULL, cancel_n_clicks_timestamp=NULL, displayed=NULL, key=NULL, ...)
}

\arguments{
\item{id}{}

\item{message}{Message to show in the popup.}

\item{submit_n_clicks}{Number of times the submit button was clicked}

\item{submit_n_clicks_timestamp}{Last time the submit button was clicked.}

\item{cancel_n_clicks}{Number of times the popup was canceled.}

\item{cancel_n_clicks_timestamp}{Last time the cancel button was clicked.}

\item{displayed}{Set to true to send the ConfirmDialog.}

\item{key}{}

\item{...}{wildcards of the form: `data-*` or `aria-*`}
}
