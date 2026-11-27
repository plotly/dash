# Cluster harness

Runs `ClusterSharedStorage` replicas as real containers (docker or podman) so
you can scale them, kill, freeze or cut off the owner, and watch what the
cluster does. Each replica runs `gunicorn -w 2` on this checkout's source,
mounted read only, so edits take effect on the next `up` or `scale`.

## Requirements

- docker, or podman 4+ (netavark and aardvark-dns, the default since 4.0).
  Rootless podman works: the harness reaches replicas with `exec`, never by IP.
- Built components in the checkout (`dash/dcc/_imports_.py` must exist).
- `openssl` for `--tls`.
- The first `up` builds `dash-cluster-harness` from `python:3.12-slim`, so the
  engine needs to reach a registry and PyPI once. `HARNESS_IMAGE=<image>`
  skips the build and uses an image you already have instead (it needs
  python3, gunicorn and the packages in `requirements/install.txt` and
  `requirements/shared_storage.txt`; without msgspec the store silently
  falls back to JSON). With rootless podman and an image that runs as a
  non-root user, the mounts may need `--userns=keep-id`.
- `CLUSTER_ENGINE=podman` picks podman when both are installed.

## By hand

```
python tests/cluster_harness/harness.py up 3            # 3 replicas, started together
python tests/cluster_harness/harness.py up 3 --quorum 3 # majority mode
python tests/cluster_harness/harness.py up 3 --tls --publish  # replica i on localhost:8050+i
python tests/cluster_harness/harness.py status          # role and token per worker
python tests/cluster_harness/harness.py scale 5
python tests/cluster_harness/harness.py kill 1          # also: pause, unpause, cut, heal, rm, logs
python tests/cluster_harness/harness.py down
```

`cut` takes a replica off the network (a partition), `heal` puts it back
under the shared DNS name. `pause` freezes it like a long GC or a stalled VM.

## Tests

They start containers, so they only run when asked:

```
DASH_CLUSTER_HARNESS=1 pytest tests/cluster_harness -s
DASH_CLUSTER_HARNESS=1 HARNESS_QUORUM=3 pytest tests/cluster_harness -s
DASH_CLUSTER_HARNESS=1 HARNESS_TLS=1 pytest tests/cluster_harness -s
```

`HARNESS_KEEP=1` leaves the cluster running afterwards. Majority mode skips
the scale tests (its replica count is fixed) and the base mode skips the
"cut-off owner refuses writes" test (without a majority it doesn't).
