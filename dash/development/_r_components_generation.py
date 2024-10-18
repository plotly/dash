# pylint: disable=consider-using-f-string
import os
import sys
import shutil
import importlib
import textwrap
import re
import warnings

from ._all_keywords import r_keywords
from ._py_components_generation import reorder_props


# Declaring longer string templates as globals to improve
# readability, make method logic clearer to anyone inspecting
# code below
r_component_string = """#' @export
{funcname} <- function({default_argtext}{wildcards}) {{
    {wildcard_declaration}
    props <- list({default_paramtext}{wildcards})
    if (length(props) > 0) {{
        props <- props[!vapply(props, is.null, logical(1))]
    }}
    component <- list(
        props = props,
        type = '{name}',
        namespace = '{project_shortname}',
        propNames = c({prop_names}{wildcard_names}),
        package = '{package_name}'
        )

    structure(component, class = c('dash_component', 'list'))
}}
"""  # noqa:E501

# the following strings represent all the elements in an object
# of the html_dependency class, which will be propagated by
# iterating over _js_dist in __init__.py
frame_open_template = """.{rpkgname}_js_metadata <- function() {{
deps_metadata <- list("""

frame_element_template = """`{dep_name}` = structure(list(name = "{dep_name}",
version = "{project_ver}", src = list(href = NULL,
file = "deps"), meta = NULL,
script = {script_name},
stylesheet = {css_name}, head = NULL, attachment = NULL, package = "{rpkgname}",
all_files = FALSE{async_or_dynamic}), class = "html_dependency")"""  # noqa:E501

frame_body_template = """`{project_shortname}` = structure(list(name = "{project_shortname}",
version = "{project_ver}", src = list(href = NULL,
file = "deps"), meta = NULL,
script = {script_name},
stylesheet = {css_name}, head = NULL, attachment = NULL, package = "{rpkgname}",
all_files = FALSE{async_or_dynamic}), class = "html_dependency")"""  # noqa:E501

frame_close_template = """)
return(deps_metadata)
}
"""

help_string = """% Auto-generated: do not edit by hand
\\name{{{funcname}}}

\\alias{{{funcname}}}

\\title{{{name} component}}

\\description{{
{description}
}}

\\usage{{
{funcname}({default_argtext})
}}

\\arguments{{
{item_text}
}}

\\value{{{value_text}}}

"""

description_template = """Package: {package_name}
Title: {package_title}
Version: {package_version}
Description: {package_description}
Depends: R (>= 3.0.2){package_depends}
Imports: {package_imports}
Suggests: {package_suggests}{package_rauthors}
License: {package_license}{package_copyright}
URL: {package_url}
BugReports: {package_issues}
Encoding: UTF-8
LazyData: true{vignette_builder}
KeepSource: true
"""

rbuild_ignore_string = r"""# ignore JS config files/folders
node_modules/
coverage/
src/
lib/
.babelrc
.builderrc
.eslintrc
.npmignore
.editorconfig
.eslintignore
.prettierrc
.circleci
.github

# demo folder has special meaning in R
# this should hopefully make it still
# allow for the possibility to make R demos
demo/.*\.js
demo/.*\.html
demo/.*\.css

# ignore Python files/folders
setup.py
usage.py
setup.py
requirements.txt
MANIFEST.in
CHANGELOG.md
test/
# CRAN has weird LICENSE requirements
LICENSE.txt
^.*\.Rproj$
^\.Rproj\.user$
"""

pkghelp_stub = """% Auto-generated: do not edit by hand
\\docType{{package}}
\\name{{{package_name}-package}}
\\alias{{{package_name}}}
\\title{{{pkg_help_title}}}
\\description{{
{pkg_help_description}
}}
\\author{{
\\strong{{Maintainer}}: {maintainer}
}}
"""

wildcard_helper = """
dash_assert_valid_wildcards <- function (attrib = list("data", "aria"), ...)
{
    args <- list(...)
    validation_results <- lapply(names(args), function(x) {
        grepl(paste0("^(", paste0(attrib, collapse="|"), ")-[a-zA-Z0-9_-]+$"),
            x)
    })
    if (FALSE %in% validation_results) {
        stop(sprintf("The following props are not valid in this component: '%s'",
            paste(names(args)[grepl(FALSE, unlist(validation_results))],
                collapse = ", ")), call. = FALSE)
    }
    else {
        return(args)
    }
}
"""  # noqa:E501

wildcard_template = """
    wildcard_names = names(dash_assert_valid_wildcards(attrib = list({}), ...))
"""

wildcard_help_template = """


\\item{{...}}{{wildcards allowed have the form: `{}`}}
"""


# pylint: disable=R0914
def generate_class_string(name, props, project_shortname, prefix):
    # Here we convert from snake case to camel case
    package_name = snake_case_to_camel_case(project_shortname)

    # Ensure props are ordered with children first
    props = reorder_props(props=props)

    prop_keys = list(props.keys())

    wildcards = ""
    wildcard_declaration = ""
    wildcard_names = ""
    default_paramtext = ""
    default_argtext = ""
    accepted_wildcards = ""

    if any(key.endswith("-*") for key in prop_keys):
        accepted_wildcards = get_wildcards_r(prop_keys)
        wildcards = ", ..."
        wildcard_declaration = wildcard_template.format(
            accepted_wildcards.replace("-*", "")
        )
        wildcard_names = ", wildcard_names"

    # Produce a string with all property names other than WCs
    prop_names = ", ".join(
        "'{}'".format(p) for p in prop_keys if "*" not in p and p not in ["setProps"]
    )

    # Filter props to remove those we don't want to expose
    for item in prop_keys[:]:
        if item.endswith("-*") or item == "setProps":
            prop_keys.remove(item)
        elif item in r_keywords:
            prop_keys.remove(item)
            warnings.warn(
                (
                    'WARNING: prop "{}" in component "{}" is an R keyword'
                    " - REMOVED FROM THE R COMPONENT"
                ).format(item, name)
            )

    default_argtext += ", ".join("{}=NULL".format(p) for p in prop_keys)

    # pylint: disable=C0301
    default_paramtext += ", ".join(
        "{0}={0}".format(p) if p != "children" else "{}=children".format(p)
        for p in prop_keys
    )

    return r_component_string.format(
        funcname=format_fn_name(prefix, name),
        name=name,
        default_argtext=default_argtext,
        wildcards=wildcards,
        wildcard_declaration=wildcard_declaration,
        default_paramtext=default_paramtext,
        project_shortname=project_shortname,
        prop_names=prop_names,
        wildcard_names=wildcard_names,
        package_name=package_name,
    )


# pylint: disable=R0914
def generate_js_metadata(pkg_data, project_shortname):
    """Dynamically generate R function to supply JavaScript and CSS dependency
    information required by the dash package for R.

    Parameters
    ----------
    project_shortname = component library name, in snake case

    Returns
    -------
    function_string = complete R function code to provide component features
    """
    # make sure the module we're building is available to Python,
    # even if it hasn't been installed yet
    sys.path.insert(0, os.getcwd())
    mod = importlib.import_module(project_shortname)

    alldist = getattr(mod, "_js_dist", []) + getattr(mod, "_css_dist", [])

    project_ver = pkg_data.get("version")

    rpkgname = snake_case_to_camel_case(project_shortname)

    # since _js_dist may suggest more than one dependency, need
    # a way to iterate over all dependencies for a given set.
    # here we define an opening, element, and closing string --
    # if the total number of dependencies > 1, we can concatenate
    # them and write a list object in R with multiple elements
    function_frame_open = frame_open_template.format(rpkgname=rpkgname)

    function_frame = []
    function_frame_body = []

    # pylint: disable=consider-using-enumerate
    if len(alldist) > 1:
        for dep in range(len(alldist)):
            curr_dep = alldist[dep]
            rpp = curr_dep.get("relative_package_path", "")
            if not rpp:
                continue

            async_or_dynamic = get_async_type(curr_dep)

            if "dash_" in rpp:
                dep_name = rpp.split(".")[0]
            else:
                dep_name = "{}".format(project_shortname)

            if "css" in rpp:
                css_name = "'{}'".format(rpp)
                script_name = "NULL"
            else:
                script_name = "'{}'".format(rpp)
                css_name = "NULL"

            function_frame += [
                frame_element_template.format(
                    dep_name=dep_name,
                    project_ver=project_ver,
                    rpkgname=rpkgname,
                    project_shortname=project_shortname,
                    script_name=script_name,
                    css_name=css_name,
                    async_or_dynamic=async_or_dynamic,
                )
            ]
            function_frame_body = ",\n".join(function_frame)
    elif len(alldist) == 1:
        dep = alldist[0]
        rpp = dep["relative_package_path"]

        async_or_dynamic = get_async_type(dep)

        if "css" in rpp:
            css_name = "'{}'".format(rpp)
            script_name = "NULL"
        else:
            script_name = "'{}'".format(rpp)
            css_name = "NULL"

        function_frame_body = frame_body_template.format(
            project_shortname=project_shortname,
            project_ver=project_ver,
            rpkgname=rpkgname,
            script_name=script_name,
            css_name=css_name,
            async_or_dynamic=async_or_dynamic,
        )

    function_string = "".join(
        [function_frame_open, function_frame_body, frame_close_template]
    )

    return function_string


# determine whether dependency uses async or dynamic flag
# then return the properly formatted string if so, i.e.
# " async = TRUE,". a dependency can have async or
# dynamic elements, neither of these, but never both.
def get_async_type(dep):
    async_or_dynamic = ""
    for key in dep.keys():
        if key in ["async", "dynamic"]:
            keyval = dep[key]
            if not isinstance(keyval, bool):
                keyval = "'{}'".format(keyval.lower())
            else:
                keyval = str(keyval).upper()
            async_or_dynamic = ", {} = {}".format(key, keyval)
    return async_or_dynamic


# This method wraps code within arbitrary LaTeX-like tags, which are used
# by R's internal help parser for constructing man pages
def wrap(tag, code):
    if tag == "":
        return code
    return "\\{}{{\n{}}}".format(tag, code)


def write_help_file(name, props, description, prefix, rpkg_data):
    """Write R documentation file (.Rd) given component name and properties.

    Parameters
    ----------
    name = the name of the Dash component for which a help file is generated
    props = the properties of the component
    description = the component's description, inserted into help file header
    prefix = the DashR library prefix (optional, can be a blank string)
    rpkg_data = package metadata (optional)

    Returns
    -------
    writes an R help file to the man directory for the generated R package
    """
    funcname = format_fn_name(prefix, name)
    file_name = funcname + ".Rd"

    wildcards = ""
    default_argtext = ""
    item_text = ""
    accepted_wildcards = ""

    # the return value of all Dash components should be the same,
    # in an abstract sense -- they produce a list
    value_text = "named list of JSON elements corresponding to React.js properties and their values"  # noqa:E501

    prop_keys = list(props.keys())

    if any(key.endswith("-*") for key in prop_keys):
        accepted_wildcards = get_wildcards_r(prop_keys)
        wildcards = ", ..."

    # Filter props to remove those we don't want to expose
    for item in prop_keys[:]:
        if item.endswith("-*") or item in r_keywords or item == "setProps":
            prop_keys.remove(item)

    default_argtext += ", ".join("{}=NULL".format(p) for p in prop_keys)

    item_text += "\n\n".join(
        "\\item{{{}}}{{{}{}}}".format(
            p, print_r_type(props[p]["type"]), props[p]["description"]
        )
        for p in prop_keys
    )

    # auto-replace any unescaped backslashes for compatibility with R docs
    description = re.sub(r"(?<!\\)%", "\\%", description)
    item_text = re.sub(r"(?<!\\)%", "\\%", item_text)

    # scrub examples which begin with **Example Usage**, as these should be
    # provided as R code within dash-info.yaml
    if "**Example Usage**" in description:
        description = description.split("**Example Usage**")[0].rstrip()

    if wildcards == ", ...":
        default_argtext += wildcards
        item_text += wildcard_help_template.format(accepted_wildcards)

    # in R, the online help viewer does not properly wrap lines for
    # the usage string -- we will hard wrap at 60 characters using
    # textwrap.fill, starting from the beginning of the usage string

    file_path = os.path.join("man", file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(
            help_string.format(
                funcname=funcname,
                name=name,
                default_argtext=textwrap.fill(
                    default_argtext, width=60, break_long_words=False
                ),
                item_text=item_text,
                value_text=value_text,
                description=description.replace("\n", " "),
            )
        )
    if rpkg_data is not None and "r_examples" in rpkg_data:
        ex = rpkg_data.get("r_examples")
        the_ex = ([e for e in ex if e.get("name") == funcname] or [None])[0]
        result = ""
        if the_ex and "code" in the_ex.keys():
            result += wrap(
                "examples",
                wrap("dontrun" if the_ex.get("dontrun") else "", the_ex["code"]),
            )
            with open(file_path, "a+", encoding="utf-8") as fa:
                fa.write(result + "\n")


# pylint: disable=too-many-arguments
def write_class_file(
    name,
    props,
    description,
    project_shortname,
    prefix=None,
    rpkg_data=None,
):
    props = reorder_props(props=props)

    # generate the R help pages for each of the Dash components that we
    # are transpiling -- this is done to avoid using Roxygen2 syntax,
    # we may eventually be able to generate similar documentation using
    # doxygen and an R plugin, but for now we'll just do it on our own
    # from within Python
    write_help_file(name, props, description, prefix, rpkg_data)

    import_string = "# AUTO GENERATED FILE - DO NOT EDIT\n\n"
    class_string = generate_class_string(name, props, project_shortname, prefix)

    file_name = format_fn_name(prefix, name) + ".R"

    file_path = os.path.join("R", file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(import_string)
        f.write(class_string)

    print("Generated {}".format(file_name))


def write_js_metadata(pkg_data, project_shortname, has_wildcards):
    """Write an internal (not exported) R function to return all JS
    dependencies as required by dash.

    Parameters
    ----------
    project_shortname = hyphenated string, e.g. dash-html-components

    Returns
    -------
    """
    function_string = generate_js_metadata(
        pkg_data=pkg_data, project_shortname=project_shortname
    )
    file_name = "internal.R"

    # the R source directory for the package won't exist on first call
    # create the R directory if it is missing
    if not os.path.exists("R"):
        os.makedirs("R")

    file_path = os.path.join("R", file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(function_string)
        if has_wildcards:
            f.write(wildcard_helper)

    # now copy over all JS dependencies from the (Python) components dir
    # the inst/lib directory for the package won't exist on first call
    # create this directory if it is missing
    if os.path.exists("inst/deps"):
        shutil.rmtree("inst/deps")

    os.makedirs("inst/deps")

    for rel_dirname, _, filenames in os.walk(project_shortname):
        for filename in filenames:
            extension = os.path.splitext(filename)[1]

            if extension in [".py", ".pyc", ".json"]:
                continue

            target_dirname = os.path.join(
                os.path.join(
                    "inst/deps/", os.path.relpath(rel_dirname, project_shortname)
                )
            )

            if not os.path.exists(target_dirname):
                os.makedirs(target_dirname)

            shutil.copy(os.path.join(rel_dirname, filename), target_dirname)


# pylint: disable=R0914, R0913, R0912, R0915
def generate_rpkg(
    pkg_data,
    rpkg_data,
    project_shortname,
    export_string,
    package_depends,
    package_imports,
    package_suggests,
    has_wildcards,
):
    """Generate documents for R package creation.

    Parameters
    ----------
    pkg_data
    rpkg_data
    project_shortname
    export_string
    package_depends
    package_imports
    package_suggests
    has_wildcards

    Returns
    -------
    """
    # Leverage package.json to import specifics which are also applicable
    # to R package that we're generating here, use .get in case the key
    # does not exist in package.json

    package_name = snake_case_to_camel_case(project_shortname)
    package_copyright = ""
    package_rauthors = ""
    lib_name = pkg_data.get("name")

    if rpkg_data is not None:
        if rpkg_data.get("pkg_help_title"):
            package_title = rpkg_data.get(
                "pkg_help_title", pkg_data.get("description", "")
            )
        if rpkg_data.get("pkg_help_description"):
            package_description = rpkg_data.get(
                "pkg_help_description", pkg_data.get("description", "")
            )
        if rpkg_data.get("pkg_copyright"):
            package_copyright = "\nCopyright: {}".format(
                rpkg_data.get("pkg_copyright", "")
            )
    else:
        # fall back to using description in package.json, if present
        package_title = pkg_data.get("description", "")
        package_description = pkg_data.get("description", "")

    package_version = pkg_data.get("version", "0.0.1")

    # remove leading and trailing commas, add space after comma if missing
    if package_depends:
        package_depends = ", " + package_depends.strip(",").lstrip()
        package_depends = re.sub(r"(,(?![ ]))", ", ", package_depends)

    if package_imports:
        package_imports = package_imports.strip(",").lstrip()
        package_imports = re.sub(r"(,(?![ ]))", ", ", package_imports)

    if package_suggests:
        package_suggests = package_suggests.strip(",").lstrip()
        package_suggests = re.sub(r"(,(?![ ]))", ", ", package_suggests)

    if "bugs" in pkg_data:
        package_issues = pkg_data["bugs"].get("url", "")
    else:
        package_issues = ""
        print(
            "Warning: a URL for bug reports was "
            "not provided. Empty string inserted.",
            file=sys.stderr,
        )

    if "homepage" in pkg_data:
        package_url = pkg_data.get("homepage", "")
    else:
        package_url = ""
        print(
            "Warning: a homepage URL was not provided. Empty string inserted.",
            file=sys.stderr,
        )

    package_author = pkg_data.get("author")

    package_author_name = package_author.split(" <")[0]
    package_author_email = package_author.split(" <")[1][:-1]

    package_author_fn = package_author_name.split(" ")[0]
    package_author_ln = package_author_name.rsplit(" ", 2)[-1]

    maintainer = pkg_data.get("maintainer", pkg_data.get("author"))

    if "<" not in package_author:
        print(
            "Error, aborting R package generation: "
            "R packages require a properly formatted author field "
            "or installation will fail. Please include an email "
            "address enclosed within < > brackets in package.json. ",
            file=sys.stderr,
        )
        sys.exit(1)

    if rpkg_data is not None:
        if rpkg_data.get("pkg_authors"):
            package_rauthors = "\nAuthors@R: {}".format(
                rpkg_data.get("pkg_authors", "")
            )
        else:
            package_rauthors = '\nAuthors@R: person("{}", "{}", role = c("aut", "cre"), email = "{}")'.format(
                package_author_fn, package_author_ln, package_author_email
            )

    if not (os.path.isfile("LICENSE") or os.path.isfile("LICENSE.txt")):
        package_license = pkg_data.get("license", "")
    else:
        package_license = pkg_data.get("license", "") + " + file LICENSE"
        # R requires that the LICENSE.txt file be named LICENSE
        if not os.path.isfile("LICENSE"):
            os.symlink("LICENSE.txt", "LICENSE")

    import_string = "# AUTO GENERATED FILE - DO NOT EDIT\n\n"
    packages_string = ""

    rpackage_list = package_depends.split(", ") + package_imports.split(", ")
    rpackage_list = filter(bool, rpackage_list)

    if rpackage_list:
        for rpackage in rpackage_list:
            packages_string += "\nimport({})\n".format(rpackage)

    if os.path.exists("vignettes"):
        vignette_builder = "\nVignetteBuilder: knitr"
        if "knitr" not in package_suggests and "rmarkdown" not in package_suggests:
            package_suggests += ", knitr, rmarkdown"
            package_suggests = package_suggests.lstrip(", ")
    else:
        vignette_builder = ""

    pkghelp_stub_path = os.path.join("man", package_name + "-package.Rd")

    # generate the internal (not exported to the user) functions which
    # supply the JavaScript dependencies to the dash package.
    # this avoids having to generate an RData file from within Python.
    write_js_metadata(pkg_data, project_shortname, has_wildcards)

    with open("NAMESPACE", "w+", encoding="utf-8") as f:
        f.write(import_string)
        f.write(export_string)
        f.write(packages_string)

    with open(".Rbuildignore", "w+", encoding="utf-8") as f2:
        f2.write(rbuild_ignore_string)

    description_string = description_template.format(
        package_name=package_name,
        package_title=package_title,
        package_description=package_description,
        package_version=package_version,
        package_rauthors=package_rauthors,
        package_depends=package_depends,
        package_imports=package_imports,
        package_suggests=package_suggests,
        package_license=package_license,
        package_copyright=package_copyright,
        package_url=package_url,
        package_issues=package_issues,
        vignette_builder=vignette_builder,
    )

    with open("DESCRIPTION", "w+", encoding="utf-8") as f3:
        f3.write(description_string)

    if rpkg_data is not None:
        if rpkg_data.get("pkg_help_description"):
            pkghelp = pkghelp_stub.format(
                package_name=package_name,
                pkg_help_title=rpkg_data.get("pkg_help_title"),
                pkg_help_description=rpkg_data.get("pkg_help_description"),
                lib_name=lib_name,
                maintainer=maintainer,
            )
            with open(pkghelp_stub_path, "w", encoding="utf-8") as f4:
                f4.write(pkghelp)


# This converts a string from snake case to camel case
# Not required for R package name to be in camel case,
# but probably more conventional this way
def snake_case_to_camel_case(namestring):
    s = namestring.split("_")
    return s[0] + "".join(w.capitalize() for w in s[1:])


# this logic will permit passing blank R prefixes to
# dash-generate-components, while also enforcing
# camelCase for the resulting functions; if a prefix
# is supplied, leave it as-is
def format_fn_name(prefix, name):
    if prefix:
        return prefix + snake_case_to_camel_case(name)
    return snake_case_to_camel_case(name[0].lower() + name[1:])


# pylint: disable=unused-argument
def generate_exports(
    project_shortname,
    components,
    metadata,
    pkg_data,
    rpkg_data,
    prefix,
    package_depends,
    package_imports,
    package_suggests,
    **kwargs
):
    export_string = make_namespace_exports(components, prefix)

    # Look for wildcards in the metadata
    has_wildcards = False
    for component_data in metadata.values():
        if any(key.endswith("-*") for key in component_data["props"]):
            has_wildcards = True
            break

    # now, bundle up the package information and create all the requisite
    # elements of an R package, so that the end result is installable either
    # locally or directly from GitHub
    generate_rpkg(
        pkg_data,
        rpkg_data,
        project_shortname,
        export_string,
        package_depends,
        package_imports,
        package_suggests,
        has_wildcards,
    )


def make_namespace_exports(components, prefix):
    export_string = ""
    for component in components:
        if (
            not component.endswith("-*")
            and str(component) not in r_keywords
            and str(component) not in ["setProps", "children"]
        ):
            export_string += "export({}{})\n".format(prefix, component)

    # the following lines enable rudimentary support for bundling in
    # R functions that are not automatically generated by the transpiler
    # such that functions contained in the R subdirectory are exported,
    # so long as they are not in utils.R.
    rfilelist = []
    omitlist = ["utils.R", "internal.R"] + [
        "{}{}.R".format(prefix, component) for component in components
    ]
    fnlist = []

    for script in os.listdir("R"):
        if script.endswith(".R") and script not in omitlist:
            rfilelist += [os.path.join("R", script)]

    for rfile in rfilelist:
        with open(rfile, "r", encoding="utf-8") as script:
            s = script.read()

            # remove comments
            s = re.sub("#.*$", "", s, flags=re.M)

            # put the whole file on one line
            s = s.replace("\n", " ").replace("\r", " ")

            # empty out strings, in case of unmatched block terminators
            s = re.sub(r"'([^'\\]|\\'|\\[^'])*'", "''", s)
            s = re.sub(r'"([^"\\]|\\"|\\[^"])*"', '""', s)

            # empty out block terminators () and {}
            # so we don't catch nested functions, or functions as arguments
            # repeat until it stops changing, in case of multiply nested blocks
            prev_len = len(s) + 1
            while len(s) < prev_len:
                prev_len = len(s)
                s = re.sub(r"\(([^()]|\(\))*\)", "()", s)
                s = re.sub(r"\{([^{}]|\{\})*\}", "{}", s)

            # now, in whatever is left, look for functions
            matches = re.findall(
                # in R, either = or <- may be used to create and assign objects
                r"([^A-Za-z0-9._]|^)([A-Za-z0-9._]+)\s*(=|<-)\s*function",
                s,
            )
            for match in matches:
                fn = match[1]
                # Allow users to mark functions as private by prefixing with .
                if fn[0] != "." and fn not in fnlist:
                    fnlist.append(fn)

    export_string += "\n".join("export({})".format(function) for function in fnlist)
    return export_string


def get_r_prop_types(type_object):
    """Mapping from the PropTypes js type object to the R type."""

    def shape_or_exact():
        return "lists containing elements {}.\n{}".format(
            ", ".join("'{}'".format(t) for t in type_object["value"]),
            "Those elements have the following types:\n{}".format(
                "\n".join(
                    create_prop_docstring_r(
                        prop_name=prop_name,
                        type_object=prop,
                        required=prop["required"],
                        description=prop.get("description", ""),
                        indent_num=1,
                    )
                    for prop_name, prop in type_object["value"].items()
                )
            ),
        )

    return dict(
        array=lambda: "unnamed list",
        bool=lambda: "logical",
        number=lambda: "numeric",
        string=lambda: "character",
        object=lambda: "named list",
        any=lambda: "logical | numeric | character | named list | unnamed list",
        element=lambda: "dash component",
        node=lambda: "a list of or a singular dash component, string or number",
        # React's PropTypes.oneOf
        enum=lambda: "a value equal to: {}".format(
            ", ".join("{}".format(str(t["value"])) for t in type_object["value"])
        ),
        # React's PropTypes.oneOfType
        union=lambda: "{}".format(
            " | ".join(
                "{}".format(get_r_type(subType))
                for subType in type_object["value"]
                if get_r_type(subType) != ""
            )
        ),
        # React's PropTypes.arrayOf
        arrayOf=lambda: (
            "list"
            + (
                " of {}s".format(get_r_type(type_object["value"]))
                if get_r_type(type_object["value"]) != ""
                else ""
            )
        ),
        # React's PropTypes.objectOf
        objectOf=lambda: "list with named elements and values of type {}".format(
            get_r_type(type_object["value"])
        ),
        # React's PropTypes.shape
        shape=shape_or_exact,
        # React's PropTypes.exact
        exact=shape_or_exact,
    )


def get_r_type(type_object, is_flow_type=False, indent_num=0):
    """
    Convert JS types to R types for the component definition
    Parameters
    ----------
    type_object: dict
        react-docgen-generated prop type dictionary
    is_flow_type: bool
    indent_num: int
        Number of indents to use for the docstring for the prop
    Returns
    -------
    str
        Python type string
    """
    js_type_name = type_object["name"]
    js_to_r_types = get_r_prop_types(type_object=type_object)
    if (
        "computed" in type_object
        and type_object["computed"]
        or type_object.get("type", "") == "function"
    ):
        return ""
    if js_type_name in js_to_r_types:
        prop_type = js_to_r_types[js_type_name]()
        return prop_type
    return ""


def print_r_type(typedata):
    typestring = get_r_type(typedata).capitalize()
    if typestring:
        typestring += ". "
    return typestring


# pylint: disable=too-many-arguments
def create_prop_docstring_r(
    prop_name, type_object, required, description, indent_num, is_flow_type=False
):
    """
    Create the Dash component prop docstring
    Parameters
    ----------
    prop_name: str
        Name of the Dash component prop
    type_object: dict
        react-docgen-generated prop type dictionary
    required: bool
        Component is required?
    description: str
        Dash component description
    indent_num: int
        Number of indents to use for the context block
        (creates 2 spaces for every indent)
    is_flow_type: bool
        Does the prop use Flow types? Otherwise, uses PropTypes
    Returns
    -------
    str
        Dash component prop docstring
    """
    r_type_name = get_r_type(
        type_object=type_object, is_flow_type=is_flow_type, indent_num=indent_num + 1
    )

    indent_spacing = "  " * indent_num
    if "\n" in r_type_name:
        return (
            "{indent_spacing}- {name} ({is_required}): {description}. "
            "{name} has the following type: {type}".format(
                indent_spacing=indent_spacing,
                name=prop_name,
                type=r_type_name,
                description=description,
                is_required="required" if required else "optional",
            )
        )
    return "{indent_spacing}- {name} ({type}{is_required}){description}".format(
        indent_spacing=indent_spacing,
        name=prop_name,
        type="{}; ".format(r_type_name) if r_type_name else "",
        description=(": {}".format(description) if description != "" else ""),
        is_required="required" if required else "optional",
    )


def get_wildcards_r(prop_keys):
    wildcards = ""
    wildcards += ", ".join("'{}'".format(p) for p in prop_keys if p.endswith("-*"))

    if wildcards == "":
        wildcards = "NULL"
    return wildcards
