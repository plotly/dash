import json

import pytest

from dash import Patch
from dash._utils import to_json


def patch_to_dict(p):
    return json.loads(to_json(p))


def test_pat001_patch_assign_item():
    p = Patch()
    p["item"] = "assigned"

    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Assign",
        "location": ["item"],
        "params": {"value": "assigned"},
    }


def test_pat002_patch_assign_attr():
    p = Patch()
    p.item = "assigned"

    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Assign",
        "location": ["item"],
        "params": {"value": "assigned"},
    }


def test_pat003_patch_multi_operations():
    p = Patch()
    p.one = 1
    p.two = 2

    data = patch_to_dict(p)

    assert len(data["operations"]) == 2
    assert data["operations"][0]["location"] == ["one"]
    assert data["operations"][1]["location"] == ["two"]


def test_pat004_patch_nested_assign():
    p = Patch()

    p["nest_item"]["nested"]["deep"] = "deep"
    p.nest_attr.nested.deep = "deep"

    data = patch_to_dict(p)

    assert data["operations"][0]["location"] == ["nest_item", "nested", "deep"]
    assert data["operations"][1]["location"] == ["nest_attr", "nested", "deep"]


def test_pat005_patch_delete_item():
    p = Patch()

    del p["delete_me"]

    data = patch_to_dict(p)

    assert data["operations"][0]["operation"] == "Delete"
    assert data["operations"][0]["location"] == ["delete_me"]


def test_pat006_patch_delete_attr():
    p = Patch()

    del p.delete_me

    data = patch_to_dict(p)

    assert data["operations"][0]["operation"] == "Delete"
    assert data["operations"][0]["location"] == ["delete_me"]


def test_pat007_patch_append():
    p = Patch()
    p.append("item")
    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Append",
        "location": [],
        "params": {"value": "item"},
    }


def test_pat008_patch_prepend():
    p = Patch()
    p.prepend("item")
    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Prepend",
        "location": [],
        "params": {"value": "item"},
    }


def test_pat009_patch_extend():
    p = Patch()
    p.extend(["extend"])
    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Extend",
        "location": [],
        "params": {"value": ["extend"]},
    }


def test_pat010_patch_merge():
    p = Patch()
    p.update({"merge": "merged"})

    p["merge"] |= {"ior": "iored"}
    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Merge",
        "location": [],
        "params": {"value": {"merge": "merged"}},
    }
    assert data["operations"][1] == {
        "operation": "Merge",
        "location": ["merge"],
        "params": {"value": {"ior": "iored"}},
    }


def test_pat011_patch_add():
    p = Patch()
    p.plusplus += 1

    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Add",
        "location": ["plusplus"],
        "params": {"value": 1},
    }


def test_pat012_patch_sub():
    p = Patch()
    p.minusless -= 1

    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Sub",
        "location": ["minusless"],
        "params": {"value": 1},
    }


def test_pat013_patch_mul():
    p = Patch()
    p.mulby *= 2

    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Mul",
        "location": ["mulby"],
        "params": {"value": 2},
    }


def test_pat014_patch_div():
    p = Patch()
    p.divby /= 2

    data = patch_to_dict(p)

    assert data["operations"][0] == {
        "operation": "Div",
        "location": ["divby"],
        "params": {"value": 2},
    }


def test_pat015_patch_insert():
    p = Patch()
    p.insert(1, "inserted")

    data = patch_to_dict(p)
    assert data["operations"][0] == {
        "operation": "Insert",
        "location": [],
        "params": {"index": 1, "value": "inserted"},
    }


def test_pat016_patch_slice():
    p = Patch()

    with pytest.raises(TypeError):
        p[2::1] = "sliced"

    with pytest.raises(TypeError):
        p[2:3]["nested"] = "nest-slice"

    with pytest.raises(TypeError):
        del p[1:]


def test_pat017_patch_clear():
    p = Patch()

    p.clear()
    data = patch_to_dict(p)
    assert data["operations"][0] == {"operation": "Clear", "location": [], "params": {}}


def test_pat018_patch_reverse():
    p = Patch()

    p.reverse()
    data = patch_to_dict(p)
    assert data["operations"][0] == {
        "operation": "Reverse",
        "location": [],
        "params": {},
    }


def test_pat019_patch_remove():
    p = Patch()

    p.remove("item")
    data = patch_to_dict(p)
    assert data["operations"][0] == {
        "operation": "Remove",
        "location": [],
        "params": {"value": "item"},
    }


def test_pat020_patch_pickle():
    import pickle

    p = Patch()
    p["a"] = "a"
    data = pickle.dumps(p)
    q = pickle.loads(data)

    assert patch_to_dict(p) == patch_to_dict(q)


def test_pat021_patch_iter():
    p = Patch()

    with pytest.raises(TypeError):
        for _ in p["invalid"]:
            print("invalid iteration")


def test_pat022_patch_update_shared_mapping():
    common = {"currency": "USD"}
    p = Patch()
    p["jan"].update(common, amount=100)
    p["feb"].update(common, amount=200)

    assert patch_to_dict(p)["operations"] == [
        {
            "operation": "Merge",
            "location": ["jan"],
            "params": {"value": {"currency": "USD", "amount": 100}},
        },
        {
            "operation": "Merge",
            "location": ["feb"],
            "params": {"value": {"currency": "USD", "amount": 200}},
        },
    ]
    assert common == {"currency": "USD"}


def test_pat023_patch_update_keywords_and_shallow_values():
    nested = {"retained": 1}
    common = {"amount": 0, "nested": nested}
    p = Patch()
    p.update(common, amount=100)

    value = p.to_plotly_json()["operations"][0]["params"]["value"]
    assert value == {"amount": 100, "nested": {"retained": 1}}
    assert value["nested"] is nested
    assert common == {"amount": 0, "nested": {"retained": 1}}


@pytest.mark.parametrize("args", [(), (None,), ({},)])
@pytest.mark.parametrize("kwargs", [{}, {"currency": "USD"}])
def test_pat024_patch_update_empty(args, kwargs):
    p = Patch()
    p.update(*args, **kwargs)

    assert patch_to_dict(p)["operations"] == [
        {"operation": "Merge", "location": [], "params": {"value": kwargs}}
    ]


def test_pat025_patch_update_union():
    common = {"currency": "USD"}
    p = Patch()
    p |= common
    p["jan"] |= common

    assert patch_to_dict(p)["operations"] == [
        {
            "operation": "Merge",
            "location": [],
            "params": {"value": {"currency": "USD"}},
        },
        {
            "operation": "Merge",
            "location": ["jan"],
            "params": {"value": {"currency": "USD"}},
        },
    ]
    assert common == {"currency": "USD"}
