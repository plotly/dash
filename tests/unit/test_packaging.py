import os
import runpy
import shutil
from pathlib import Path
from unittest import mock

import setuptools
from setuptools._distutils.filelist import FileList

ROOT = Path(__file__).resolve().parents[2]


def test_only_dash_is_packaged(monkeypatch):
    # A stray top-level package in the wheel (for example the repo's benchmarks
    # harness) shadows a directory of the same name in every project that
    # installs dash.
    monkeypatch.chdir(ROOT)
    with mock.patch.object(setuptools, "setup") as setup:
        runpy.run_path(str(ROOT / "setup.py"))

    packages = setup.call_args.kwargs["packages"]
    assert "dash" in packages
    assert "dash.testing" in packages
    assert [p for p in packages if p != "dash" and not p.startswith("dash.")] == []


LABEXTENSION_FILES = [
    "package.json",
    "install.json",
    "static/remoteEntry.abc123.js",
    "static/509.abc123.js",
]


def _labextension_tree(root):
    for name in ["setup.py", "MANIFEST.in", "README.md", "dash/version.py"]:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, root / name)
    shutil.copytree(ROOT / "requirements", root / "requirements")
    for name in LABEXTENSION_FILES:
        path = root / "dash" / "labextension" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")


def test_sdist_includes_prebuilt_labextension(tmp_path, monkeypatch):
    # conda-forge builds the wheel from the sdist, so the sdist must carry the
    # whole static bundle or the installed extension has no remoteEntry.
    _labextension_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    file_list = FileList()
    file_list.findall()
    for line in (tmp_path / "MANIFEST.in").read_text().splitlines():
        if line.strip():
            file_list.process_template_line(line)

    for name in LABEXTENSION_FILES:
        assert f"dash/labextension/{name}" in file_list.files


def test_labextension_installed_as_prebuilt(tmp_path, monkeypatch):
    _labextension_tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    with mock.patch.object(setuptools, "setup") as setup:
        runpy.run_path(str(tmp_path / "setup.py"))

    dest = "share/jupyter/labextensions/@plotly/dash-jupyterlab"
    installed = {
        os.path.join(target, os.path.basename(source)).replace(os.sep, "/")
        for target, sources in setup.call_args.kwargs["data_files"]
        for source in sources
    }
    for name in LABEXTENSION_FILES:
        assert f"{dest}/{name}" in installed
