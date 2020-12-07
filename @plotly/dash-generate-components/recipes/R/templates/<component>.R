${recipe.vars.r_header}

${config.vars.prefix + target.displayName} <- function(${templates.ctor_argument(js.core.filterProps(target.props))}) {

  props <- list(${templates.prop_assignment(js.core.filterProps(target.props))})
  if (length(props) > 0) {
      props <- props[!vapply(props, is.null, logical(1))]
  }
  component <- list(
    props = props,
    type = '${target.displayName}',
    namespace = '${recipe.vars.js_name}',
    propNames = c(${templates.prop_name(js.core.filterProps(target.props))}),
    namespace = '${recipe.vars.r_name}',
    )

  structure(component, class = c('dash_component', 'list')
}