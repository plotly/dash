"""Pick a shared-storage backend from ``DASH_SHARED_STORAGE``.

Lets a hosting platform switch backends without editing the app's ``Dash(...)``
call. Only used when the app did not pass ``shared_storage=``.
"""

import functools
import re
from typing import Any, Optional
from urllib.parse import urlparse

from ..exceptions import InvalidConfig
from .diskcache import DiskcacheSharedStorage, _require_diskcache
from .local import LocalSharedStorage
from .redis import RedisSharedStorage, _require_redis

ENV_VAR = "DASH_SHARED_STORAGE"


def _redact(value: str) -> str:
    # Keep credentials in a URL out of the error message.
    return re.sub(r"(://)[^/@]*@", r"\1***@", value)


def _invalid(value: str, reason: str) -> InvalidConfig:
    return InvalidConfig(
        f"{ENV_VAR}={_redact(value)!r} is not valid: {reason}. Use 'local', 'none', "
        "'diskcache:///absolute/path', or a redis:// or rediss:// URL."
    )


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

    scheme = urlparse(raw).scheme.lower()
    if scheme in ("redis", "rediss"):
        _require_redis()
        return functools.partial(RedisSharedStorage, url=raw)
    if scheme == "diskcache":
        parsed = urlparse(raw)
        if parsed.netloc or not parsed.path.startswith("/"):
            raise _invalid(raw, "diskcache needs an absolute path (three slashes)")
        _require_diskcache()
        return functools.partial(DiskcacheSharedStorage, directory=parsed.path)
    if scheme == "cluster":
        raise InvalidConfig(
            f"{ENV_VAR}={_redact(raw)!r}: the cluster:// backend is not supported in this "
            "version of Dash."
        )
    raise _invalid(raw, "unknown backend")
