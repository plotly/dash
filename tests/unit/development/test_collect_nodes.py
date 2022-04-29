from dash.development._collect_nodes import collect_nodes

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
}


def test_dcn001_collect_nodes():
    nodes = collect_nodes(metadata)

    assert nodes == [
        "shape.node",
        "list_of_nodes",
        "[]list_of_union.b",
        "[]list_of_union",
        "[]list_of_shapes.label",
        "mixed",
        "direct",
    ]
