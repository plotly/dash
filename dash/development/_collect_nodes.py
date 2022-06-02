def is_node(value):
    return value in ("node", "element")


def is_shape(value):
    return value in ("shape", "exact")


def collect_array(a_value, base, nodes):
    a_type = a_value["name"]
    if is_node(a_type):
        nodes.append(base)
    elif a_type in ("shape", "exact"):
        nodes = collect_nodes(a_value["value"], base + "[]", nodes)
    elif a_type == "union":
        nodes = collect_union(a_value["value"], base + "[]", nodes)
    return nodes


def collect_union(type_list, base, nodes):
    for t in type_list:
        if is_node(t["name"]):
            nodes.append(base)
        elif is_shape(t["name"]):
            nodes = collect_nodes(t["value"], base, nodes)
        elif t["name"] == "arrayOf":
            nodes = collect_array(t["value"], base, nodes)
    return nodes


def collect_nodes(metadata, base="", nodes=None):
    nodes = nodes or []

    for prop_name, value in metadata.items():
        # Support for recursive shapes, the type is directly in the field.
        t_value = value.get("type", value)
        p_type = t_value.get("name")

        if base:
            key = f"{base}.{prop_name}"
        else:
            key = prop_name
        if is_node(p_type):
            nodes.append(key)
        elif p_type == "arrayOf":
            a_value = t_value.get("value", t_value)
            nodes = collect_array(a_value, key, nodes)
        elif is_shape(p_type):
            nodes = collect_nodes(t_value["value"], key, nodes)
        elif p_type == "union":
            nodes = collect_union(t_value["value"], key, nodes)

    return nodes


def filter_base_nodes(nodes):
    return [n for n in nodes if not any(e in n for e in ("[]", "."))]
