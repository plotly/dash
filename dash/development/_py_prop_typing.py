def generate_any(_):
    return "typing.Any"


def generate_shape(t):
    props = []

    for prop in t["value"].values():
        prop_type = PROP_TYPING.get(prop["name"], generate_any)(prop)
        if prop_type not in props:
            props.append(prop_type)

    if len(props) == 0:
        return "typing.Any"

    return f"typing.Dict[str, typing.Union[{', '.join(props)}]]"


def generate_union(t):
    types = []
    for union in t["value"]:
        u_type = PROP_TYPING.get(union["name"], generate_any)(union)
        if u_type not in types:
            types.append(u_type)
    return f"typing.Union[{', '.join(types)}]"


def generate_tuple(type_info):
    els = type_info.get("elements")
    elements = ", ".join(get_prop_typing(x.get("name"), x) for x in els)
    return f"typing.Tuple[{elements}]"


def generate_array_of(t):
    typed = PROP_TYPING.get(t["value"]["name"], generate_any)(t["value"])
    return f"typing.List[{typed}]"


def generate_object_of(t):
    typed = PROP_TYPING.get(t["value"]["name"], generate_any)(t["value"])
    return f"typing.Dict[typing.Union[str, float, int], {typed}]"


def generate_type(typename):
    def type_handler(_):
        return typename

    return type_handler


def get_prop_typing(type_name: str, type_info):
    return PROP_TYPING.get(type_name, generate_any)(type_info)


PROP_TYPING = {
    "array": generate_type("typing.List"),
    "arrayOf": generate_array_of,
    "object": generate_type("typing.Dict"),
    "shape": generate_shape,
    "exact": generate_shape,
    "string": generate_type("str"),
    "bool": generate_type("bool"),
    "number": generate_type("numbers.Number"),
    "node": generate_type(
        "typing.Union[str, int, float, Component,"
        " typing.List[typing.Union"
        "[str, int, float, Component]]]"
    ),
    "func": generate_any,
    "element": generate_type("Component"),
    "union": generate_union,
    "any": generate_any,
    "custom": generate_any,
    "enum": generate_any,
    "objectOf": generate_object_of,
    "tuple": generate_tuple,
}
