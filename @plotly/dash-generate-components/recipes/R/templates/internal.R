.${recipe.vars.r_name}_js_metadata <- function() {
deps_metadata <- list(\`${recipe.vars.js_name}\` = ${templates.dist(config.dist)}
))
return(deps_metadata)
}