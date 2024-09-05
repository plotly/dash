import pytest
import string


# A collection of fixtures for testing argument grouping-related code.  Each fixture
# returns a two-element list where the first element is the grouping data structure,
# and the second is the number of elements contained in the data structure.
@pytest.fixture
def scalar_grouping_size(request):
    return 0, 1


@pytest.fixture(params=list(range(0, 5)))
def list_grouping_size(request):
    n = request.param
    return list(range(n)), n


@pytest.fixture(params=list(range(0, 5)))
def dict_grouping_size(request):
    n = request.param
    return {string.ascii_uppercase[i]: i for i in range(n)}, n


@pytest.fixture(params=list(range(0, 5)))
def mixed_grouping_size(request):
    case = request.param
    if case == 0:
        # list of lists
        grouping = [[0, 1], 2]
        grouping_size = 3
    elif case == 1:
        # Deeply nested list of lists
        grouping = [0, [1, [2, 3], []], [], [4, [[5, [6, [7, 8]]], 9]]]
        grouping_size = 10
    elif case == 2:
        # dict of list
        grouping = {"A": [0, 1], "B": 2}
        grouping_size = 3
    elif case == 3:
        # dict of dicts
        grouping = dict(
            k0=0,
            k6=dict(k1=1, k2=dict(k3=2, k4=3), k5=[]),
            k7=[],
            k13=dict(k8=4, k9=dict(k10=dict(k11=5), k12=6)),
        )
        grouping_size = 7
    else:
        # list of mixed
        grouping = [
            dict(
                k0=0,
                k6=dict(k1=1, k2=dict(k3=2, k4=3), k5=[]),
                k7=[],
                k13=dict(k8=4, k9=[5, 6], k12=[]),
            ),
            7,
            [[8, dict(k13=[9, 10, 11], k14=dict(k15=12))], []],
        ]
        grouping_size = 13

    return grouping, grouping_size
