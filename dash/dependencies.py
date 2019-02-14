class DashDependency:
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


# pylint: disable=too-few-public-methods
class Output(DashDependency):
    """Output of a callback."""


# pylint: disable=too-few-public-methods
class Input(DashDependency):
    """Input of callback trigger an update when it is updated."""


# pylint: disable=too-few-public-methods
class State(DashDependency):
    """Use the value of a state in a callback but don't trigger updates."""
