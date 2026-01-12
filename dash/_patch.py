from typing import List, Union, Optional, Any, Dict


def _operation(name: str, location: List["_KeyType"], **kwargs: Any) -> Dict[str, Any]:
    return {"operation": name, "location": location, "params": kwargs}


_noop: Any = object()

_KeyType = Union[str, int]


def validate_slice(obj: Any):
    if isinstance(obj, slice):
        raise TypeError("a slice is not a valid index for patch")


class Patch:
    """
    Patch a callback output value

    Act like a proxy of the output prop value on the frontend.

    Supported prop types: Dictionaries and lists.
    """

    def __init__(
        self,
        location: Optional[List[_KeyType]] = None,
        parent: Optional["Patch"] = None,
    ):
        if location is not None:
            self._location: List[_KeyType] = location
        else:
            # pylint: disable=consider-using-ternary
            self._location = (parent and parent._location) or []
        if parent is not None:
            self._operations: List[Dict[str, Any]] = parent._operations
        else:
            self._operations = []

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)

    def __getitem__(self, item: _KeyType) -> "Patch":
        validate_slice(item)
        return Patch(location=self._location + [item], parent=self)

    def __getattr__(self, item: _KeyType) -> "Patch":
        if item == "tolist":
            # to_json fix
            raise AttributeError
        if item == "_location":
            return self._location  # type: ignore
        if item == "_operations":
            return self._operations  # type: ignore
        return self.__getitem__(item)

    def __setattr__(self, key: _KeyType, value: Any):
        if key in ("_location", "_operations"):
            self.__dict__[str(key)] = value
        else:
            self.__setitem__(key, value)

    def __delattr__(self, item: _KeyType):
        self.__delitem__(item)

    def __setitem__(self, key: _KeyType, value: Any):
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

    def __delitem__(self, key: _KeyType):
        validate_slice(key)
        self._operations.append(_operation("Delete", self._location + [key]))

    def __iadd__(self, other: Any):
        if isinstance(other, (list, tuple)):
            self.extend(other)
        else:
            self._operations.append(_operation("Add", self._location, value=other))
        if not self._location:
            return self
        return _noop

    def __isub__(self, other: Any):
        self._operations.append(_operation("Sub", self._location, value=other))
        if not self._location:
            return self
        return _noop

    def __imul__(self, other: Any) -> "Patch":
        self._operations.append(_operation("Mul", self._location, value=other))
        if not self._location:
            return self
        return _noop

    def __itruediv__(self, other: Any):
        self._operations.append(_operation("Div", self._location, value=other))
        if not self._location:
            return self
        return _noop

    def __ior__(self, other: Any):
        self.update(E=other)
        if not self._location:
            return self
        return _noop

    def __iter__(self):
        raise TypeError("Patch objects are write-only, you cannot iterate them.")

    def __repr__(self):
        return f"<write-only dash.Patch object at {self._location}>"

    def append(self, item: Any) -> None:
        """Add the item to the end of a list"""
        self._operations.append(_operation("Append", self._location, value=item))

    def prepend(self, item: Any) -> None:
        """Add the item to the start of a list"""
        self._operations.append(_operation("Prepend", self._location, value=item))

    def insert(self, index: int, item: Any) -> None:
        """Add the item at the index of a list"""
        self._operations.append(
            _operation("Insert", self._location, value=item, index=index)
        )

    def clear(self) -> None:
        """Remove all items in a list"""
        self._operations.append(_operation("Clear", self._location))

    def reverse(self) -> None:
        """Reversal of the order of items in a list"""
        self._operations.append(_operation("Reverse", self._location))

    def extend(self, item: Union[list, tuple]) -> None:
        """Add all the items to the end of a list"""
        if not isinstance(item, (list, tuple)):
            raise TypeError(f"{item} should be a list or tuple")
        self._operations.append(_operation("Extend", self._location, value=item))

    def remove(self, item: Any) -> None:
        """filter the item out of a list on the frontend"""
        self._operations.append(_operation("Remove", self._location, value=item))

    def update(self, E: Any = None, **F) -> None:
        """Merge a dict or keyword arguments with another dictionary"""
        value = E or {}
        value.update(F)
        self._operations.append(_operation("Merge", self._location, value=value))

    # pylint: disable=no-self-use
    def sort(self):
        raise KeyError(
            "sort is reserved for future use, use brackets to access this key on your object"
        )

    def to_plotly_json(self) -> Any:
        return {
            "__dash_patch_update": "__dash_patch_update",
            "operations": self._operations,
        }
