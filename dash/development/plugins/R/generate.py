import os

from ..helpers import (
    compile,
    get_package_data
)

from ..._r_components_generation import (
    generate_description as description_and_help_generator,
    generate_js_metadata as metadata_generator
)

from .generators import (
    component_adapters,
    component_help,
    description,
    global_help,
    internal,
    namespace,
    js_artefacts,
    license,

    get_license
)

def compile_zip(project_shortname, metadata, compiler):
    components, results = compile(project_shortname, metadata, compiler)

    return zip(components, results)

def generate(project_shortname, metadata, prefix, root):
    if not prefix:
        return

    man_path = os.path.join(root, 'man')
    r_path = os.path.join(root, 'R')
    inst_deps_path = os.path.join(root, 'inst/deps')

    if not os.path.exists(r_path):
        os.makedirs(r_path)

    if not os.path.exists(man_path):
        os.makedirs(man_path)

    if not os.path.exists(inst_deps_path):
        os.makedirs(inst_deps_path)

    package_data = get_package_data()
    package_license = get_license(package_data, root)

    bound_compile = lambda compiler: compile_zip(project_shortname, metadata, compiler)
    get_description = lambda: description_and_help_generator(package_data, project_shortname, package_license)[0]
    get_help = lambda: description_and_help_generator(package_data, project_shortname, package_license)[1]
    get_internal = lambda: metadata_generator(package_data, project_shortname)
    get_package_name = lambda: description_and_help_generator(package_data, project_shortname, package_license)[2]

    component_adapters(bound_compile, prefix, r_path)
    component_help(bound_compile, prefix, man_path)
    description(get_description, root)
    global_help(get_help, get_package_name, man_path)
    internal(get_internal, r_path)
    js_artefacts('dist/js', inst_deps_path)
    license(package_data, root)
    namespace(bound_compile, prefix, root)