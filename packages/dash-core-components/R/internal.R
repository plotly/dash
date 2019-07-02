.dashCoreComponents_js_metadata <- function() {
deps_metadata <- list(`dash_core_components` = structure(list(name = "dash_core_components",
version = "0", src = list(href = NULL,
file = "deps"), meta = NULL,
script = 'plotly-1.48.3.min.js',
stylesheet = NULL, head = NULL, attachment = NULL, package = "dashCoreComponents",
all_files = FALSE), class = "html_dependency"),
`dash_core_components` = structure(list(name = "dash_core_components",
version = "1.0.0", src = list(href = NULL,
file = "deps"), meta = NULL,
script = 'highlight.pack.js',
stylesheet = NULL, head = NULL, attachment = NULL, package = "dashCoreComponents",
all_files = FALSE), class = "html_dependency"),
`dash_core_components` = structure(list(name = "dash_core_components",
version = "1.0.0", src = list(href = NULL,
file = "deps"), meta = NULL,
script = 'dash_core_components.min.js',
stylesheet = NULL, head = NULL, attachment = NULL, package = "dashCoreComponents",
all_files = FALSE), class = "html_dependency"),
`dash_core_components` = structure(list(name = "dash_core_components",
version = "1.0.0", src = list(href = NULL,
file = "deps"), meta = NULL,
script = 'dash_core_components.min.js.map',
stylesheet = NULL, head = NULL, attachment = NULL, package = "dashCoreComponents",
all_files = FALSE), class = "html_dependency"),
`dash_core_components` = structure(list(name = "dash_core_components",
version = "1.0.0", src = list(href = NULL,
file = "deps"), meta = NULL,
script = NULL,
stylesheet = 'highlight.css', head = NULL, attachment = NULL, package = "dashCoreComponents",
all_files = FALSE), class = "html_dependency"))
return(deps_metadata)
}

dash_assert_valid_wildcards <- function (attrib = list("data", "aria"), ...)
{
    args <- list(...)
    validation_results <- lapply(names(args), function(x) {
        grepl(paste0("^", attrib, "-[a-zA-Z0-9]{1,}$", collapse = "|"),
            x)
    })
    if (FALSE %in% validation_results) {
        stop(sprintf("The following wildcards are not currently valid in Dash: '%s'",
            paste(names(args)[grepl(FALSE, unlist(validation_results))],
                collapse = ", ")), call. = FALSE)
    }
    else {
        return(args)
    }
}
