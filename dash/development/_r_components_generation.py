from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import shutil
import glob
import importlib
import textwrap
import re

from ._all_keywords import r_keywords
from ._py_components_generation import reorder_props


# Declaring longer string templates as globals to improve
# readability, make method logic clearer to anyone inspecting
# code below
r_component_string = """{funcname} <- function({default_argtext}{wildcards}) {{
    {wildcard_declaration}
    component <- list(
        props = list({default_paramtext}{wildcards}),
        type = '{name}',
        namespace = '{project_shortname}',
        propNames = c({prop_names}{wildcard_names}),
        package = '{package_name}'
        )

    component$props <- filter_null(component$props)

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
all_files = FALSE), class = "html_dependency")"""   # noqa:E501

frame_body_template = """`{project_shortname}` = structure(list(name = "{project_shortname}",
version = "{project_ver}", src = list(href = NULL,
file = "deps"), meta = NULL,
script = {script_name},
stylesheet = {css_name}, head = NULL, attachment = NULL, package = "{rpkgname}",
all_files = FALSE), class = "html_dependency")"""  # noqa:E501

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
"""

description_template = """Package: {package_name}
Title: {package_description}
Version: {package_version}
Authors @R: as.person(c({package_author}))
Description: {package_description}
Depends: R (>= 3.0.2){package_depends}
Imports: dash{package_imports}
Suggests: {package_suggests}
License: {package_license}
URL: {package_url}
BugReports: {package_issues}
Encoding: UTF-8
LazyData: true
Author: {package_author_no_email}
Maintainer: {package_author}
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

# demo folder has special meaning in R
# this should hopefully make it still
# allow for the possibility to make R demos
demo/.*\.js
demo/.*\.html
demo/.*\.css

# ignore python files/folders
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
\\title{{{pkg_help_header}}}
\\description{{
{pkg_help_desc}
}}
\\seealso{{
Useful links:
\\itemize{{
  \\item \\url{{https://github.com/plotly/{lib_name}}}
  \\item Report bugs at \\url{{https://github.com/plotly/{lib_name}/issues}}
}}
}}
\\author{{
\\strong{{Maintainer}}: {package_author}
}}
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

    if any("-*" in key for key in prop_keys):
        wildcards = ", ..."
        wildcard_declaration = (
            "\n    wildcard_names = names(assert_valid_wildcards(...))\n"
        )
        wildcard_names = ", wildcard_names"

    default_paramtext = ""
    default_argtext = ""
    default_wildcards = ""

    # Produce a string with all property names other than WCs
    prop_names = ", ".join(
        "'{}'".format(p)
        for p in prop_keys
        if "*" not in p and p not in ["setProps"]
    )

    # in R, we set parameters with no defaults to NULL
    # Here we'll do that if no default value exists
    default_wildcards += ", ".join("'{}'".format(p)
                                   for p in prop_keys if "*" in p)

    if default_wildcards == "":
        default_wildcards = "NULL"
    else:
        default_wildcards = "c({})".format(default_wildcards)

    # Filter props to remove those we don't want to expose
    for item in prop_keys[:]:
        if item.endswith("-*") or item in r_keywords or item == "setProps":
            prop_keys.remove(item)

    default_argtext += ", ".join("{}=NULL".format(p) for p in prop_keys)

    # pylint: disable=C0301
    default_paramtext += ", ".join(
        "{0}={0}".format(p) if p != "children" else "{}=children".format(p)
        for p in prop_keys
    )

    return r_component_string.format(funcname=format_fn_name(prefix, name),
                                     name=name,
                                     default_argtext=default_argtext,
                                     wildcards=wildcards,
                                     wildcard_declaration=wildcard_declaration,
                                     default_paramtext=default_paramtext,
                                     project_shortname=project_shortname,
                                     prop_names=prop_names,
                                     wildcard_names=wildcard_names,
                                     package_name=package_name)


# pylint: disable=R0914
def generate_js_metadata(pkg_data, project_shortname):
    """
    Dynamically generate R function to supply JavaScript
    and CSS dependency information required by the dash
    package for R.

    Parameters
    ----------
    project_shortname = component library name, in snake case

    Returns
    -------
    function_string = complete R function code to provide component features
    """
    importlib.import_module(project_shortname)

    # import component library module into sys
    mod = sys.modules[project_shortname]

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
            rpp = alldist[dep]["relative_package_path"]
            if "dash_" in rpp:
                dep_name = rpp.split(".")[0]
            else:
                dep_name = "{}_{}".format(project_shortname, str(dep))
                project_ver = str(dep)
            if "css" in rpp:
                css_name = "'{}'".format(rpp)
                script_name = 'NULL'
            else:
                script_name = "'{}'".format(rpp)
                css_name = 'NULL'
            function_frame += [
                frame_element_template.format(
                    dep_name=dep_name,
                    project_ver=project_ver,
                    rpkgname=rpkgname,
                    project_shortname=project_shortname,
                    script_name=script_name,
                    css_name=css_name,
                )
            ]
            function_frame_body = ",\n".join(function_frame)
    elif len(alldist) == 1:
        rpp = alldist[0]["relative_package_path"]
        if "css" in rpp:
            css_name = rpp
            script_name = "NULL"
        else:
            script_name = rpp
            css_name = "NULL"
        function_frame_body = frame_body_template.format(
            project_shortname=project_shortname,
            project_ver=project_ver,
            rpkgname=rpkgname,
            script_name=script_name,
            css_name=css_name,
        )

    function_string = "".join(
        [function_frame_open, function_frame_body, frame_close_template]
    )

    return function_string


def write_help_file(name, props, description, prefix):
    """
    Write R documentation file (.Rd) given component name and properties

    Parameters
    ----------
    name = the name of the Dash component for which a help file is generated
    props = the properties of the component
    description = the component's description, inserted into help file header
    prefix = the DashR library prefix (optional, can be a blank string)

    Returns
    -------
    writes an R help file to the man directory for the generated R package

    """
    file_name = format_fn_name(prefix, name) + ".Rd"

    default_argtext = ""
    item_text = ""

    prop_keys = list(props.keys())

    has_wildcards = any("-*" in key for key in prop_keys)

    # Filter props to remove those we don't want to expose
    for item in prop_keys[:]:
        if item.endswith("-*") or item in r_keywords or item == "setProps":
            prop_keys.remove(item)

    default_argtext += ", ".join("{}=NULL".format(p) for p in prop_keys)

    item_text += "\n\n".join(
        "\\item{{{}}}{{{}{}}}".format(p,
                                      print_r_type(
                                          props[p]["type"]
                                      ),
                                      props[p]["description"])
        for p in prop_keys
    )

    if has_wildcards:
        item_text += '\n\n\\item{...}{wildcards: `data-*` or `aria-*`}'
        default_argtext += ', ...'

    # in R, the online help viewer does not properly wrap lines for
    # the usage string -- we will hard wrap at 80 characters using
    # textwrap.fill, starting from the beginning of the usage string
    argtext = prefix + name + "({})".format(default_argtext)

    file_path = os.path.join('man', file_name)
    with open(file_path, 'w') as f:
        f.write(help_string.format(
            funcname=format_fn_name(prefix, name),
            name=name,
            default_argtext=textwrap.fill(argtext,
                                          width=80,
                                          break_long_words=False),
            item_text=item_text,
            description=description.replace('\n', ' ')
        ))


def write_class_file(name,
                     props,
                     description,
                     project_shortname,
                     prefix=None):
    props = reorder_props(props=props)

    # generate the R help pages for each of the Dash components that we
    # are transpiling -- this is done to avoid using Roxygen2 syntax,
    # we may eventually be able to generate similar documentation using
    # doxygen and an R plugin, but for now we'll just do it on our own
    # from within Python
    write_help_file(
        name,
        props,
        description,
        prefix
    )

    import_string =\
        "# AUTO GENERATED FILE - DO NOT EDIT\n\n"
    class_string = generate_class_string(
        name,
        props,
        project_shortname,
        prefix
    )

    file_name = format_fn_name(prefix, name) + ".R"

    file_path = os.path.join("R", file_name)
    with open(file_path, "w") as f:
        f.write(import_string)
        f.write(class_string)

    print("Generated {}".format(file_name))


def write_js_metadata(pkg_data, project_shortname):
    """
    Write an internal (not exported) R function to return all JS
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
    with open(file_path, "w") as f:
        f.write(function_string)

    # now copy over all JS dependencies from the (Python) components dir
    # the inst/lib directory for the package won't exist on first call
    # create this directory if it is missing
    if not os.path.exists("inst/deps"):
        os.makedirs("inst/deps")

    for javascript in glob.glob("{}/*.js".format(project_shortname)):
        shutil.copy(javascript, "inst/deps/")

    for css in glob.glob("{}/*.css".format(project_shortname)):
        shutil.copy(css, "inst/deps/")

    for sourcemap in glob.glob("{}/*.map".format(project_shortname)):
        shutil.copy(sourcemap, "inst/deps/")


# pylint: disable=R0914, R0913, R0912, R0915
def generate_rpkg(
        pkg_data,
        project_shortname,
        export_string,
        package_depends,
        package_imports,
        package_suggests
):
    """
    Generate documents for R package creation

    Parameters
    ----------
    pkg_data
    project_shortname
    export_string

    Returns
    -------

    """
    # Leverage package.json to import specifics which are also applicable
    # to R package that we're generating here, use .get in case the key
    # does not exist in package.json

    package_name = snake_case_to_camel_case(project_shortname)
    lib_name = pkg_data.get("name")
    package_description = pkg_data.get("description", "")
    package_version = pkg_data.get("version", "0.0.1")

    # remove leading and trailing commas
    if package_depends:
        package_depends = ", " + package_depends.strip(",").lstrip()

    if package_imports:
        package_imports = ", " + package_imports.strip(",").lstrip()

    if package_suggests:
        package_suggests = package_suggests.strip(",").lstrip()

    if "bugs" in pkg_data.keys():
        package_issues = pkg_data["bugs"].get("url", "")
    else:
        package_issues = ""
        print(
            "Warning: a URL for bug reports was "
            "not provided. Empty string inserted.",
            file=sys.stderr,
        )

    if "homepage" in pkg_data.keys():
        package_url = pkg_data.get("homepage", "")
    else:
        package_url = ""
        print(
            "Warning: a homepage URL was not provided. Empty string inserted.",
            file=sys.stderr,
        )

    package_author = pkg_data.get("author")

    package_author_no_email = package_author.split(" <")[0] + " [aut]"

    if not (os.path.isfile("LICENSE") or os.path.isfile("LICENSE.txt")):
        package_license = pkg_data.get("license", "")
    else:
        package_license = pkg_data.get("license", "") + " + file LICENSE"
        # R requires that the LICENSE.txt file be named LICENSE
        if not os.path.isfile("LICENSE"):
            os.symlink("LICENSE.txt", "LICENSE")

    import_string = "# AUTO GENERATED FILE - DO NOT EDIT\n\n"
    packages_string = ''

    rpackage_list = package_depends.split(', ') + package_imports.split(', ')
    rpackage_list = filter(bool, rpackage_list)

    if rpackage_list:
        for rpackage in rpackage_list:
            packages_string += "\nimport({})\n".format(rpackage)

    pkghelp_stub_path = os.path.join("man", package_name + "-package.Rd")

    # generate the internal (not exported to the user) functions which
    # supply the JavaScript dependencies to the dash package.
    # this avoids having to generate an RData file from within Python.
    write_js_metadata(pkg_data=pkg_data, project_shortname=project_shortname)

    with open("NAMESPACE", "w") as f:
        f.write(import_string)
        f.write(export_string)
        f.write(packages_string)

    with open(".Rbuildignore", "w") as f2:
        f2.write(rbuild_ignore_string)

    # Write package stub files for R online help, generate if
    # dashHtmlComponents or dashCoreComponents; makes it easy
    # for R users to bring up main package help page
    pkg_help_header = ""

    if package_name in ["dashHtmlComponents"]:
        pkg_help_header = "Vanilla HTML Components for Dash"
        pkg_help_desc = "Dash is a web application framework that\n\
provides pure Python and R abstraction around HTML, CSS, and\n\
JavaScript. Instead of writing HTML or using an HTML\n\
templating engine, you compose your layout using R\n\
functions within the dashHtmlComponents package. The\n\
source for this package is on GitHub:\n\
plotly/dash-html-components."
    if package_name in ["dashCoreComponents"]:
        pkg_help_header = "Core Interactive UI Components for Dash"
        pkg_help_desc = "Dash ships with supercharged components for\n\
interactive user interfaces. A core set of components,\n\
written and maintained by the Dash team, is available in\n\
the dashCoreComponents package. The source for this package\n\
is on GitHub: plotly/dash-core-components."

    description_string = description_template.format(
        package_name=package_name,
        package_description=package_description,
        package_version=package_version,
        package_author=package_author,
        package_depends=package_depends,
        package_imports=package_imports,
        package_suggests=package_suggests,
        package_license=package_license,
        package_url=package_url,
        package_issues=package_issues,
        package_author_no_email=package_author_no_email,
    )

    with open("DESCRIPTION", "w") as f3:
        f3.write(description_string)

    if pkg_help_header != "":
        pkghelp = pkghelp_stub.format(
            package_name=package_name,
            pkg_help_header=pkg_help_header,
            pkg_help_desc=pkg_help_desc,
            lib_name=lib_name,
            package_author=package_author,
        )
        with open(pkghelp_stub_path, "w") as f4:
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
        prefix,
        package_depends,
        package_imports,
        package_suggests,
        **kwargs
):
    export_string = ""
    for component in components:
        if (
                not component.endswith("-*")
                and str(component) not in r_keywords
                and str(component) not in ["setProps",
                                           "children",
                                           "dashEvents"]
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
    stripped_line = ""
    fnlist = []

    for script in os.listdir("R"):
        if script.endswith(".R") and script not in omitlist:
            rfilelist += [os.path.join("R", script)]

    # in R, either = or <- may be used to create and assign objects
    definitions = ["<-function", "=function"]

    for rfile in rfilelist:
        with open(rfile, "r") as script:
            for line in script:
                stripped_line = line.replace(" ", "").replace("\n", "")
                if any(fndef in stripped_line for fndef in definitions):
                    fnlist += set([re.split("<-|=", stripped_line)[0]])

    export_string += "\n".join("export({})".format(function)
                               for function in fnlist)

    # now, bundle up the package information and create all the requisite
    # elements of an R package, so that the end result is installable either
    # locally or directly from GitHub
    generate_rpkg(
        pkg_data,
        project_shortname,
        export_string,
        package_depends,
        package_imports,
        package_suggests,
    )


def get_r_prop_types(type_object):
    """Mapping from the PropTypes js type object to the R type"""

    def shape_or_exact():
        return 'lists containing elements {}.\n{}'.format(
            ', '.join(
                "'{}'".format(t) for t in list(type_object['value'].keys())
            ),
            'Those elements have the following types:\n{}'.format(
                '\n'.join(
                    create_prop_docstring_r(
                        prop_name=prop_name,
                        type_object=prop,
                        required=prop['required'],
                        description=prop.get('description', ''),
                        indent_num=1
                    ) for prop_name, prop in
                    list(type_object['value'].items())))
            )

    return dict(
        array=lambda: "unnamed list",
        bool=lambda: "logical",
        number=lambda: "numeric",
        string=lambda: "character",
        object=lambda: "named list",
        any=lambda: "logical | numeric | character | "
                    "named list | unnamed list",
        element=lambda: "dash component",
        node=lambda: "a list of or a singular dash "
                     "component, string or number",
        # React's PropTypes.oneOf
        enum=lambda: "a value equal to: {}".format(
            ", ".join("{}".format(str(t["value"]))
                      for t in type_object["value"])
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
            "list" + ((" of {}s").format(
                get_r_type(type_object["value"]))
                      if get_r_type(type_object["value"]) != ""
                      else "")
        ),
        # React's PropTypes.objectOf
        objectOf=lambda: (
            "list with named elements and values of type {}"
            ).format(
                get_r_type(type_object["value"])
            ),

        # React's PropTypes.shape
        shape=shape_or_exact,
        # React's PropTypes.exact
        exact=shape_or_exact
    )


def get_r_type(type_object, is_flow_type=False, indent_num=0):
    """
    Convert JS types to R types for the component definition
    Parameters
    ----------
    type_object: dict
        react-docgen-generated prop type dictionary

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
    elif js_type_name in js_to_r_types:
        prop_type = js_to_r_types[js_type_name]()
        return prop_type
    return ""


def print_r_type(typedata):
    typestring = get_r_type(typedata).capitalize()
    if typestring:
        typestring += ". "
    return typestring


# pylint: disable=too-many-arguments
def create_prop_docstring_r(prop_name, type_object, required, description,
                            indent_num, is_flow_type=False):
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
        type_object=type_object,
        is_flow_type=is_flow_type,
        indent_num=indent_num + 1)

    indent_spacing = '  ' * indent_num
    if '\n' in r_type_name:
        return '{indent_spacing}- {name} ({is_required}): {description}. ' \
               '{name} has the following type: {type}'.format(
                   indent_spacing=indent_spacing,
                   name=prop_name,
                   type=r_type_name,
                   description=description,
                   is_required='required' if required else 'optional')
    return '{indent_spacing}- {name} ({type}' \
           '{is_required}){description}'.format(
               indent_spacing=indent_spacing,
               name=prop_name,
               type='{}; '.format(r_type_name) if r_type_name else '',
               description=(
                   ': {}'.format(description) if description != '' else ''
               ),
               is_required='required' if required else 'optional')
