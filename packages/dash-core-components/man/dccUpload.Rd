% Auto-generated: do not edit by hand
\name{dccUpload}

\alias{dccUpload}

\title{Upload component}

\description{
Upload components allow your app to accept user-uploaded files via drag'n'drop
}

\usage{
dccUpload(dccUpload(children=NULL, id=NULL, contents=NULL, filename=NULL,
last_modified=NULL, accept=NULL, disabled=NULL, disable_click=NULL,
max_size=NULL, min_size=NULL, multiple=NULL, className=NULL,
className_active=NULL, className_reject=NULL, className_disabled=NULL,
style=NULL, style_active=NULL, style_reject=NULL, style_disabled=NULL,
loading_state=NULL))
}

\arguments{
\item{children}{A list of or a singular dash component, string or number | character. Contents of the upload component}

\item{id}{Character. The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.}

\item{contents}{Character | list of characters. The contents of the uploaded file as a binary string}

\item{filename}{Character | list of characters. The name of the file(s) that was(were) uploaded.
Note that this does not include the path of the file
(for security reasons).}

\item{last_modified}{Numeric | list of numerics. The last modified date of the file that was uploaded in unix time
(seconds since 1970).}

\item{accept}{Character. Allow specific types of files.
See https://github.com/okonet/attr-accept for more information.
Keep in mind that mime type determination is not reliable across
platforms. CSV files, for example, are reported as text/plain
under macOS but as application/vnd.ms-excel under Windows.
In some cases there might not be a mime type set at all.
See: https://github.com/react-dropzone/react-dropzone/issues/276}

\item{disabled}{Logical. Enable/disable the upload component entirely}

\item{disable_click}{Logical. Disallow clicking on the component to open the file dialog}

\item{max_size}{Numeric. Maximum file size. If `-1`, then infinite}

\item{min_size}{Numeric. Minimum file size}

\item{multiple}{Logical. Allow dropping multiple files}

\item{className}{Character. HTML class name of the component}

\item{className_active}{Character. HTML class name of the component while active}

\item{className_reject}{Character. HTML class name of the component if rejected}

\item{className_disabled}{Character. HTML class name of the component if disabled}

\item{style}{Named list. CSS styles to apply}

\item{style_active}{Named list. CSS styles to apply while active}

\item{style_reject}{Named list. CSS styles if rejected}

\item{style_disabled}{Named list. CSS styles if disabled}

\item{loading_state}{Lists containing elements 'is_loading', 'prop_name', 'component_name'.
those elements have the following types:
  - is_loading (logical; optional): determines if the component is loading or not
  - prop_name (character; optional): holds which property is loading
  - component_name (character; optional): holds the name of the component that is loading. Object that holds the loading state object coming from dash-renderer}
}
