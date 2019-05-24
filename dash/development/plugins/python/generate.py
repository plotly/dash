import json
import os
import shutil

from ..helpers import (
    compile,
    get_package_data,
    glob_js
)

from ..._py_components_generation import (
    generate_component_wrapper as adapter_compiler,
    generate_imports as py_generate_imports
)

def generate(project_shortname, package_info_filename, metadata, root):
    # Python Generation -- Version
    module_path = os.path.join(root, project_shortname)
    version_path = os.path.join(module_path, 'version.py')

    package_data = get_package_data()
    version = package_data['version'].replace(' ', '_').replace('-', '_')

    with open(version_path, 'w') as f:
        f.write('__version__ = \'{}\''.format(version))

    package_target = os.path.join(root, package_info_filename)

    if package_target != 'package.json':
        shutil.copyfile(
            'package.json',
            package_target
        )

    # Python Generation -- Metadata
    metadata_path = os.path.join(module_path, 'metadata.json')

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    if root != '':
        shutil.copyfile('LICENSE', os.path.join(root, 'LICENSE'))
        shutil.copyfile('README.md', os.path.join(root, 'README.md'))

    # Python Generation -- Component Wrappers
    bound_compile = lambda compiler: compile(project_shortname, metadata, compiler)

    components, wrappers = bound_compile(adapter_compiler)

    for component, wrapper in zip(components, wrappers):
        component_path = os.path.join(module_path, '{}.py'.format(component))
        with open(component_path, 'w') as f:
            f.write(wrapper)

    # Python Generation -- Imports
    imports = py_generate_imports(project_shortname, components)
    imports_path = os.path.join(module_path, '_imports_.py')

    with open(imports_path, 'w') as f:
        f.write(imports)

    glob_js('dist/js', module_path)