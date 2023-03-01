def _operation(name, location, **kwargs):
    return {"operation": name, "location": location, "params": dict(**kwargs)}


_noop = object()


def validate_slice(obj):
    if isinstance(obj, slice):
        raise TypeError("a slice is not a valid index for patch")


class Patch:
    """
    Patch a callback output value

    Act like a proxy of the output prop value on the frontend.

    Supported prop types: Dictionaries and lists.
    """

    def __init__(self, location=None, parent=None):
        if location is not None:
            self._location = location
        else:
            # pylint: disable=consider-using-ternary
            self._location = (parent and parent._location) or []
        if parent is not None:
            self._operations = parent._operations
        else:
            self._operations = []

    def __getitem__(self, item):
        validate_slice(item)
        return Patch(location=self._location + [item], parent=self)

    def __getattr__(self, item):
        if item == "tolist":
            # to_json fix
            raise AttributeError
        if item == "_location":
            return self._location
        if item == "_operations":
            return self._operations
        return self.__getitem__(item)

    def __setattr__(self, key, value):
        if key in ("_location", "_operations"):
            self.__dict__[key] = value
        else:
            self.__setitem__(key, value)

    def __delattr__(self, item):
        self.__delitem__(item)

    def __setitem__(self, key, value):
        validate_slice(key)
        if value is _noop:
            # The += set themselves.
            return
        self._operations.append(
            _operation(
                "Assign",
                self._location + [key],
                value=value,
            )
        )

    def __delitem__(self, key):
        validate_slice(key)
        self._operations.append(_operation("Delete", self._location + [key]))

    def __iadd__(self, other):
        if isinstance(other, (list, tuple)):
            self.extend(other)
        else:
            self._operations.append(_operation("Add", self._location, value=other))
        return _noop

    def __isub__(self, other):
        self._operations.append(_operation("Sub", self._location, value=other))
        return _noop

    def __imul__(self, other):
        self._operations.append(_operation("Mul", self._location, value=other))
        return _noop

    def __itruediv__(self, other):
        self._operations.append(_operation("Div", self._location, value=other))
        return _noop

    def __ior__(self, other):
        self.merge(other)
        return _noop

    def append(self, item):
        self._operations.append(_operation("Append", self._location, value=item))

    def prepend(self, item):
        self._operations.append(_operation("Prepend", self._location, value=item))

    def insert(self, index, item):
        self._operations.append(
            _operation("Insert", self._location, value=item, index=index)
        )

    def clear(self):
        self._operations.append(_operation("Clear", self._location))

    def reverse(self):
        self._operations.append(_operation("Reverse", self._location))

    def extend(self, item):
        if not isinstance(item, (list, tuple)):
            raise TypeError(f"{item} should be a list or tuple")
        self._operations.append(_operation("Extend", self._location, value=item))

    def merge(self, item):
        if not isinstance(item, dict):
            raise TypeError(f"{item} should be a dictionary")
        self._operations.append(_operation("Merge", self._location, value=item))

    def to_plotly_json(self):
        return {
            "__dash_patch_update": "__dash_patch_update",
            "operations": self._operations,
        }
