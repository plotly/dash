% Auto-generated: do not edit by hand
\name{dccUpload}

\alias{dccUpload}

\title{Upload component}

\description{

}

\usage{
dccUpload(children=NULL, id=NULL, contents=NULL, filename=NULL, last_modified=NULL, accept=NULL, disabled=NULL, disable_click=NULL, max_size=NULL, min_size=NULL, multiple=NULL, className=NULL, className_active=NULL, className_reject=NULL, className_disabled=NULL, style=NULL, style_active=NULL, style_reject=NULL, style_disabled=NULL, loading_state=NULL, ...)
}

\arguments{
\item{children}{Contents of the upload component}

\item{id}{ID of the component. Used to identify component
in Dash callback functions.}

\item{contents}{The contents of the uploaded file as a binary string}

\item{filename}{The name of the file(s) that was(were) uploaded.
Note that this does not include the path of the file
(for security reasons).}

\item{last_modified}{The last modified date of the file that was uploaded in unix time
(seconds since 1970).}

\item{accept}{Allow specific types of files.
See https://github.com/okonet/attr-accept for more information.
Keep in mind that mime type determination is not reliable across
platforms. CSV files, for example, are reported as text/plain
under macOS but as application/vnd.ms-excel under Windows.
In some cases there might not be a mime type set at all.
See: https://github.com/react-dropzone/react-dropzone/issues/276}

\item{disabled}{Enable/disable the upload component entirely}

\item{disable_click}{Disallow clicking on the component to open the file dialog}

\item{max_size}{Maximum file size. If `-1`, then infinite}

\item{min_size}{Minimum file size}

\item{multiple}{Allow dropping multiple files}

\item{className}{HTML class name of the component}

\item{className_active}{HTML class name of the component while active}

\item{className_reject}{HTML class name of the component if rejected}

\item{className_disabled}{HTML class name of the component if disabled}

\item{style}{CSS styles to apply}

\item{style_active}{CSS styles to apply while active}

\item{style_reject}{CSS styles if rejected}

\item{style_disabled}{CSS styles if disabled}

\item{loading_state}{Object that holds the loading state object coming from dash-renderer}
}
