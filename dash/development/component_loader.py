import collections
import json
import os
import textwrap

from .base_component import generate_class
from .base_component import generate_class_file
from .base_component import ComponentRegistry


def _get_metadata(metadata_path):
    # Start processing
    with open(metadata_path) as data_file:
        json_string = data_file.read()
        data = json\
            .JSONDecoder(object_pairs_hook=collections.OrderedDict)\
            .decode(json_string)
    return data


def generate_imports(project_shortname, components):
    with open(os.path.join(project_shortname, '_imports_.py'), 'w') as f:
        f.write(textwrap.dedent(
            '''
            {}

            __all__ = [
            {}
            ]
            '''.format(
                '\n'.join(
                    'from .{0} import {0}'.format(x) for x in components),
                ',\n'.join('    "{}"'.format(x) for x in components)
            )
        ).lstrip())


def load_components(metadata_path,
                    namespace='default_namespace'):
    """Load React component metadata into a format Dash can parse.

    Usage: load_components('../../component-suites/lib/metadata.json')

    Keyword arguments:
    metadata_path -- a path to a JSON file created by
    [`react-docgen`](https://github.com/reactjs/react-docgen).

    Returns:
    components -- a list of component objects with keys
    `type`, `valid_kwargs`, and `setup`.
    """

    # Register the component lib for index include.
    ComponentRegistry.registry.add(namespace)
    components = []

    data = _get_metadata(metadata_path)

    # Iterate over each property name (which is a path to the component)
    for componentPath in data:
        componentData = data[componentPath]

        # Extract component name from path
        # e.g. src/components/MyControl.react.js
        # TODO Make more robust - some folks will write .jsx and others
        # will be on windows. Unfortunately react-docgen doesn't include
        # the name of the component atm.
        name = componentPath.split('/').pop().split('.')[0]
        component = generate_class(
            name,
            componentData['props'],
            componentData['description'],
            namespace
        )

        components.append(component)

    return components


def generate_classes_files(project_shortname, metadata, *component_generators):
    components = []
    for component_path, component_data in metadata.items():
        component_name = component_path.split('/')[-1].split('.')[0]
        components.append(component_name)

        for generator in component_generators:
            generator(
                component_name,
                component_data['props'],
                component_data['description'],
                project_shortname
            )

    return components


def generate_classes(namespace, metadata_path='lib/metadata.json'):
    """Load React component metadata into a format Dash can parse,
    then create python class files.

    Usage: generate_classes()

    Keyword arguments:
    namespace -- name of the generated python package (also output dir)

    metadata_path -- a path to a JSON file created by
    [`react-docgen`](https://github.com/reactjs/react-docgen).

    Returns:
    """

    data = _get_metadata(metadata_path)
    imports_path = os.path.join(namespace, '_imports_.py')

    # Make sure the file doesn't exist, as we use append write
    if os.path.exists(imports_path):
        os.remove(imports_path)

    components = generate_classes_files(namespace, data, generate_class_file)

    # Add the __all__ value so we can import * from _imports_
    generate_imports(namespace, components)
