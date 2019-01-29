% Auto-generated: do not edit by hand
\name{coreLogoutButton}

\alias{coreLogoutButton}

\title{LogoutButton component}

\description{
Logout button to submit a form post request to the `logout_url` prop. Usage is intended for dash-deployment-server authentication.  DDS usage:  `dcc.LogoutButton(logout_url=os.getenv('DASH_LOGOUT_URL'))`  Custom usage:  - Implement a login mechanism. - Create a flask route with a post method handler. `@app.server.route('/logout', methods=['POST'])`   - The logout route should perform what's necessary for the user to logout.   - If you store the session in a cookie, clear the cookie:   `rep = flask.Response(); rep.set_cookie('session', '', expires=0)`  - Create a logout button component and assign it the logout_url `dcc.LogoutButton(logout_url='/logout')`  See https://dash.plot.ly/dash-core-components/logout_button for more documentation and examples.
}

\usage{
coreLogoutButton(id=NULL, label=NULL, logout_url=NULL, style=NULL, method=NULL, className=NULL, ...)
}

\arguments{
\item{id}{Id of the button.}

\item{label}{Text of the button}

\item{logout_url}{Url to submit a post logout request.}

\item{style}{Style of the button}

\item{method}{Http method to submit the logout form.}

\item{className}{CSS class for the button.}
}
