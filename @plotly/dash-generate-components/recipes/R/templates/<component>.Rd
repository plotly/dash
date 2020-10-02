${recipe.vars.rd_header}
\\name{${config.vars.prefix}${target.displayName}}

\\alias{${config.vars.prefix}${target.displayName}}

\\title{${target.displayName} component}

\\description{
${config.vars.pkg_help_description}
}

\\usage{
${config.vars.prefix}${target.displayName}(
${templates.class_parameter(js.core.filterProps(target.props))}
)
}

\\arguments{
${templates.class_property(js.core.filterProps(target.props))}
}

\\value{named list of JSON elements corresponding to React.js properties and their values}

\\examples{
${config.vars.examples[target.displayName].code}
}