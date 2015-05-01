"""Run some integration tests.

Try to install a few packages.
"""

import glob
import os
import sys

import pytest

from setuptools.command.easy_install import easy_install
from setuptools.command import easy_install as easy_install_pkg
from setuptools.dist import Distribution
from setuptools.compat import urlopen


def setup_module(module):
    packages = 'stevedore', 'virtualenvwrapper', 'pbr', 'novaclient'
    for pkg in packages:
        try:
            __import__(pkg)
            tmpl = "Integration tests cannot run when {pkg} is installed"
            pytest.skip(tmpl.format(**locals()))
        except ImportError:
            pass

    try:
        urlopen('https://pypi.python.org/pypi')
    except Exception as exc:
        pytest.skip(reason=str(exc))


@pytest.fixture
def install_context(request, tmpdir, monkeypatch):
    """Fixture to set up temporary installation directory.
    """
    # Save old values so we can restore them.
    new_cwd = tmpdir.mkdir('cwd')
    user_base = tmpdir.mkdir('user_base')
    user_site = tmpdir.mkdir('user_site')
    install_dir = tmpdir.mkdir('install_dir')

    def fin():
        # undo the monkeypatch, particularly needed under
        # windows because of kept handle on cwd
        monkeypatch.undo()
        new_cwd.remove()
        user_base.remove()
        user_site.remove()
        install_dir.remove()
    request.addfinalizer(fin)

    # Change the environment and site settings to control where the
    # files are installed and ensure we do not overwrite anything.
    monkeypatch.chdir(new_cwd)
    monkeypatch.setattr(easy_install_pkg, '__file__', user_site.strpath)
    monkeypatch.setattr('site.USER_BASE', user_base.strpath)
    monkeypatch.setattr('site.USER_SITE', user_site.strpath)
    monkeypatch.setattr('sys.path', sys.path + [install_dir.strpath])
    monkeypatch.setenv('PYTHONPATH', os.path.pathsep.join(sys.path))

    # Set up the command for performing the installation.
    dist = Distribution()
    cmd = easy_install(dist)
    cmd.install_dir = install_dir.strpath
    return cmd


def _install_one(requirement, cmd, pkgname, modulename):
    cmd.args = [requirement]
    cmd.ensure_finalized()
    cmd.run()
    target = cmd.install_dir
    dest_path = glob.glob(os.path.join(target, pkgname + '*.egg'))
    assert dest_path
    assert os.path.exists(os.path.join(dest_path[0], pkgname, modulename))


def test_stevedore(install_context):
    _install_one('stevedore', install_context,
                 'stevedore', 'extension.py')


@pytest.mark.xfail
def test_virtualenvwrapper(install_context):
    _install_one('virtualenvwrapper', install_context,
                 'virtualenvwrapper', 'hook_loader.py')


def test_pbr(install_context):
    _install_one('pbr', install_context,
                 'pbr', 'core.py')


@pytest.mark.xfail
def test_python_novaclient(install_context):
    _install_one('python-novaclient', install_context,
                 'novaclient', 'base.py')
