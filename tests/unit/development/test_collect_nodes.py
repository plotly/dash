from dash.development._collect_nodes import collect_nodes, filter_base_nodes

metadata = {
    "string": {"type": {"name": "string"}},
    "shape": {
        "type": {
            "name": "shape",
            "value": {
                "single": {"type": {"name": "number"}},
                "node": {"type": {"name": "node"}},
            },
        }
    },
    "list_of_nodes": {
        "type": {"name": "arrayOf", "value": {"name": "node"}},
    },
    "list_of_union": {
        "type": {
            "name": "arrayOf",
            "value": {
                "name": "union",
                "value": [
                    {
                        "name": "shape",
                        "value": {
                            "a": {"type": {"name": "string"}},
                            "b": {"type": {"name": "element"}},
                        },
                    },
                    {"name": "node"},
                ],
            },
        }
    },
    "list_of_shapes": {
        "type": {
            "name": "arrayOf",
            "value": {
                "name": "shape",
                "value": {"label": {"name": "node"}, "value": {"name": "string"}},
            },
        }
    },
    "mixed": {
        "type": {"name": "union", "value": [{"name": "number"}, {"name": "element"}]}
    },
    "direct": {"type": {"name": "node"}},
    "nested_list": {
        "type": {
            "name": "shape",
            "value": {
                "list": {
                    "type": {
                        "name": "arrayOf",
                        "value": {
                            "name": "shape",
                            "value": {"component": {"name": "node"}},
                        },
                    }
                }
            },
        }
    },
    "dynamic": {
        "type": {"name": "objectOf", "value": {"name": "node"}},
    },
    "dynamic_list": {
        "type": {
            "name": "arrayOf",
            "value": {"name": "objectOf", "value": {"name": "node"}},
        }
    },
    "dynamic_node_in_dict": {
        "type": {
            "name": "shape",
            "value": {"a": {"name": "objectOf", "value": {"name": "node"}}},
        }
    },
    "dynamic_in_object": {
        "type": {
            "name": "objectOf",
            "value": {
                "name": "shape",
                "value": {
                    "a": {
                        "name": "node",
                    }
                },
            },
        }
    },
}


def test_dcn001_collect_nodes():
    nodes = collect_nodes(metadata)

    assert nodes == [
        "shape.node",
        "list_of_nodes",
        "list_of_union[].b",
        "list_of_union[]",
        "list_of_shapes[].label",
        "mixed",
        "direct",
        "nested_list.list[].component",
        "dynamic{}",
        "dynamic_list[]{}",
        "dynamic_node_in_dict.a{}",
        "dynamic_in_object{}.a",
    ]


def test_dcn002_base_nodes():
    nodes = collect_nodes(metadata)

    assert filter_base_nodes(nodes) == ["list_of_nodes", "mixed", "direct"]
