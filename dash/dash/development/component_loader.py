import json
from base_component import generate_class


def empty(self):
    pass


def load_components(metadata_path,
                    default_props=['content', 'id', 'key', 'className', 'style', 'dependencies'],
                    namespace={},
                    module_name='__main__'):
    """Load React component metadata into a format Dash can parse.

    Usage: load_components('../../component-suites/lib/metadata.json', ['content', 'id', 'key', 'className', 'style', 'dependencies'])

    Keyword arguments:
    metadata_path -- a path to a JSON file created by [`react-docgen`](https://github.com/reactjs/react-docgen).
    default_props -- props not in component propTypes that should be considered valid.

    Returns:
    components -- a list of component objects with keys `type`, `valid_kwargs`, and `setup`.
    """

    # This will be returned
    components = []

    # Start processing
    with open(metadata_path) as data_file:
        data = json.load(data_file)

    # Iterate over each property name (which is a path to the component)
    for path in data:
        componentData = data[path]

        # Extract component name from path
        # e.g. src/components/MyControl.react.js
        # TODO Make more robust
        name = path.split('/').pop().split('.')[0]

        # Extract props
        props = []

        if 'props' in componentData:
            componentProps = componentData['props']

            for prop in componentProps:
                props.append(prop)

        component_spec = {
            'type': name,
            # Convert list to set and back again to get unique values only.
            # This avoids the dreaded `SyntaxError: keyword argument repeated`
            # in dynamic generate_class() function.
            'valid_kwargs': list(set(default_props + props)),
            'setup': empty
        }

        component = generate_class(
            component_spec['type'],
            component_spec['valid_kwargs'],
            component_spec['setup']
        )

        component.__module__ = module_name
        namespace[component_spec['type']] = component
