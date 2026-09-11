"""Persistence for the hot-reload state-preservation token.

When ``dev_tools_hot_reload_preserve_state`` is on, the renderer scopes the
sessionStorage snapshot of preserved UI state by the page's ``end_id`` (see
``dash/_callback_signing.py``). A hard hot reload restarts the server process
and re-serves the page, so that token has to survive the restart *and* stay
unique to this app - otherwise switching to a different app served on the same
URL (same ``window.location.pathname``) would let one app's snapshot be
restored into another's, re-firing its callbacks with foreign state.

We get both by persisting the token to disk keyed by the app's path: the same
app reads back the same token across reloads, a different app (different path)
gets a different one and so a different sessionStorage scope. This is a
dev-only convenience, so a missing/unwritable cache dir degrades gracefully to
an in-process token (state is then preserved across soft reloads only).
"""

import hashlib
import os
import tempfile

_SUBDIR = "hot_reload_state"


def _base_dir():
    """A per-user writable directory for the persisted tokens.

    Prefer ``platformdirs`` when it is importable (it picks the right per-OS
    location), but never hard-depend on it - fall back to ``~/.dash`` and then
    the system temp dir so this keeps working in a bare install.
    """
    try:
        import platformdirs  # pylint: disable=import-outside-toplevel

        return platformdirs.user_data_dir("dash", "plotly")
    except Exception:  # pylint: disable=broad-except
        pass
    try:
        home = os.path.expanduser("~")
        if home and home != "~":
            return os.path.join(home, ".dash")
    except Exception:  # pylint: disable=broad-except
        pass
    return os.path.join(tempfile.gettempdir(), "dash")


def _token_path(app_key):
    # Hash the app key so an arbitrary filesystem path becomes a safe,
    # fixed-length filename.
    digest = hashlib.sha256(app_key.encode("utf-8")).hexdigest()[:16]
    return os.path.join(_base_dir(), _SUBDIR, f"{digest}.txt")


def stable_end_id(app_key, factory):
    """Return a token stable across reloads of the app identified by ``app_key``.

    Reads the persisted token for ``app_key`` if one exists, otherwise calls
    ``factory()`` to mint a fresh one and persists it. Any disk error falls
    back to the freshly minted token without persisting, so hot reload still
    works (state preserved across soft reloads only).
    """
    path = _token_path(app_key)
    try:
        with open(path, encoding="utf-8") as handle:
            existing = handle.read().strip()
        if existing:
            return existing
    except OSError:
        pass

    token = factory()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(token)
    except OSError:
        pass
    return token
