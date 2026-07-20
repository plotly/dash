"""Signing helpers for background-callback handles.

Background callbacks round-trip two values through the browser: the ``cacheKey``
(the diskcache/celery result key) and the ``job`` (the OS PID or Celery task id).
Historically these were sent to the client verbatim and trusted verbatim when
they came back, which let any HTTP client ask the server to read/delete an
arbitrary cache entry or to ``SIGKILL`` an arbitrary process id.

To close that, the server issues a per-page-load ``end_id`` token (signed so the
server can recognise the ones it minted), and every ``cacheKey``/``job`` handle
is HMAC-signed with a server-held secret and bound to that ``end_id``. A forged
PID or arbitrary cache key never carries a valid signature, and a handle minted
for one page load cannot be replayed from another. The client treats all of
these as opaque strings, so nothing about the handshake is visible to or
forgeable by the browser.

(This ``end_id`` is unrelated to the client-generated ``rendererId`` used for
SharedWorker routing in ``dash-renderer/src/utils/rendererId.ts``.)
"""

import hmac
from hashlib import sha256
from typing import Optional

# Separates the payload from its signature in a signed token. Chosen because it
# never appears in the values we sign (hex digests, integers, and gen_salt
# output are all limited to ``[A-Za-z0-9]``).
_SEP = "~"


def _mac(secret: bytes, scope: str, value: str) -> str:
    msg = f"{scope}\x00{value}".encode("utf-8")
    return hmac.new(secret, msg, sha256).hexdigest()


def sign(secret: bytes, scope: str, value: str) -> str:
    """Return ``value`` with an HMAC signature appended, bound to ``scope``."""
    return f"{value}{_SEP}{_mac(secret, scope, value)}"


def unsign(secret: bytes, scope: str, signed: Optional[str]) -> Optional[str]:
    """Verify a signed token and return the original value, or ``None``.

    Returns ``None`` when the token is missing, malformed, or the signature does
    not match ``scope`` under ``secret``. Uses a constant-time comparison so the
    check does not leak the expected signature.
    """
    if not signed or _SEP not in signed:
        return None

    value, _, mac = signed.rpartition(_SEP)
    expected = _mac(secret, scope, value)
    if hmac.compare_digest(mac, expected):
        return value
    return None


# Scope strings. The end_id is folded into the job/cache scopes so a handle is
# only valid for the page load it was issued to.
END_SCOPE = "end"


def job_scope(end_id: Optional[str]) -> str:
    return f"job:{end_id or ''}"


def cache_scope(end_id: Optional[str]) -> str:
    return f"cacheKey:{end_id or ''}"
