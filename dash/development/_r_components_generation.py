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
r_component_string = '''{prefix}{name} <- function(..., {default_argtext}) {{

    component <- list(
        props = list({default_paramtext}),
        type = '{name}',
        namespace = '{project_shortname}',
        propNames = c({prop_names}),
        package = '{package_name}'
        )

    component$props <- filter_null(component$props)
    component <- append_wildcard_props(component, wildcards = {default_wildcards}, ...)

    structure(component, class = c('dash_component', 'list'))
}}'''  # noqa:E501

# the following strings represent all the elements in an object
# of the html_dependency class, which will be propagated by
# iterating over _js_dist in __init__.py
frame_open_template = '''.{rpkgname}_js_metadata <- function() {{
deps_metadata <- list('''

frame_element_template = '''`{dep_name}` = structure(list(name = "{dep_name}",
version = "{project_ver}", src = list(href = NULL,
file = "lib/"), meta = NULL,
script = "{dep_rpp}",
stylesheet = NULL, head = NULL, attachment = NULL, package = "{rpkgname}",
all_files = FALSE), class = "html_dependency")'''

frame_body_template = '''`{project_shortname}` = structure(list(name = "{project_shortname}",
version = "{project_ver}", src = list(href = NULL,
file = "lib/"), meta = NULL,
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
{prefix}{name}(..., {default_argtext})
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
Suggests: testthat, roxygen2
License: {package_license}
URL: {package_url}
BugReports: {package_issues}
Encoding: UTF-8
LazyData: true
Author: {package_author_no_email}
Maintainer: {package_author}
'''

rbuild_ignore_string = r'''# ignore JS config files/folders
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
demo/*.js
demo/*.html
demo/*.css

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
'''


# This is an initial attempt at resolving type inconsistencies
# between R and JSON.
def props_to_r_type(current_prop):
    object_type = current_prop['type']['name']
    if 'defaultValue' in current_prop and object_type == 'string':
        if "\"" in current_prop['defaultValue']['value']:
            argument = current_prop['defaultValue']['value']
        else:
            argument = "{}".format(current_prop['defaultValue']['value'])
    elif object_type == 'custom' and 'raw' in current_prop['type']:
        argument = current_prop['defaultValue'].get('value', 'numeric()')
    elif object_type == 'enum':
        argument = current_prop.get('defaultValue', {}).get('value', 'NULL')
    elif 'defaultValue' in current_prop and object_type == 'object':
        argument = 'list()'
    elif 'defaultValue' in current_prop and \
            current_prop['defaultValue']['value'] == '[]':
        argument = 'list()'
    elif object_type == 'number':
        argument = current_prop['defaultValue'].get('value', 'NULL')
    elif object_type == 'bool':
        argument = current_prop['defaultValue'].get('value')
        if argument:
            argument = 'TRUE'
        else:
            argument = 'logical()'
    else:
        argument = 'NULL'
    return argument


# pylint: disable=R0914
def generate_class_string(name, props, project_shortname, prefix):
    # Here we convert from snake case to camel case
    package_name = snake_case_to_camel_case(project_shortname)

    prop_keys = props.keys()

    default_paramtext = ''
    default_argtext = ''
    default_wildcards = ''

    # Produce a string with all property names other than WCs
    prop_names = ", ".join(
        '\'{}\''.format(p)
        for p in prop_keys
        if '*' not in p and
        p not in ['setProps', 'dashEvents', 'fireEvent']
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
    for p in prop_keys:
        if p.endswith("-*") \
                or p in r_keywords \
                or p in ['setProps', 'dashEvents', 'fireEvent']:
            prop_keys.remove(p)

    default_argtext += ", ".join(
        '{}={}'.format(p, props_to_r_type(props[p]))
        if 'defaultValue' in props[p] else
        '{}=NULL'.format(p)
        for p in prop_keys
    )

    # pylint: disable=C0301
    default_paramtext += ", ".join(
        '{}={}'.format(p, p)
        if p != "children" else
        '{}=c(children, assert_valid_children(..., wildcards = {}))'
        .format(p, default_wildcards)
        for p in prop_keys
    )
    return r_component_string.format(prefix=prefix,
                                     name=name,
                                     default_argtext=default_argtext,
                                     default_paramtext=default_paramtext,
                                     project_shortname=project_shortname,
                                     prop_names=prop_names,
                                     package_name=package_name,
                                     default_wildcards=default_wildcards)


# pylint: disable=R0914
def generate_js_metadata(project_shortname):
    """
    Dynamically generate R function to supply JavaScript
    dependency information required by htmltools package,
    which is loaded by dashR.

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
    project_ver = getattr(mod, '__version__', [])

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

    function_string = ''.join([function_frame_open,
                               function_frame_body,
                               frame_close_template])

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
    file_name = '{}{}.Rd'.format(prefix, name)
    prop_keys = props.keys()

    default_argtext = ''
    item_text = ''

    # Ensure props are ordered with children first
    props = reorder_props(props=props)

    # Filter props to remove those we don't want to expose
    for p in prop_keys:
        if p.endswith("-*") \
                or p in r_keywords \
                or p in ['setProps', 'dashEvents', 'fireEvent']:
            prop_keys.remove(p)

    default_argtext += ", ".join(
        '{}={}'.format(p, props_to_r_type(props[p]))
        if 'defaultValue' in props[p] else
        '{}=NULL'.format(p)
        for p in prop_keys
    )

    item_text += "\n\n".join(
        '\\item{{{}}}{{{}}}'.format(p, props[p]['description'])
        for p in prop_keys
    )

    file_path = os.path.join('man', file_name)
    with open(file_path, 'w') as f:
        f.write(help_string.format(
            prefix=prefix,
            name=name,
            default_argtext=default_argtext,
            item_text=item_text,
            description=description.replace('\n', ' ')
        ))


def write_class_file(name,
                     props,
                     description,
                     project_shortname,
                     prefix=None):
    import_string =\
        "# AUTO GENERATED FILE - DO NOT EDIT\n\n"
    class_string = generate_class_string(
        name,
        props,
        project_shortname,
        prefix
    )
    file_name = "{}{}.R".format(prefix, name)

    file_path = os.path.join('R', file_name)
    with open(file_path, 'w') as f:
        f.write(import_string)
        f.write(class_string)

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

    print('Generated {}'.format(file_name))


def write_js_metadata(project_shortname):
    """
    Write an internal (not exported) R function to return all JS
    dependencies as required by htmltools package given a
    function string

    Parameters
    ----------
    project_shortname = hyphenated string, e.g. dash-html-components

    Returns
    -------

    """
    function_string = generate_js_metadata(
        project_shortname
    )
    file_name = "internal.R"

    # the R source directory for the package won't exist on first call
    # create the R directory if it is missing
    if not os.path.exists('R'):
        os.makedirs('R')

    file_path = os.path.join('R', file_name)
    with open(file_path, 'w') as f:
        f.write(function_string)

    # now copy over all JS dependencies from the (Python) components dir
    # the inst/lib directory for the package won't exist on first call
    # create this directory if it is missing
    if not os.path.exists('inst/lib'):
        os.makedirs('inst/lib')

    for javascript in glob.glob('{}/*.js'.format(project_shortname)):
        shutil.copy(javascript, 'inst/lib/')

    for css in glob.glob('{}/*.css'.format(project_shortname)):
        shutil.copy(css, 'inst/lib/')


# pylint: disable=R0914
def generate_rpkg(pkg_data,
                  project_shortname,
                  export_string):
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

    if not (os.path.isfile('LICENSE') or os.path.isfile('LICENSE.txt')):
        package_license = pkg_data.get('license', '')
    else:
        package_license = pkg_data.get('license', '') + ' + file LICENSE'
        # R requires that the LICENSE.txt file be named LICENSE
        if not os.path.isfile('LICENSE'):
            os.symlink("LICENSE.txt", "LICENSE")

    import_string =\
        '# AUTO GENERATED FILE - DO NOT EDIT\n\n'

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

    # generate the internal (not exported to the user) functions which
    # supply the JavaScript dependencies to the htmlDependency package,
    # which is required by DashR (this avoids having to generate an
    # RData file from within Python, given the current package generation
    # workflow)
    write_js_metadata(
        project_shortname
    )

    with open('NAMESPACE', 'w') as f:
        f.write(import_string)
        f.write(export_string)

    with open('DESCRIPTION', 'w') as f2:
        f2.write(description_string)

    with open('.Rbuildignore', 'w') as f3:
        f3.write(rbuild_ignore_string)


# This converts a string from snake case to camel case
# Not required for R package name to be in camel case,
# but probably more conventional this way
def snake_case_to_camel_case(namestring):
    s = namestring.split('_')
    return s[0] + ''.join(w.capitalize() for w in s[1:])


# pylint: disable=unused-argument
def generate_exports(project_shortname,
                     components,
                     metadata,
                     pkg_data,
                     prefix,
                     **kwargs):
    export_string = ''
    for component in components:
        if not component.endswith('-*') and \
                str(component) not in r_keywords and \
                str(component) not in ['setProps', 'children', 'dashEvents']:
            export_string += 'export({}{})\n'.format(prefix, component)

    # now, bundle up the package information and create all the requisite
    # elements of an R package, so that the end result is installable either
    # locally or directly from GitHub
    generate_rpkg(
        pkg_data,
        project_shortname,
        export_string
    )
