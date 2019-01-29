% Auto-generated: do not edit by hand
\name{coreConfirmDialogProvider}

\alias{coreConfirmDialogProvider}

\title{ConfirmDialogProvider component}

\description{
A wrapper component that will display a confirmation dialog when its child component has been clicked on.  For example: ``` dcc.ConfirmDialogProvider(     html.Button('click me', id='btn'),     message='Danger - Are you sure you want to continue.'     id='confirm') ```
}

\usage{
coreConfirmDialogProvider(id=NULL, message=NULL, submit_n_clicks=NULL, submit_n_clicks_timestamp=NULL, cancel_n_clicks=NULL, cancel_n_clicks_timestamp=NULL, displayed=NULL, ...)
}

\arguments{
\item{id}{}

\item{message}{Message to show in the popup.}

\item{submit_n_clicks}{Number of times the submit was clicked}

\item{submit_n_clicks_timestamp}{Last time the submit button was clicked.}

\item{cancel_n_clicks}{Number of times the popup was canceled.}

\item{cancel_n_clicks_timestamp}{Last time the cancel button was clicked.}

\item{displayed}{Is the modal currently displayed.}
}
