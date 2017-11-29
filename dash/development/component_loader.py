import collections
import json
from .base_component import generate_class


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

    # Start processing
    with open(metadata_path) as data_file:
        json_string = data_file.read()
        data = json\
            .JSONDecoder(object_pairs_hook=collections.OrderedDict)\
            .decode(json_string)

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
