import os
import shutil

from ..._all_keywords import r_keywords

from ..._r_components_generation import (
    generate_component_wrapper as adapter_compiler,
    generate_description as description_generator,
    generate_help_file as help_generator
)

from ..helpers import glob_js

def component_adapters(compile, prefix, path):
    for component, adapter in compile(adapter_compiler):
        component_path = os.path.join(path, '{}{}.R'.format(prefix, component))
        with open(component_path, 'w') as f:
            f.write(adapter)

def component_help(compile, prefix, path):
    for component, wrapper in compile(help_generator):
        component_path = os.path.join(path, '{}{}.Rd'.format(prefix, component))
        with open(component_path, 'w') as f:
            f.write(wrapper)

def description(get_description, path):
    description = get_description()

    desription_path = os.path.join(path, 'DESCRIPTION')
    with open(desription_path, 'w') as f:
        f.write(description)

def global_help(get_help, get_package_name, path):
    help = get_help()
    package_name = get_package_name()

    if help is not None:
        package_help_path = os.path.join(path, '{}-package.Rd'.format(package_name))
        with open(package_help_path, 'w') as f:
            f.write(help)

def internal(get_internal, path):
    internal_path = os.path.join(path, 'internal.R')
    internal = get_internal()

    with open(internal_path, 'w') as f:
        f.write(internal)

def js_artefacts(source, target):
    glob_js(source, target)

def license(package_data, path):
    license_path = get_license_path(path)

    if has_license(path):
        shutil.copyfile('LICENSE', license_path)

def namespace(compile, prefix, path):
    import_string = '# AUTO GENERATED FILE - DO NOT EDIT\n\n'
    export_string = ''

    for component, none in compile(None):
        if not component.endswith('-*') and \
                str(component) not in r_keywords and \
                str(component) not in ['setProps', 'children', 'dashEvents']:
            export_string += 'export({}{})\n'.format(prefix, component)

    namespace_path = os.path.join(path, 'NAMESPACE')
    with open(namespace_path, 'w') as f:
        f.write(import_string)
        f.write(export_string)

def get_license_path(path):
    return os.path.join(path, 'LICENSE')

def get_license(package_data, path):
    license_path = get_license_path(path)

    result = package_data.get('license', '')
    if has_license(path):
        result = result + ' + file LICENSE'

    return result

def has_license(path):
    license_path = get_license_path(path)
    return os.path.isfile(license_path) or os.path.isfile('LICENSE')