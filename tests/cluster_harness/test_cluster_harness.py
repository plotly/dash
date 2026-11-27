"""ClusterSharedStorage across real containers: scaling, failover, partitions.

Opt in, it starts containers:

    DASH_CLUSTER_HARNESS=1 pytest tests/cluster_harness -s
    DASH_CLUSTER_HARNESS=1 HARNESS_QUORUM=3 pytest tests/cluster_harness -s
    DASH_CLUSTER_HARNESS=1 HARNESS_TLS=1 pytest tests/cluster_harness -s

Tests run in file order and share one cluster, each leaves it settled.
"""
import os
import time

import pytest

from .harness import Cluster

pytestmark = pytest.mark.skipif(
    os.environ.get("DASH_CLUSTER_HARNESS") != "1",
    reason="starts containers, set DASH_CLUSTER_HARNESS=1",
)

QUORUM = int(os.environ.get("HARNESS_QUORUM", "0")) or None
TLS = os.environ.get("HARNESS_TLS") == "1"
SIZE = QUORUM or 3
majority_only = pytest.mark.skipif(not QUORUM, reason="majority mode only")
no_majority = pytest.mark.skipif(
    bool(QUORUM), reason="majority mode needs a fixed replica count"
)


@pytest.fixture(scope="module")
def cluster():
    c = Cluster(quorum=QUORUM, tls=TLS)
    try:
        c.up(SIZE)
        yield c
    finally:
        if os.environ.get("HARNESS_KEEP") != "1":
            c.down()


def wait_for(what, check, timeout=60):
    t0 = time.monotonic()
    last = None
    while time.monotonic() - t0 < timeout:
        try:
            last = check()
            if last is True:
                return time.monotonic() - t0
        except Exception as err:  # pylint: disable=broad-except
            last = err
        time.sleep(0.3)
    raise AssertionError(f"{what} after {timeout}s, last: {last!r}")


def write(cluster, index, key, value):
    # Wait out the backend's own retries: a write the test gave up on would
    # still land later and overwrite the next one.
    res = cluster.post(index, f"/kv/{key}", {"value": value}, timeout=150)
    return res["status"] == 200


def reads(cluster, indexes, key, value):
    return all(
        res["value"] == value
        for index in indexes
        for res in cluster.every_worker(index, f"/kv/{key}").values()
    )


def test_cold_start_agrees_on_one_owner(cluster):
    owner, _token, roles = cluster.settled()
    print(f"owner: replica {owner}")
    # Each replica holds its own lock once, shared by its workers.
    assert sum(r["holds_lock"] for r in roles.values()) == SIZE


def test_writes_reach_every_replica_and_worker(cluster):
    assert write(cluster, 2, "a", {"from": 2})
    assert reads(cluster, cluster.indexes(), "a", {"from": 2})


def test_pubsub_across_replicas(cluster):
    assert cluster.post(1, "/pub/t", {"message": "x"})["status"] == 200
    assert cluster.post(3, "/pub/t", {"message": "y"})["status"] == 200
    res = cluster.get(2, "/poll/t?from=0")["body"]
    assert res["pairs"] == [[1, "x"], [2, "y"]], res


@no_majority
def test_scale_up_keeps_the_owner_and_the_data(cluster):
    owner, token, _ = cluster.settled()
    cluster.scale(SIZE + 2)
    new_owner, new_token, _ = cluster.settled()
    assert (new_owner, new_token) == (owner, token)
    assert reads(cluster, cluster.indexes(), "a", {"from": 2})


@no_majority
def test_scale_down_keeps_serving(cluster):
    cluster.scale(SIZE)
    cluster.settled()
    assert write(cluster, cluster.indexes()[0], "b", 1)
    assert reads(cluster, cluster.indexes(), "b", 1)


def test_killing_the_owner_fails_over(cluster):
    owner, token, _ = cluster.settled()
    cluster.kill(owner)
    cluster.remove(owner)
    rest = cluster.indexes()
    took = wait_for(
        "no failover",
        lambda: write(cluster, rest[0], "c", 2) and reads(cluster, rest, "c", 2),
    )
    print(f"failover {took:.1f}s after killing replica {owner}")
    _owner, new_token, _ = cluster.settled()
    assert new_token != token
    cluster.scale(SIZE)
    cluster.settled()


def test_frozen_owner_is_replaced(cluster):
    owner, token, _ = cluster.settled()
    rest = [i for i in cluster.indexes() if i != owner]
    cluster.pause(owner)
    try:
        took = wait_for(
            "no takeover from a frozen owner",
            lambda: write(cluster, rest[0], "d", "majority")
            and reads(cluster, rest, "d", "majority"),
        )
        print(f"took over {took:.1f}s after freezing replica {owner}")
    finally:
        cluster.unpause(owner)
    _owner, new_token, _ = cluster.settled(timeout=90)
    if QUORUM:
        # The old owner's lease ran out while frozen: nothing it held wins.
        assert new_token != token
        assert reads(cluster, cluster.indexes(), "d", "majority")
    # Without a majority the older owner wins the merge when it wakes up,
    # and what the others wrote meanwhile is gone (a SharedStorageGap).


@majority_only
def test_cut_off_owner_refuses_writes_and_rejoins(cluster):
    owner, _token, _ = cluster.settled()
    rest = [i for i in cluster.indexes() if i != owner]
    cluster.cut(owner)
    took = wait_for(
        "the majority never took over",
        lambda: write(cluster, rest[0], "e", "majority")
        and reads(cluster, rest, "e", "majority"),
    )
    print(f"majority took over {took:.1f}s after the cut")
    for _ in range(cluster.workers):
        t0 = time.monotonic()
        res = cluster.post(owner, "/kv/e", {"value": "lost"}, timeout=180)
        assert res["status"] == 500, res
        print(f"cut-off replica refused a write after {time.monotonic() - t0:.1f}s")
    cluster.heal(owner)
    took = wait_for(
        "the cut-off replica never rejoined",
        lambda: reads(cluster, cluster.indexes(), "e", "majority"),
        timeout=120,
    )
    print(f"rejoined {took:.1f}s after healing")
    cluster.settled()


@no_majority
def test_cut_off_owner_converges_after_healing(cluster):
    # Without a majority both sides own for a while; after healing they
    # merge back to one owner, and its store must not change on its own.
    owner, token, _ = cluster.settled()
    rest = [i for i in cluster.indexes() if i != owner]
    assert reads(cluster, [rest[0]], "f", None)  # connects both workers
    cluster.cut(owner)
    # The first try goes to the cut-off owner and times out, the retry
    # lands on the new one.
    assert write(cluster, rest[0], "f", 1)
    cluster.heal(owner)
    _owner, merged, _ = cluster.settled(timeout=90)
    # The older store wins: the cut-off owner's, where "f" was never set.
    expected = None if merged == token else 1
    t0 = time.monotonic()
    while time.monotonic() - t0 < 45:
        # A write the client gave up on, still queued in the kernel, would
        # reach the old owner once the network heals and land here late.
        assert reads(cluster, cluster.indexes(), "f", expected)
        time.sleep(1)
    assert write(cluster, owner, "f", 2)
    assert reads(cluster, cluster.indexes(), "f", 2)


def test_rolling_restart(cluster):
    for index in list(cluster.indexes()):
        cluster.remove(index)
        cluster.scale(SIZE)
        cluster.settled(timeout=90)
    indexes = cluster.indexes()
    assert write(cluster, indexes[0], "g", "after")
    assert reads(cluster, indexes, "g", "after")


def test_scale_to_zero_and_back(cluster):
    cluster.scale(0)
    assert not cluster.indexes()
    cluster.scale(SIZE)
    cluster.settled()
    indexes = cluster.indexes()
    # Nothing outlives the last replica without path= on a shared volume.
    assert reads(cluster, indexes, "g", None)
    assert write(cluster, indexes[-1], "h", 1)
    assert reads(cluster, indexes, "h", 1)
