"""Pick a shared-storage backend from ``DASH_SHARED_STORAGE``.

Lets a hosting platform switch backends without editing the app's ``Dash(...)``
call. Only used when the app did not pass ``shared_storage=``.
"""

import functools
import os
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl, unquote, urlencode, urlparse

from ..exceptions import InvalidConfig
from .cluster import DEFAULT_PORT, SECRET_ENV, ClusterSharedStorage
from .diskcache import DiskcacheSharedStorage, _require_diskcache
from .local import LocalSharedStorage
from .redis import RedisSharedStorage, _require_redis

ENV_VAR = "DASH_SHARED_STORAGE"


def _invalid(reason: str) -> InvalidConfig:
    # The value can hold credentials, so it stays out of the message.
    return InvalidConfig(
        f"{ENV_VAR} is not valid: {reason}. Use 'local', 'none', "
        "'diskcache:///absolute/path', a redis:// or rediss:// URL, or "
        "cluster://host[:port]."
    )


def _redis_from_url(raw: str) -> Any:
    parsed = urlparse(raw)
    query = parse_qsl(parsed.query, keep_blank_values=True)
    kwargs: Dict[str, Any] = {}
    rest = []
    for key, value in query:
        if key == "key_prefix":
            if not value:
                raise _invalid("key_prefix cannot be empty")
            kwargs["key_prefix"] = value
        else:
            rest.append((key, value))
    url = parsed._replace(query=urlencode(rest)).geturl()
    return functools.partial(RedisSharedStorage, url=url, **kwargs)


def _cluster_from_url(raw: str) -> Any:
    parsed = urlparse(raw)
    try:
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        raise _invalid("cluster needs a valid port") from None
    if port is None:
        port = DEFAULT_PORT
    elif port == 0:
        raise _invalid("cluster needs a valid port")
    if not host:
        raise _invalid("cluster needs a host that resolves to every replica")
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise _invalid("cluster takes only a host, a port and a secret")
    if port >= 65535:
        raise _invalid("cluster needs a port below 65535, the next one is used too")
    if parsed.username and not parsed.password:
        raise _invalid("put the cluster secret after a colon: cluster://:secret@host")
    secret = unquote(parsed.password) if parsed.password else None
    if not secret and not os.environ.get(SECRET_ENV):
        raise _invalid(
            f"cluster needs a secret: cluster://:secret@host or {SECRET_ENV}"
        )
    return functools.partial(ClusterSharedStorage, host=host, port=port, secret=secret)


def storage_from_env(value: Optional[str]) -> Any:
    """Turn a ``DASH_SHARED_STORAGE`` value into a ``shared_storage`` argument.

    Returns ``None`` (disabled), or a zero-argument callable that builds the
    backend. Nothing is built or connected here, so startup stays lazy; missing
    optional dependencies still fail now, with the backend's own error.
    """
    raw = (value or "").strip()
    lowered = raw.lower()
    if lowered in ("", "none"):
        return None
    if lowered == "local":
        return LocalSharedStorage

    try:
        scheme = urlparse(raw).scheme.lower()
    except ValueError:
        raise _invalid("malformed URL") from None
    if scheme in ("redis", "rediss"):
        _require_redis()
        return _redis_from_url(raw)
    if scheme == "diskcache":
        parsed = urlparse(raw)
        if parsed.netloc or not parsed.path.startswith("/"):
            raise _invalid("diskcache needs an absolute path (three slashes)")
        _require_diskcache()
        return functools.partial(DiskcacheSharedStorage, directory=unquote(parsed.path))
    if scheme == "cluster":
        return _cluster_from_url(raw)
    raise _invalid("unknown backend")
