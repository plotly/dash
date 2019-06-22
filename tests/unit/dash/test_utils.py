import pytest

import dash._utils as utils


def test_ddut001_attribute_dict():
    a = utils.AttributeDict()

    assert str(a) == '{}'
    with pytest.raises(AttributeError):
        a.k
    with pytest.raises(KeyError):
        a['k']
    assert a.first('no', 'k', 'nope') is None

    a.k = 1

    assert a.k == 1
    assert a['k'] == 1
    assert a.first('no', 'k', 'nope') == 1

    a['k'] = 2

    assert a.k == 2
    assert a['k'] == 2

    a.set_read_only(['k', 'q'], 'boo')

    with pytest.raises(AttributeError) as err:
        a.k = 3
    assert err.value.args == ('boo', 'k')
    assert a.k == 2

    with pytest.raises(AttributeError) as err:
        a['k'] = 3
    assert err.value.args == ('boo', 'k')
    assert a.k == 2

    a.set_read_only(['q'])

    a.k = 3
    assert a.k == 3

    with pytest.raises(AttributeError) as err:
        a.q = 3
    assert err.value.args == ('Attribute is read-only', 'q')
    assert 'q' not in a

    a.finalize('nope')

    with pytest.raises(AttributeError) as err:
        a.x = 4
    assert err.value.args == ('nope', 'x')
    assert 'x' not in a

    a.finalize()

    with pytest.raises(AttributeError) as err:
        a.x = 4
    assert err.value.args == (
        'Object is final: No new keys may be added.', 'x'
    )
    assert 'x' not in a


def test_redis_dict():

    redis_kwargs = {'host': 'localhost',
                    'port': 6379}
    import redis
    r = redis.Redis(**redis_kwargs)
    r.flushdb()
    rd = utils.RedisDict(redis_kwargs)

    test_d = {'A.figure': {'in': [None, 2, 3],
                           'out': ['boo', 'fing']},
              'B.id': {'c': 'woo'}}
    for k, v in test_d.items():
        rd[k] = v

    for k, v in rd.items():
        assert k in test_d.keys()
        for (k2, v2), (k3, v3) in zip(test_d[k].items(),
                                      v.items()):
            assert k2 == k3
            for e1, e2 in zip(v2, v3):
                assert e1 == e2

    def f(x):
        return x + 2

    test_d['F'] = f

    assert f(10) == test_d['F'](10)
