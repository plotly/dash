from __future__ import absolute_import
from __future__ import print_function

import copy
import os
import shutil
import glob
import warnings
import sys
import importlib
import uuid
import hashlib

from ._all_keywords import julia_keywords
from ._py_components_generation import reorder_props

# uuid of DashBase Julia package.
jl_dash_base_uuid = "03207cf0-e2b3-4b91-9ca8-690cf0fb507e"

# uuid of Dash Julia package. Used as base for component package uuid
jl_dash_uuid = "1b08a953-4be3-4667-9a23-3db579824955"

# Declaring longer string templates as globals to improve
# readability, make method logic clearer to anyone inspecting
# code below
jl_component_string = '''
export {funcname}

"""
    {funcname}(;kwargs...){children_signatures}

{docstring}
"""
function {funcname}(; kwargs...)
        available_props = Symbol[{component_props}]
        wild_props = Symbol[{wildcard_symbols}]
        return Component("{funcname}", "{element_name}", "{module_name}", available_props, wild_props; kwargs...)
end
{children_definitions}
'''  # noqa:E501

jl_children_signatures = """
    {funcname}(children::Any;kwargs...)
    {funcname}(children_maker::Function;kwargs...)
"""

jl_children_definitions = """
{funcname}(children::Any; kwargs...) = {funcname}(;kwargs..., children = children)
{funcname}(children_maker::Function; kwargs...) = {funcname}(children_maker(); kwargs...)
"""

jl_package_file_string = """
module {package_name}
using {base_package}

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "{version}"

{component_includes}

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "{project_shortname}",
            resources_path,
            version = version,
            [
                {resources_dist}
            ]
        )

    )
end
end
"""

jl_projecttoml_string = """
name = "{package_name}"
uuid = "{package_uuid}"
{authors}version = "{version}"

[deps]
{base_package} = "{dash_uuid}"

[compat]
julia = "1.2"
{base_package} = "{base_version}"
"""

jl_base_version = {
    "Dash": "0.1.3",
    "DashBase": "0.1",
}

jl_component_include_string = 'include("{name}.jl")'

jl_resource_tuple_string = """DashBase.Resource(
    relative_package_path = {relative_package_path},
    external_url = {external_url},
    dynamic = {dynamic},
    async = {async_string},
    type = :{type}
)"""

core_packages = ["dash_html_components", "dash_core_components", "dash_table"]


def jl_package_name(namestring):
    s = namestring.split("_")
    return "".join(w.capitalize() for w in s)


def stringify_wildcards(wclist, no_symbol=False):
    if no_symbol:
        wcstring = "|".join("{}-".format(item) for item in wclist)
    else:
        wcstring = ", ".join('Symbol("{}-")'.format(item) for item in wclist)
    return wcstring


def get_wildcards_jl(props):
    return [key.replace("-*", "") for key in props if key.endswith("-*")]


def get_jl_prop_types(type_object):
    """Mapping from the PropTypes js type object to the Julia type."""

    def shape_or_exact():
        return "lists containing elements {}.\n{}".format(
            ", ".join("'{}'".format(t) for t in type_object["value"]),
            "Those elements have the following types:\n{}".format(
                "\n".join(
                    create_prop_docstring_jl(
                        prop_name=prop_name,
                        type_object=prop,
                        required=prop["required"],
                        description=prop.get("description", ""),
                        indent_num=1,
                    )
                    for prop_name, prop in type_object["value"].items()
                )
            ),
        )

    return dict(
        array=lambda: "Array",
        bool=lambda: "Bool",
        number=lambda: "Real",
        string=lambda: "String",
        object=lambda: "Dict",
        any=lambda: "Bool | Real | String | Dict | Array",
        element=lambda: "dash component",
        node=lambda: "a list of or a singular dash component, string or number",
        # React's PropTypes.oneOf
        enum=lambda: "a value equal to: {}".format(
            ", ".join("{}".format(str(t["value"])) for t in type_object["value"])
        ),
        # React's PropTypes.oneOfType
        union=lambda: "{}".format(
            " | ".join(
                "{}".format(get_jl_type(subType))
                for subType in type_object["value"]
                if get_jl_type(subType) != ""
            )
        ),
        # React's PropTypes.arrayOf
        arrayOf=lambda: (
            "Array"
            + (
                " of {}s".format(get_jl_type(type_object["value"]))
                if get_jl_type(type_object["value"]) != ""
                else ""
            )
        ),
        # React's PropTypes.objectOf
        objectOf=lambda: ("Dict with Strings as keys and values of type {}").format(
            get_jl_type(type_object["value"])
        ),
        # React's PropTypes.shape
        shape=shape_or_exact,
        # React's PropTypes.exact
        exact=shape_or_exact,
    )


def filter_props(props):
    """Filter props from the Component arguments to exclude:
        - Those without a "type" or a "flowType" field
        - Those with arg.type.name in {'func', 'symbol', 'instanceOf'}
    Parameters
    ----------
    props: dict
        Dictionary with {propName: propMetadata} structure
    Returns
    -------
    dict
        Filtered dictionary with {propName: propMetadata} structure
    """
    filtered_props = copy.deepcopy(props)

    for arg_name, arg in list(filtered_props.items()):
        if "type" not in arg and "flowType" not in arg:
            filtered_props.pop(arg_name)
            continue

        # Filter out functions and instances --
        if "type" in arg:  # These come from PropTypes
            arg_type = arg["type"]["name"]
            if arg_type in {"func", "symbol", "instanceOf"}:
                filtered_props.pop(arg_name)
        elif "flowType" in arg:  # These come from Flow & handled differently
            arg_type_name = arg["flowType"]["name"]
            if arg_type_name == "signature":
                # This does the same as the PropTypes filter above, but "func"
                # is under "type" if "name" is "signature" vs just in "name"
                if "type" not in arg["flowType"] or arg["flowType"]["type"] != "object":
                    filtered_props.pop(arg_name)
        else:
            raise ValueError

    return filtered_props


def get_jl_type(type_object):
    """
    Convert JS types to Julia types for the component definition
    Parameters
    ----------
    type_object: dict
        react-docgen-generated prop type dictionary
    Returns
    -------
    str
        Julia type string
    """
    js_type_name = type_object["name"]
    js_to_jl_types = get_jl_prop_types(type_object=type_object)
    if js_type_name in js_to_jl_types:
        prop_type = js_to_jl_types[js_type_name]()
        return prop_type
    return ""


def print_jl_type(typedata):
    typestring = get_jl_type(typedata).capitalize()
    if typestring:
        typestring += ". "
    return typestring


def create_docstring_jl(component_name, props, description):
    """Create the Dash component docstring.
    Parameters
    ----------
    component_name: str
        Component name
    props: dict
        Dictionary with {propName: propMetadata} structure
    description: str
        Component description
    Returns
    -------
    str
        Dash component docstring
    """
    # Ensure props are ordered with children first
    props = reorder_props(props=props)

    return ("A{n} {name} component.\n{description}\nKeyword arguments:\n{args}").format(
        n="n" if component_name[0].lower() in "aeiou" else "",
        name=component_name,
        description=description,
        args="\n".join(
            create_prop_docstring_jl(
                prop_name=p,
                type_object=prop["type"] if "type" in prop else prop["flowType"],
                required=prop["required"],
                description=prop["description"],
                indent_num=0,
            )
            for p, prop in filter_props(props).items()
        ),
    )


def create_prop_docstring_jl(
    prop_name, type_object, required, description, indent_num,
):
    """
    Create the Dash component prop docstring
    Parameters
    ----------
    prop_name: str
        Name of the Dash component prop
    type_object: dict
        react-docgen-generated prop type dictionary
    required: bool
        Component is required?
    description: str
        Dash component description
    indent_num: int
        Number of indents to use for the context block
        (creates 2 spaces for every indent)
    is_flow_type: bool
        Does the prop use Flow types? Otherwise, uses PropTypes
    Returns
    -------
    str
        Dash component prop docstring
    """
    jl_type_name = get_jl_type(type_object=type_object)

    indent_spacing = "  " * indent_num
    if "\n" in jl_type_name:
        return (
            "{indent_spacing}- `{name}` ({is_required}): {description}. "
            "{name} has the following type: {type}".format(
                indent_spacing=indent_spacing,
                name=prop_name,
                type=jl_type_name,
                description=description,
                is_required="required" if required else "optional",
            )
        )
    return "{indent_spacing}- `{name}` ({type}{is_required}){description}".format(
        indent_spacing=indent_spacing,
        name=prop_name,
        type="{}; ".format(jl_type_name) if jl_type_name else "",
        description=(": {}".format(description) if description != "" else ""),
        is_required="required" if required else "optional",
    )


# this logic will permit passing blank Julia prefixes to
# dash-generate-components, while also enforcing
# lower case names for the resulting functions; if a prefix
# is supplied, leave it as-is
def format_fn_name(prefix, name):
    if prefix:
        return "{}_{}".format(prefix, name.lower())
    return name.lower()


def generate_metadata_strings(resources, metatype):
    def nothing_or_string(v):
        return '"{}"'.format(v) if v else "nothing"

    return [
        jl_resource_tuple_string.format(
            relative_package_path=nothing_or_string(
                resource.get("relative_package_path", "")
            ),
            external_url=nothing_or_string(resource.get("external_url", "")),
            dynamic=str(resource.get("dynamic", "nothing")).lower(),
            type=metatype,
            async_string=":{}".format(str(resource.get("async")).lower())
            if "async" in resource.keys()
            else "nothing",
        )
        for resource in resources
    ]


def is_core_package(project_shortname):
    return project_shortname in core_packages


def base_package_name(project_shortname):
    return "DashBase" if is_core_package(project_shortname) else "Dash"


def base_package_uid(project_shortname):
    return jl_dash_base_uuid if is_core_package(project_shortname) else jl_dash_uuid


def generate_package_file(project_shortname, components, pkg_data, prefix):
    package_name = jl_package_name(project_shortname)

    sys.path.insert(0, os.getcwd())
    mod = importlib.import_module(project_shortname)
    js_dist = getattr(mod, "_js_dist", [])
    css_dist = getattr(mod, "_css_dist", [])
    project_ver = pkg_data.get("version")

    resources_dist = ",\n".join(
        generate_metadata_strings(js_dist, "js")
        + generate_metadata_strings(css_dist, "css")
    )

    package_string = jl_package_file_string.format(
        package_name=package_name,
        component_includes="\n".join(
            [
                jl_component_include_string.format(
                    name=format_fn_name(prefix, comp_name)
                )
                for comp_name in components
            ]
        ),
        resources_dist=resources_dist,
        version=project_ver,
        project_shortname=project_shortname,
        base_package=base_package_name(project_shortname),
    )
    file_path = os.path.join("src", package_name + ".jl")
    with open(file_path, "w") as f:
        f.write(package_string)
    print("Generated {}".format(file_path))


def generate_toml_file(project_shortname, pkg_data):
    package_author = pkg_data.get("author", "")
    project_ver = pkg_data.get("version")
    package_name = jl_package_name(project_shortname)
    u = uuid.UUID(jl_dash_uuid)

    package_uuid = uuid.UUID(
        hex=u.hex[:-12] + hashlib.md5(package_name.encode("utf-8")).hexdigest()[-12:]
    )

    authors_string = (
        'authors = ["{}"]\n'.format(package_author) if package_author else ""
    )

    base_package = base_package_name(project_shortname)

    toml_string = jl_projecttoml_string.format(
        package_name=package_name,
        package_uuid=package_uuid,
        version=project_ver,
        authors=authors_string,
        base_package=base_package,
        base_version=jl_base_version[base_package],
        dash_uuid=base_package_uid(project_shortname),
    )
    file_path = "Project.toml"
    with open(file_path, "w") as f:
        f.write(toml_string)
    print("Generated {}".format(file_path))


def generate_class_string(name, props, description, project_shortname, prefix):
    # Ensure props are ordered with children first
    filtered_props = reorder_props(filter_props(props))

    prop_keys = list(filtered_props.keys())

    docstring = (
        create_docstring_jl(
            component_name=name, props=filtered_props, description=description
        )
        .replace("\r\n", "\n")
        .replace("$", "\\$")
    )

    wclist = get_wildcards_jl(props)
    default_paramtext = ""

    # Filter props to remove those we don't want to expose
    for item in prop_keys[:]:
        if item.endswith("-*") or item == "setProps":
            prop_keys.remove(item)
        elif item in julia_keywords:
            prop_keys.remove(item)
            warnings.warn(
                (
                    'WARNING: prop "{}" in component "{}" is a Julia keyword'
                    " - REMOVED FROM THE JULIA COMPONENT"
                ).format(item, name)
            )

    default_paramtext += ", ".join(":{}".format(p) for p in prop_keys)

    has_children = "children" in prop_keys
    funcname = format_fn_name(prefix, name)
    children_signatures = (
        jl_children_signatures.format(funcname=funcname) if has_children else ""
    )
    children_definitions = (
        jl_children_definitions.format(funcname=funcname) if has_children else ""
    )
    return jl_component_string.format(
        funcname=format_fn_name(prefix, name),
        docstring=docstring,
        component_props=default_paramtext,
        wildcard_symbols=stringify_wildcards(wclist, no_symbol=False),
        wildcard_names=stringify_wildcards(wclist, no_symbol=True),
        element_name=name,
        module_name=project_shortname,
        children_signatures=children_signatures,
        children_definitions=children_definitions,
    )


def generate_struct_file(name, props, description, project_shortname, prefix):
    props = reorder_props(props=props)
    import_string = "# AUTO GENERATED FILE - DO NOT EDIT\n"
    class_string = generate_class_string(
        name, props, description, project_shortname, prefix
    )

    file_name = format_fn_name(prefix, name) + ".jl"

    file_path = os.path.join("src", file_name)
    with open(file_path, "w") as f:
        f.write(import_string)
        f.write(class_string)

    print("Generated {}".format(file_name))


# pylint: disable=unused-argument
def generate_module(
    project_shortname, components, metadata, pkg_data, prefix, **kwargs
):
    # the Julia source directory for the package won't exist on first call
    # create the Julia directory if it is missing
    if not os.path.exists("src"):
        os.makedirs("src")

    # now copy over all JS dependencies from the (Python) components dir
    # the inst/lib directory for the package won't exist on first call
    # create this directory if it is missing
    if os.path.exists("deps"):
        shutil.rmtree("deps")

    os.makedirs("deps")

    for javascript in glob.glob("{}/*.js".format(project_shortname)):
        shutil.copy(javascript, "deps/")

    for css in glob.glob("{}/*.css".format(project_shortname)):
        shutil.copy(css, "deps/")

    for sourcemap in glob.glob("{}/*.map".format(project_shortname)):
        shutil.copy(sourcemap, "deps/")

    generate_package_file(project_shortname, components, pkg_data, prefix)
    generate_toml_file(project_shortname, pkg_data)
