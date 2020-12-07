${recipe.vars.rd_header}
\\docType{package}
\\name{${recipe.vars.r_name}-package}
\\alias{${recipe.vars.r_name}}
\\title{${config.vars.pkg_help_title}}
\\description{
${config.vars.pkg_help_description.split('\n').join(' ')}
}
\\author{
\\strong{Maintainer}: ${recipe.vars.maintainer}
}