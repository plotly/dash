import pytest

import dash._utils as utils


def test_ddut001_attribute_dict():
    a = utils.AttributeDict()

    assert str(a) == "{}"
    with pytest.raises(AttributeError):
        a.k
    with pytest.raises(KeyError):
        a["k"]
    assert a.first("no", "k", "nope") is None

    a.k = 1

    assert a.k == 1
    assert a["k"] == 1
    assert a.first("no", "k", "nope") == 1

    a["k"] = 2

    assert a.k == 2
    assert a["k"] == 2

    a.set_read_only(["k"], "boo")

    with pytest.raises(AttributeError) as err:
        a.k = 3
    assert err.value.args == ("boo", "k")
    assert a.k == 2
    assert a._read_only == {"k": "boo"}

    with pytest.raises(AttributeError) as err:
        a["k"] = 3
    assert err.value.args == ("boo", "k")
    assert a.k == 2

    a.set_read_only(["q"])

    with pytest.raises(AttributeError) as err:
        a.q = 3
    assert err.value.args == ("Attribute is read-only", "q")
    assert "q" not in a
    assert a._read_only == {"k": "boo", "q": "Attribute is read-only"}

    a.finalize("nope")

    with pytest.raises(AttributeError) as err:
        a.x = 4
    assert err.value.args == ("nope", "x")
    assert "x" not in a

    a.finalize()

    with pytest.raises(AttributeError) as err:
        a.x = 4
    assert err.value.args == ("Object is final: No new keys may be added.", "x")
    assert "x" not in a
