import os

from dash import _hot_reload


def _base(monkeypatch, tmp_path):
    # Pin the token store to a temp dir so the test never touches the real
    # user data dir.
    monkeypatch.setattr(_hot_reload, "_base_dir", lambda: str(tmp_path))


def test_stable_end_id_is_persisted_per_app_key(monkeypatch, tmp_path):
    _base(monkeypatch, tmp_path)

    calls = []

    def factory(value):
        def _make():
            calls.append(value)
            return value

        return _make

    first = _hot_reload.stable_end_id("app-A", factory("A-token"))
    # A second run of the same app reads the persisted token back instead of
    # minting a new one.
    second = _hot_reload.stable_end_id("app-A", factory("A-token-2"))

    assert first == "A-token"
    assert second == "A-token"
    assert calls == ["A-token"]  # factory only ran on the first (cache miss)


def test_stable_end_id_differs_between_apps(monkeypatch, tmp_path):
    _base(monkeypatch, tmp_path)

    a = _hot_reload.stable_end_id("app-A", lambda: "A-token")
    b = _hot_reload.stable_end_id("app-B", lambda: "B-token")

    assert a != b
    assert a == "A-token"
    assert b == "B-token"


def test_stable_end_id_falls_back_when_dir_unwritable(monkeypatch, tmp_path):
    # Point at a path that cannot be created (a file where a dir is expected)
    # so persistence fails; the freshly minted token is still returned.
    blocker = tmp_path / "blocker"
    blocker.write_text("not a dir")
    monkeypatch.setattr(_hot_reload, "_base_dir", lambda: str(blocker / "sub"))

    minted = _hot_reload.stable_end_id("app-A", lambda: "fresh")
    assert minted == "fresh"


def test_stable_end_id_hashes_key_into_filename(monkeypatch, tmp_path):
    _base(monkeypatch, tmp_path)

    # An app key that is a filesystem path must not leak path separators into
    # the token filename.
    _hot_reload.stable_end_id("/abs/path/to/app.py|/", lambda: "tok")

    files = os.listdir(os.path.join(str(tmp_path), _hot_reload._SUBDIR))
    assert len(files) == 1
    assert files[0].endswith(".txt")
    assert "/" not in files[0]
