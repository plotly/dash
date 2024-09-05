import collections
import json
import os
import warnings


from ._py_components_generation import (
    generate_class_file,
    generate_imports,
    generate_classes_files,
    generate_class,
)
from .base_component import ComponentRegistry


def _get_metadata(metadata_path):
    # Start processing
    with open(metadata_path, encoding="utf-8") as data_file:
        json_string = data_file.read()
        data = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(
            json_string
        )
    return data


def load_components(metadata_path, namespace="default_namespace"):
    """Load React component metadata into a format Dash can parse.

    Usage: load_components('../../component-suites/lib/metadata.json')

    Keyword arguments:
    metadata_path -- a path to a JSON file created by
    [`react-docgen`](https://github.com/reactjs/react-docgen).

    Returns:
    components -- a list of component objects with keys
    `type`, `valid_kwargs`, and `setup`.
    """
    warnings.warn(
        DeprecationWarning(
            "Dynamic components loading has been deprecated and will be removed"
            " in dash 3.0.\n"
            f"Update {namespace} to generate components with dash-generate-components"
        )
    )
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
        name = componentPath.split("/").pop().split(".")[0]
        component = generate_class(
            name, componentData["props"], componentData["description"], namespace, None
        )

        components.append(component)

    return components


def generate_classes(namespace, metadata_path="lib/metadata.json"):
    """Load React component metadata into a format Dash can parse, then create
    Python class files.

    Usage: generate_classes()

    Keyword arguments:
    namespace -- name of the generated Python package (also output dir)

    metadata_path -- a path to a JSON file created by
    [`react-docgen`](https://github.com/reactjs/react-docgen).

    Returns:
    """

    data = _get_metadata(metadata_path)
    imports_path = os.path.join(namespace, "_imports_.py")

    # Make sure the file doesn't exist, as we use append write
    if os.path.exists(imports_path):
        os.remove(imports_path)

    components = generate_classes_files(namespace, data, generate_class_file)

    # Add the __all__ value so we can import * from _imports_
    generate_imports(namespace, components)
