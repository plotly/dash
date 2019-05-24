from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import shutil
import glob
import importlib

from ._all_keywords import r_keywords
from ._py_components_generation import reorder_props


# Declaring longer string templates as globals to improve
# readability, make method logic clearer to anyone inspecting
# code below
r_component_string = '''{prefix}{name} <- function({default_argtext}{wildcards}) {{
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
}}'''  # noqa:E501

# the following strings represent all the elements in an object
# of the html_dependency class, which will be propagated by
# iterating over _js_dist in __init__.py
frame_open_template = '''.{rpkgname}_js_metadata <- function() {{
deps_metadata <- list('''

frame_element_template = '''`{dep_name}` = structure(list(name = "{dep_name}",
version = "{project_ver}", src = list(href = NULL,
file = "deps"), meta = NULL,
script = "{dep_rpp}",
stylesheet = NULL, head = NULL, attachment = NULL, package = "{rpkgname}",
all_files = FALSE), class = "html_dependency")'''

frame_body_template = '''`{project_shortname}` = structure(list(name = "{project_shortname}",
version = "{project_ver}", src = list(href = NULL,
file = "deps"), meta = NULL,
script = "{dep_rpp}",
stylesheet = NULL, head = NULL, attachment = NULL, package = "{rpkgname}",
all_files = FALSE), class = "html_dependency")'''  # noqa:E501

frame_close_template = ''')
return(deps_metadata)
}'''

help_string = '''% Auto-generated: do not edit by hand
\\name{{{prefix}{name}}}

\\alias{{{prefix}{name}}}

\\title{{{name} component}}

\\description{{
{description}
}}

\\usage{{
{prefix}{name}({default_argtext})
}}

\\arguments{{
{item_text}
}}
'''

description_template = '''Package: {package_name}
Title: {package_description}
Version: {package_version}
Authors @R: as.person(c({package_author}))
Description: {package_description}
Depends: R (>= 3.0.2)
Imports: dashR
Suggests: testthat, roxygen2
License: {package_license}
URL: {package_url}
BugReports: {package_issues}
Encoding: UTF-8
LazyData: true
Author: {package_author_no_email}
Maintainer: {package_author}
'''


pkghelp_stub = '''% Auto-generated: do not edit by hand
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
'''


# pylint: disable=R0914
def generate_class_string(name, props, project_shortname, prefix):
    # Here we convert from snake case to camel case
    package_name = snake_case_to_camel_case(project_shortname)

    # Ensure props are ordered with children first
    props = reorder_props(props=props)

    prop_keys = list(props.keys())

    wildcards = ''
    wildcard_declaration = ''
    wildcard_names = ''

    if any('-*' in key for key in prop_keys):
        wildcards = ', ...'
        wildcard_declaration =\
            '\n    wildcard_names = names(assert_valid_wildcards(...))\n'
        wildcard_names = ', wildcard_names'

    default_paramtext = ''
    default_argtext = ''
    default_wildcards = ''

    # Produce a string with all property names other than WCs
    prop_names = ", ".join(
        '\'{}\''.format(p)
        for p in prop_keys
        if '*' not in p and
        p not in ['setProps']
    )

    # in R, we set parameters with no defaults to NULL
    # Here we'll do that if no default value exists
    default_wildcards += ", ".join(
        '\'{}\''.format(p)
        for p in prop_keys
        if '*' in p
    )

    if default_wildcards == '':
        default_wildcards = 'NULL'
    else:
        default_wildcards = 'c({})'.format(default_wildcards)

    # Filter props to remove those we don't want to expose
    for item in prop_keys[:]:
        if item.endswith('-*') \
                or item in r_keywords \
                or item == 'setProps':
            prop_keys.remove(item)

    default_argtext += ", ".join(
        '{}=NULL'.format(p)
        for p in prop_keys
    )

    # pylint: disable=C0301
    default_paramtext += ", ".join(
        '{0}={0}'.format(p)
        if p != "children" else
        '{}=children'
        .format(p)
        for p in prop_keys
    )

    return r_component_string.format(prefix=prefix,
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
    and CSS dependency information required by dashR package.

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

    jsdist = getattr(mod, '_js_dist', [])
    project_ver = pkg_data.get('version')

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
    if len(jsdist) > 1:
        for dep in range(len(jsdist)):
            if 'dash_' in jsdist[dep]['relative_package_path']:
                dep_name = jsdist[dep]['relative_package_path'].split('.')[0]
            else:
                dep_name = '{}_{}'.format(project_shortname, str(dep))
                project_ver = str(dep)
            function_frame += [frame_element_template.format(
                dep_name=dep_name,
                project_ver=project_ver,
                rpkgname=rpkgname,
                project_shortname=project_shortname,
                dep_rpp=jsdist[dep]['relative_package_path']
            )]
            function_frame_body = ',\n'.join(function_frame)
    elif len(jsdist) == 1:
        function_frame_body = frame_body_template. \
            format(project_shortname=project_shortname,
                   project_ver=project_ver,
                   rpkgname=rpkgname,
                   dep_rpp=jsdist[0]['relative_package_path'])

    return function_frame_open + ''.join(function_frame_body) + frame_close_template


def generate_help_file(name,
                    props,
                    description,
                    project_shortname,
                    prefix=None):
    # generate the R help pages for each of the Dash components that we
    # are transpiling -- this is done to avoid using Roxygen2 syntax,
    # we may eventually be able to generate similar documentation using
    # doxygen and an R plugin, but for now we'll just do it on our own
    # from within Python
    props = reorder_props(props=props)

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
    default_argtext = ''
    item_text = ''

    prop_keys = list(props.keys())

    has_wildcards = any('-*' in key for key in prop_keys)

    # Filter props to remove those we don't want to expose
    for item in prop_keys[:]:
        if item.endswith('-*') \
                or item in r_keywords \
                or item == 'setProps':
            prop_keys.remove(item)

    default_argtext += ", ".join(
        '{}=NULL'.format(p)
        for p in prop_keys
    )

    item_text += "\n\n".join(
        '\\item{{{}}}{{{}}}'.format(p, props[p]['description'])
        for p in prop_keys
    )

    if has_wildcards:
        item_text += '\n\n\\item{...}{wildcards: `data-*` or `aria-*`}'
        default_argtext += ', ...'

    return help_string.format(
        prefix=prefix,
        name=name,
        default_argtext=default_argtext,
        item_text=item_text,
        description=description.replace('\n', ' ')
    )


def generate_component_wrapper(name,
                     props,
                     description,
                     project_shortname,
                     prefix=None):
    props = reorder_props(props=props)

    import_string =\
        "# AUTO GENERATED FILE - DO NOT EDIT\n\n"
    class_string = generate_class_string(
        name,
        props,
        project_shortname,
        prefix
    )

    return import_string + class_string

# pylint: disable=R0914
def generate_description(pkg_data,
                  project_shortname,
                  package_license):
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
    lib_name = pkg_data.get('name')
    package_description = pkg_data.get('description', '')
    package_version = pkg_data.get('version', '0.0.1')

    if 'bugs' in pkg_data.keys():
        package_issues = pkg_data['bugs'].get('url', '')
    else:
        package_issues = ''
        print(
            'Warning: a URL for bug reports was '
            'not provided. Empty string inserted.',
            file=sys.stderr
        )

    if 'homepage' in pkg_data.keys():
        package_url = pkg_data.get('homepage', '')
    else:
        package_url = ''
        print(
            'Warning: a homepage URL was not provided. Empty string inserted.',
            file=sys.stderr
        )

    package_author = pkg_data.get('author')

    package_author_no_email = package_author.split(" <")[0] + ' [aut]'


    pkghelp_stub_path = os.path.join('man', package_name + '-package.Rd')



    # Write package stub files for R online help, generate if
    # dashHtmlComponents or dashCoreComponents; makes it easy
    # for R users to bring up main package help page
    pkg_help_header = ""

    if package_name in ['dashHtmlComponents']:
        pkg_help_header = "Vanilla HTML Components for Dash"
        pkg_help_desc = "Dash is a web application framework that\n\
provides pure Python and R abstraction around HTML, CSS, and\n\
JavaScript. Instead of writing HTML or using an HTML\n\
templating engine, you compose your layout using R\n\
functions within the dashHtmlComponents package. The\n\
source for this package is on GitHub:\n\
plotly/dash-html-components."
    if package_name in ['dashCoreComponents']:
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
        package_license=package_license,
        package_url=package_url,
        package_issues=package_issues,
        package_author_no_email=package_author_no_email
    )

    pkghelp = None if pkg_help_header == '' else pkghelp_stub.format(
        package_name=package_name,
        pkg_help_header=pkg_help_header,
        pkg_help_desc=pkg_help_desc,
        lib_name=lib_name,
        package_author=package_author
    )

    return description_string, pkghelp, package_name



# This converts a string from snake case to camel case
# Not required for R package name to be in camel case,
# but probably more conventional this way
def snake_case_to_camel_case(namestring):
    s = namestring.split('_')
    return s[0] + ''.join(w.capitalize() for w in s[1:])
