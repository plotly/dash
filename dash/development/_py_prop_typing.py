import collections
import json
import string
import textwrap
import importlib

from .._utils import pascal_case


shapes = {}
shape_template = """{name} = TypedDict(
    "{name}",
    {values}
)
"""
custom_imports = collections.defaultdict(lambda: collections.defaultdict(list))


def _get_custom(module_name, prop, default):
    if not module_name:
        return default
    try:
        module = importlib.import_module(module_name)
        return getattr(module, prop, default)
    except ImportError:
        return default


def get_custom_imports(module_name):
    return _get_custom(module_name, "custom_imports", {})


def get_custom_props(module_name):
    return _get_custom(module_name, "custom_props", {})


def get_custom_ignore(module_name):
    return _get_custom(module_name, "ignore_props", ["style"])


def _clean_key(key):
    k = ""
    for ch in key:
        if ch not in string.ascii_letters + "_":
            k += "_"
        else:
            k += ch
    return k


def generate_any(*_):
    return "typing.Any"


def generate_shape(type_info, component_name: str, prop_name: str):
    props = []
    name = pascal_case(prop_name)

    for prop_key, prop_type in type_info["value"].items():
        typed = get_prop_typing(
            prop_type["name"], component_name, f"{prop_name}_{prop_key}", prop_type
        )
        if not prop_type.get("required"):
            props.append(f'        "{prop_key}": NotRequired[{typed}]')
        else:
            props.append(f'        "{prop_key}": {typed}')

    shapes.setdefault(component_name, {})
    shapes[component_name][name] = textwrap.indent(
        shape_template.format(
            name=name, values="    {\n" + ",\n".join(props) + "\n    }"
        ),
        "    ",
    )

    return f'"{name}"'


def generate_union(type_info, component_name: str, prop_name: str):
    types = []
    for union in type_info["value"]:
        u_type = get_prop_typing(union["name"], component_name, prop_name, union)
        if u_type not in types:
            types.append(u_type)
    return f"typing.Union[{', '.join(types)}]"


def generate_tuple(
    type_info,
    component_name: str,
    prop_name: str,
):
    els = type_info.get("elements")
    elements = ", ".join(
        get_prop_typing(x.get("name"), component_name, prop_name, x) for x in els
    )
    return f"typing.Tuple[{elements}]"


def generate_array_of(
    type_info,
    component_name: str,
    prop_name: str,
):
    typed = get_prop_typing(
        type_info["value"]["name"], component_name, prop_name, type_info["value"]
    )
    return f"typing.Sequence[{typed}]"


def generate_object_of(type_info, component_name: str, prop_name: str):
    typed = get_prop_typing(
        type_info["value"]["name"], component_name, prop_name, type_info["value"]
    )
    return f"typing.Dict[typing.Union[str, float, int], {typed}]"


def generate_type(typename):
    def type_handler(*_):
        return typename

    return type_handler


def _get_literal_value(value):
    if isinstance(value, str):
        value = json.loads(value.replace("'", '"'))

    if value is None:
        return "None"

    if isinstance(value, bool):
        return str(value)

    return json.dumps(value)


def generate_enum(type_info, *_):
    values = [_get_literal_value(v["value"]) for v in type_info["value"] if v]
    return f"Literal[{', '.join(values)}]"


def generate_literal(type_info, *_):
    return f"Literal[{json.dumps(type_info['value'])}]"


def _get_custom_prop(custom_props, component_name, prop_name):
    customs = custom_props.get(component_name) or custom_props.get("*", {})
    return customs.get(prop_name)


def get_prop_typing(
    type_name: str,
    component_name: str,
    prop_name: str,
    type_info,
    custom_props=None,
    custom_ignore=None,
):
    if prop_name == "id":
        # Id is always the same either a string or a dict for pattern matching.
        return "typing.Union[str, dict]"

    if custom_props:
        special = _get_custom_prop(custom_props, component_name, prop_name)
        if special:
            return special(type_info, component_name, prop_name)

    if custom_ignore and prop_name in custom_ignore:
        return "typing.Any"

    prop_type = PROP_TYPING.get(type_name, generate_any)(
        type_info, component_name, prop_name
    )
    return prop_type


PROP_TYPING = {
    "array": generate_type("typing.Sequence"),
    "arrayOf": generate_array_of,
    "object": generate_type("dict"),
    "shape": generate_shape,
    "exact": generate_shape,
    "string": generate_type("str"),
    "bool": generate_type("bool"),
    "number": generate_type(
        "typing.Union[typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex]"
    ),
    "node": generate_type(
        "typing.Union[str, int, float, ComponentType,"
        " typing.Sequence[typing.Union"
        "[str, int, float, ComponentType]]]"
    ),
    "func": generate_any,
    "element": generate_type("ComponentType"),
    "union": generate_union,
    "any": generate_any,
    "custom": generate_any,
    "enum": generate_enum,
    "objectOf": generate_object_of,
    "tuple": generate_tuple,
    "literal": generate_literal,
}
