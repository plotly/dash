% Auto-generated: do not edit by hand
\name{dccLogoutButton}

\alias{dccLogoutButton}

\title{LogoutButton component}

\description{
Logout button to submit a form post request to the `logout_url` prop. Usage is intended for dash-deployment-server authentication.  DDS usage:  `dcc.LogoutButton(logout_url=os.getenv('DASH_LOGOUT_URL'))`  Custom usage:  - Implement a login mechanism. - Create a flask route with a post method handler. `@app.server.route('/logout', methods=['POST'])`   - The logout route should perform what's necessary for the user to logout.   - If you store the session in a cookie, clear the cookie:   `rep = flask.Response(); rep.set_cookie('session', '', expires=0)`  - Create a logout button component and assign it the logout_url `dcc.LogoutButton(logout_url='/logout')`  See https://dash.plot.ly/dash-core-components/logout_button for more documentation and examples.
}

\usage{
dccLogoutButton(dccLogoutButton(id=NULL, label=NULL, logout_url=NULL, style=NULL, method=NULL,
className=NULL, loading_state=NULL))
}

\arguments{
\item{id}{Character. Id of the button.}

\item{label}{Character. Text of the button}

\item{logout_url}{Character. Url to submit a post logout request.}

\item{style}{Named list. Style of the button}

\item{method}{Character. Http method to submit the logout form.}

\item{className}{Character. CSS class for the button.}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
