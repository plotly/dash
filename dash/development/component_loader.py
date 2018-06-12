import collections
import json
from .base_component import generate_class
from .base_component import generate_class_file


def _get_metadata(metadata_path):
    # Start processing
    with open(metadata_path) as data_file:
        json_string = data_file.read()
        data = json\
            .JSONDecoder(object_pairs_hook=collections.OrderedDict)\
            .decode(json_string)
    return data


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


def generate_classes(metadata_path='lib/metadata.json', output_dir='lib'):
    """Load React component metadata into a format Dash can parse,
    then create python class files.

    Usage: generate_classes('../../component-suites/lib/metadata.json')

    Keyword arguments:
    metadata_path -- a path to a JSON file created by
    [`react-docgen`](https://github.com/reactjs/react-docgen).

    output_dir -- the directory to put component classes in

    Returns:
    """

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
        generate_class_file(
            name,
            componentData['props'],
            componentData['description'],
            output_dir
        )
