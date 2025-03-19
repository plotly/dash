import abc
import collections
import inspect
import sys
import typing
import uuid
import random
import warnings
import textwrap

from .._utils import patch_collections_abc, stringify_id, OrderedSet

MutableSequence = patch_collections_abc("MutableSequence")

rd = random.Random(0)

_deprecated_components = {
    "dash_core_components": {
        "LogoutButton": textwrap.dedent(
            """
        The Logout Button is no longer used with Dash Enterprise and can be replaced with a html.Button or html.A.
        eg: html.A(href=os.getenv('DASH_LOGOUT_URL'))
    """
        )
    }
}


# pylint: disable=no-init,too-few-public-methods
class ComponentRegistry:
    """Holds a registry of the namespaces used by components."""

    registry = OrderedSet()
    children_props = collections.defaultdict(dict)
    namespace_to_package = {}

    @classmethod
    def get_resources(cls, resource_name, includes=None):
        resources = []

        for module_name in cls.registry:
            if includes is not None and module_name not in includes:
                continue
            module = sys.modules[module_name]
            resources.extend(getattr(module, resource_name, []))

        return resources


class ComponentMeta(abc.ABCMeta):

    # pylint: disable=arguments-differ
    def __new__(mcs, name, bases, attributes):
        component = abc.ABCMeta.__new__(mcs, name, bases, attributes)
        module = attributes["__module__"].split(".")[0]
        if name == "Component" or module == "builtins":
            # Don't do the base component
            # and the components loaded dynamically by load_component
            # as it doesn't have the namespace.
            return component

        _namespace = attributes.get("_namespace", module)
        ComponentRegistry.namespace_to_package[_namespace] = module
        ComponentRegistry.registry.add(module)
        ComponentRegistry.children_props[_namespace][name] = attributes.get(
            "_children_props"
        )

        return component


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def _check_if_has_indexable_children(item):
    if not hasattr(item, "children") or (
        not isinstance(item.children, Component)
        and not isinstance(item.children, (tuple, MutableSequence))
    ):

        raise KeyError


class Component(metaclass=ComponentMeta):
    _children_props = []
    _base_nodes = ["children"]
    _namespace: str
    _type: str
    _prop_names: typing.List[str]

    _valid_wildcard_attributes: typing.List[str]
    available_wildcard_properties: typing.List[str]

    class _UNDEFINED:
        def __repr__(self):
            return "undefined"

        def __str__(self):
            return "undefined"

    UNDEFINED = _UNDEFINED()

    class _REQUIRED:
        def __repr__(self):
            return "required"

        def __str__(self):
            return "required"

    REQUIRED = _REQUIRED()

    def __init__(self, **kwargs):
        self._validate_deprecation()
        import dash  # pylint: disable=import-outside-toplevel, cyclic-import

        for k, v in list(kwargs.items()):
            # pylint: disable=no-member
            k_in_propnames = k in self._prop_names
            k_in_wildcards = any(
                k.startswith(w) for w in self._valid_wildcard_attributes
            )
            # e.g. "The dash_core_components.Dropdown component (version 1.6.0)
            # with the ID "my-dropdown"
            id_suffix = f' with the ID "{kwargs["id"]}"' if "id" in kwargs else ""
            try:
                # Get fancy error strings that have the version numbers
                error_string_prefix = "The `{}.{}` component (version {}){}"
                # These components are part of dash now, so extract the dash version:
                dash_packages = {
                    "dash_html_components": "html",
                    "dash_core_components": "dcc",
                    "dash_table": "dash_table",
                }
                if self._namespace in dash_packages:
                    error_string_prefix = error_string_prefix.format(
                        dash_packages[self._namespace],
                        self._type,
                        dash.__version__,
                        id_suffix,
                    )
                else:
                    # Otherwise import the package and extract the version number
                    error_string_prefix = error_string_prefix.format(
                        self._namespace,
                        self._type,
                        getattr(__import__(self._namespace), "__version__", "unknown"),
                        id_suffix,
                    )
            except ImportError:
                # Our tests create mock components with libraries that
                # aren't importable
                error_string_prefix = f"The `{self._type}` component{id_suffix}"

            if not k_in_propnames and not k_in_wildcards:
                allowed_args = ", ".join(
                    sorted(self._prop_names)
                )  # pylint: disable=no-member
                raise TypeError(
                    f"{error_string_prefix} received an unexpected keyword argument: `{k}`"
                    f"\nAllowed arguments: {allowed_args}"
                )

            if k not in self._base_nodes and isinstance(v, Component):
                raise TypeError(
                    error_string_prefix
                    + " detected a Component for a prop other than `children`\n"
                    + f"Prop {k} has value {v!r}\n\n"
                    + "Did you forget to wrap multiple `children` in an array?\n"
                    + 'For example, it must be html.Div(["a", "b", "c"]) not html.Div("a", "b", "c")\n'
                )

            if k == "id":
                if isinstance(v, dict):
                    for id_key, id_val in v.items():
                        if not isinstance(id_key, str):
                            raise TypeError(
                                "dict id keys must be strings,\n"
                                + f"found {id_key!r} in id {v!r}"
                            )
                        if not isinstance(id_val, (str, int, float, bool)):
                            raise TypeError(
                                "dict id values must be strings, numbers or bools,\n"
                                + f"found {id_val!r} in id {v!r}"
                            )
                elif not isinstance(v, str):
                    raise TypeError(f"`id` prop must be a string or dict, not {v!r}")

            setattr(self, k, v)

    def _set_random_id(self):

        if hasattr(self, "id"):
            return getattr(self, "id")

        kind = f"`{self._namespace}.{self._type}`"  # pylint: disable=no-member

        if getattr(self, "persistence", False):
            raise RuntimeError(
                f"""
                Attempting to use an auto-generated ID with the `persistence` prop.
                This is prohibited because persistence is tied to component IDs and
                auto-generated IDs can easily change.

                Please assign an explicit ID to this {kind} component.
                """
            )
        if "dash_snapshots" in sys.modules:
            raise RuntimeError(
                f"""
                Attempting to use an auto-generated ID in an app with `dash_snapshots`.
                This is prohibited because snapshots saves the whole app layout,
                including component IDs, and auto-generated IDs can easily change.
                Callbacks referencing the new IDs will not work with old snapshots.

                Please assign an explicit ID to this {kind} component.
                """
            )

        v = str(uuid.UUID(int=rd.randint(0, 2**128)))
        setattr(self, "id", v)
        return v

    def to_plotly_json(self):
        # Add normal properties
        props = {
            p: getattr(self, p)
            for p in self._prop_names  # pylint: disable=no-member
            if hasattr(self, p)
        }
        # Add the wildcard properties data-* and aria-*
        props.update(
            {
                k: getattr(self, k)
                for k in self.__dict__
                if any(
                    k.startswith(w)
                    # pylint:disable=no-member
                    for w in self._valid_wildcard_attributes
                )
            }
        )
        as_json = {
            "props": props,
            "type": self._type,  # pylint: disable=no-member
            "namespace": self._namespace,  # pylint: disable=no-member
        }

        return as_json

    # pylint: disable=too-many-branches, too-many-return-statements
    # pylint: disable=redefined-builtin, inconsistent-return-statements
    def _get_set_or_delete(self, id, operation, new_item=None):
        _check_if_has_indexable_children(self)

        # pylint: disable=access-member-before-definition,
        # pylint: disable=attribute-defined-outside-init
        if isinstance(self.children, Component):
            if getattr(self.children, "id", None) is not None:
                # Woohoo! It's the item that we're looking for
                if self.children.id == id:
                    if operation == "get":
                        return self.children
                    if operation == "set":
                        self.children = new_item
                        return
                    if operation == "delete":
                        self.children = None
                        return

            # Recursively dig into its subtree
            try:
                if operation == "get":
                    return self.children.__getitem__(id)
                if operation == "set":
                    self.children.__setitem__(id, new_item)
                    return
                if operation == "delete":
                    self.children.__delitem__(id)
                    return
            except KeyError:
                pass

        # if children is like a list
        if isinstance(self.children, (tuple, MutableSequence)):
            for i, item in enumerate(self.children):
                # If the item itself is the one we're looking for
                if getattr(item, "id", None) == id:
                    if operation == "get":
                        return item
                    if operation == "set":
                        self.children[i] = new_item
                        return
                    if operation == "delete":
                        del self.children[i]
                        return

                # Otherwise, recursively dig into that item's subtree
                # Make sure it's not like a string
                elif isinstance(item, Component):
                    try:
                        if operation == "get":
                            return item.__getitem__(id)
                        if operation == "set":
                            item.__setitem__(id, new_item)
                            return
                        if operation == "delete":
                            item.__delitem__(id)
                            return
                    except KeyError:
                        pass

        # The end of our branch
        # If we were in a list, then this exception will get caught
        raise KeyError(id)

    # Magic methods for a mapping interface:
    # - __getitem__
    # - __setitem__
    # - __delitem__
    # - __iter__
    # - __len__

    def __getitem__(self, id):  # pylint: disable=redefined-builtin
        """Recursively find the element with the given ID through the tree of
        children."""

        # A component's children can be undefined, a string, another component,
        # or a list of components.
        return self._get_set_or_delete(id, "get")

    def __setitem__(self, id, item):  # pylint: disable=redefined-builtin
        """Set an element by its ID."""
        return self._get_set_or_delete(id, "set", item)

    def __delitem__(self, id):  # pylint: disable=redefined-builtin
        """Delete items by ID in the tree of children."""
        return self._get_set_or_delete(id, "delete")

    def _traverse(self):
        """Yield each item in the tree."""
        for t in self._traverse_with_paths():
            yield t[1]

    @staticmethod
    def _id_str(component):
        id_ = stringify_id(getattr(component, "id", ""))
        return id_ and f" (id={id_:s})"

    def _traverse_with_paths(self):
        """Yield each item with its path in the tree."""
        children = getattr(self, "children", None)
        children_type = type(children).__name__
        children_string = children_type + self._id_str(children)

        # children is just a component
        if isinstance(children, Component):
            yield "[*] " + children_string, children
            # pylint: disable=protected-access
            for p, t in children._traverse_with_paths():
                yield "\n".join(["[*] " + children_string, p]), t

        # children is a list of components
        elif isinstance(children, (tuple, MutableSequence)):
            for idx, i in enumerate(children):
                list_path = f"[{idx:d}] {type(i).__name__:s}{self._id_str(i)}"
                yield list_path, i

                if isinstance(i, Component):
                    # pylint: disable=protected-access
                    for p, t in i._traverse_with_paths():
                        yield "\n".join([list_path, p]), t

    def _traverse_ids(self):
        """Yield components with IDs in the tree of children."""
        for t in self._traverse():
            if isinstance(t, Component) and getattr(t, "id", None) is not None:
                yield t

    def __iter__(self):
        """Yield IDs in the tree of children."""
        for t in self._traverse_ids():
            yield t.id

    def __len__(self):
        """Return the number of items in the tree."""
        # TODO - Should we return the number of items that have IDs
        # or just the number of items?
        # The number of items is more intuitive but returning the number
        # of IDs matches __iter__ better.
        length = 0
        if getattr(self, "children", None) is None:
            length = 0
        elif isinstance(self.children, Component):
            length = 1
            length += len(self.children)
        elif isinstance(self.children, (tuple, MutableSequence)):
            for c in self.children:
                length += 1
                if isinstance(c, Component):
                    length += len(c)
        else:
            # string or number
            length = 1
        return length

    def __repr__(self):
        # pylint: disable=no-member
        props_with_values = [
            c for c in self._prop_names if getattr(self, c, None) is not None
        ] + [
            c
            for c in self.__dict__
            if any(c.startswith(wc_attr) for wc_attr in self._valid_wildcard_attributes)
        ]
        if any(p != "children" for p in props_with_values):
            props_string = ", ".join(
                f"{p}={getattr(self, p)!r}" for p in props_with_values
            )
        else:
            props_string = repr(getattr(self, "children", None))
        return f"{self._type}({props_string})"

    def _validate_deprecation(self):
        _type = getattr(self, "_type", "")
        _ns = getattr(self, "_namespace", "")
        deprecation_message = _deprecated_components.get(_ns, {}).get(_type)
        if deprecation_message:
            warnings.warn(DeprecationWarning(textwrap.dedent(deprecation_message)))


ComponentType = typing.TypeVar("ComponentType", bound=Component)


# This wrapper adds an argument given to generated Component.__init__
# with the actual given parameters by the user as a list of string.
# This is then checked in the generated init to check if required
# props were provided.
def _explicitize_args(func):
    varnames = func.__code__.co_varnames

    def wrapper(*args, **kwargs):
        if "_explicit_args" in kwargs:
            raise Exception("Variable _explicit_args should not be set.")
        kwargs["_explicit_args"] = list(
            set(list(varnames[: len(args)]) + [k for k, _ in kwargs.items()])
        )
        if "self" in kwargs["_explicit_args"]:
            kwargs["_explicit_args"].remove("self")
        return func(*args, **kwargs)

    new_sig = inspect.signature(wrapper).replace(
        parameters=list(inspect.signature(func).parameters.values())
    )
    wrapper.__signature__ = new_sig
    return wrapper
