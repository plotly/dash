import json


class _Wildcard:  # pylint: disable=too-few-public-methods
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self._name

    def __repr__(self):
        return "<{}>".format(self)

    def to_json(self):
        # used in serializing wildcards - arrays are not allowed as
        # id values, so make the wildcards look like length-1 arrays.
        return '["{}"]'.format(self._name)


MATCH = _Wildcard("MATCH")
ALL = _Wildcard("ALL")
ALLSMALLER = _Wildcard("ALLSMALLER")


class DashDependency:  # pylint: disable=too-few-public-methods
    def __init__(self, component_id, component_property):
        self.component_id = component_id
        self.component_property = component_property

    def __str__(self):
        return "{}.{}".format(self.component_id_str(), self.component_property)

    def __repr__(self):
        return "<{} `{}`>".format(self.__class__.__name__, self)

    def component_id_str(self):
        i = self.component_id

        def _dump(v):
            return json.dumps(v, sort_keys=True, separators=(",", ":"))

        def _json(k, v):
            vstr = v.to_json() if hasattr(v, "to_json") else json.dumps(v)
            return "{}:{}".format(json.dumps(k), vstr)

        if isinstance(i, dict):
            return "{" + ",".join(_json(k, i[k]) for k in sorted(i)) + "}"

        return i

    def to_dict(self):
        return {"id": self.component_id_str(), "property": self.component_property}

    def __eq__(self, other):
        """
        We use "==" to denote two deps that refer to the same prop on
        the same component. In the case of wildcard deps, this means
        the same prop on *at least one* of the same components.
        """
        return (
            isinstance(other, DashDependency)
            and self.component_property == other.component_property
            and self._id_matches(other)
        )

    def _id_matches(self, other):
        my_id = self.component_id
        other_id = other.component_id
        self_dict = isinstance(my_id, dict)
        other_dict = isinstance(other_id, dict)

        if self_dict != other_dict:
            return False
        if self_dict:
            if set(my_id.keys()) != set(other_id.keys()):
                return False

            for k, v in my_id.items():
                other_v = other_id[k]
                if v == other_v:
                    continue
                v_wild = isinstance(v, _Wildcard)
                other_wild = isinstance(other_v, _Wildcard)
                if v_wild or other_wild:
                    if not (v_wild and other_wild):
                        continue  # one wild, one not
                    if v is ALL or other_v is ALL:
                        continue  # either ALL
                    if v is MATCH or other_v is MATCH:
                        return False  # one MATCH, one ALLSMALLER
                else:
                    return False
            return True

        # both strings
        return my_id == other_id

    def __hash__(self):
        return hash(str(self))


class Output(DashDependency):  # pylint: disable=too-few-public-methods
    """Output of a callback."""

    allowed_wildcards = (MATCH, ALL)


class Input(DashDependency):  # pylint: disable=too-few-public-methods
    """Input of callback: trigger an update when it is updated."""

    allowed_wildcards = (MATCH, ALL, ALLSMALLER)


class State(DashDependency):  # pylint: disable=too-few-public-methods
    """Use the value of a State in a callback but don't trigger updates."""

    allowed_wildcards = (MATCH, ALL, ALLSMALLER)


class ClientsideFunction:  # pylint: disable=too-few-public-methods
    def __init__(self, namespace=None, function_name=None):

        if namespace.startswith("_dashprivate_"):
            raise ValueError("Namespaces cannot start with '_dashprivate_'.")

        if namespace in ["PreventUpdate", "no_update"]:
            raise ValueError(
                '"{}" is a forbidden namespace in' " dash_clientside.".format(namespace)
            )

        self.namespace = namespace
        self.function_name = function_name

    def __repr__(self):
        return "ClientsideFunction({}, {})".format(self.namespace, self.function_name)
