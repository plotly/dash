def _operation(name, location, **kwargs):
    return {"operation": name, "location": location, "params": dict(**kwargs)}


_noop = object()


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
        self._operations.append(_operation("Delete", self._location + [key]))

    def __add__(self, other):
        self._operations.append(_operation("Add", self._location, value=other))
        return _noop

    def __iadd__(self, other):
        self._operations.append(_operation("Add", self._location, value=other))
        return _noop

    def __sub__(self, other):
        self._operations.append(_operation("Sub", self._location, value=other))
        return _noop

    def __isub__(self, other):
        self._operations.append(_operation("Sub", self._location, value=other))
        return _noop

    def __mul__(self, other):
        self._operations.append(_operation("Mul", self._location, value=other))
        return _noop

    def __imul__(self, other):
        self._operations.append(_operation("Mul", self._location, value=other))
        return _noop

    def __truediv__(self, other):
        self._operations.append(_operation("Div", self._location, value=other))
        return _noop

    def __itruediv__(self, other):
        self._operations.append(_operation("Div", self._location, value=other))
        return _noop

    def append(self, item):
        self._operations.append(_operation("Append", self._location, value=item))

    def prepend(self, item):
        self._operations.append(_operation("Prepend", self._location, value=item))

    def extend(self, item):
        if not isinstance(item, list):
            raise TypeError(f"{item} should be a list")
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
