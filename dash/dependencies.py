# pylint: disable=old-style-class, too-few-public-methods
class Output:
    def __init__(self, component_id, component_property):
        self.component_id = component_id
        self.component_property = component_property


# pylint: disable=old-style-class, too-few-public-methods
class Input:
    def __init__(self, component_id, component_property):
        self.component_id = component_id
        self.component_property = component_property


# pylint: disable=old-style-class, too-few-public-methods
class State:
    def __init__(self, component_id, component_property):
        self.component_id = component_id
        self.component_property = component_property


# pylint: disable=old-style-class, too-few-public-methods
class Event:
    def __init__(self, component_id, component_event):
        self.component_id = component_id
        self.component_event = component_event
