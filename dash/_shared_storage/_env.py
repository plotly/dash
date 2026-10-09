"""Pick a shared-storage backend from ``DASH_SHARED_STORAGE``.

Lets a hosting platform switch backends without editing the app's ``Dash(...)``
call. Only used when the app did not pass ``shared_storage=``.
"""

import functools
from typing import Any, Optional
from urllib.parse import parse_qsl, unquote, urlencode, urlparse

from ..exceptions import InvalidConfig
from .diskcache import DiskcacheSharedStorage, _require_diskcache
from .local import LocalSharedStorage
from .redis import RedisSharedStorage, _require_redis

ENV_VAR = "DASH_SHARED_STORAGE"


def _invalid(reason: str) -> InvalidConfig:
    # The value can hold credentials, so it stays out of the message.
    return InvalidConfig(
        f"{ENV_VAR} is not valid: {reason}. Use 'local', 'none', "
        "'diskcache:///absolute/path', or a redis:// or rediss:// URL."
    )


def _redis_from_url(raw: str) -> Any:
    parsed = urlparse(raw)
    query = parse_qsl(parsed.query, keep_blank_values=True)
    kwargs = {}
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


def storage_from_env(value: Optional[str]) -> Any:
    """Turn a ``DASH_SHARED_STORAGE`` value into a ``shared_storage`` argument.

    Returns ``None`` (disabled), or a zero-argument callable that builds the
    backend. Nothing is built or connected here, so startup stays lazy; missing
    optional dependencies still fail now, with the backend's own error.
    """
    raw = (value or "").strip()
    lowered = raw.lower()
    if lowered in ("", "local"):
        return LocalSharedStorage
    if lowered == "none":
        return None

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
        raise InvalidConfig(
            f"{ENV_VAR}: the cluster:// backend is not supported in this "
            "version of Dash."
        )
    raise _invalid("unknown backend")
