class DashDependency:
    # pylint: disable=too-few-public-methods
    def __init__(self, component_id, component_property):
        self.component_id = component_id
        self.component_property = component_property

    def __str__(self):
        return '{}.{}'.format(
            self.component_id,
            self.component_property
        )

    def __repr__(self):
        return '<{} `{}`>'.format(self.__class__.__name__, self)

    def __eq__(self, other):
        return isinstance(other, DashDependency) and str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


class Output(DashDependency):  # pylint: disable=too-few-public-methods
    """Output of a callback."""


class Input(DashDependency):  # pylint: disable=too-few-public-methods
    """Input of callback trigger an update when it is updated."""


class State(DashDependency):  # pylint: disable=too-few-public-methods
    """Use the value of a state in a callback but don't trigger updates."""


class ClientsideFunction:
    # pylint: disable=too-few-public-methods
    def __init__(self, namespace=None, function_name=None):

        if namespace.startswith('_dashprivate_'):
            raise ValueError("Namespaces cannot start with '_dashprivate_'.")

        if namespace in ['PreventUpdate', 'no_update']:
            raise ValueError('"{}" is a forbidden namespace in'
                             ' dash_clientside.'.format(namespace))

        self.namespace = namespace
        self.function_name = function_name

    def __repr__(self):
        return 'ClientsideFunction({}, {})'.format(
            self.namespace,
            self.function_name
        )
