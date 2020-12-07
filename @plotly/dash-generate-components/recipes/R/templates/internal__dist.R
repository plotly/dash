structure(list(name = "${recipe.vars.snake_name}",
version = "${recipe.vars.version}", src = list(href = NULL,
file = "deps"), meta = NULL,
script = "${target.target}",
stylesheet = NULL, head = NULL, attachment = NULL, package = "${recipe.vars.r_name}",
all_files = FALSE, async = ${js.toAsync(target.async)}), class = "html_dependency")