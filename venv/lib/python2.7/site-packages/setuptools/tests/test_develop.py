"""develop tests
"""
import os
import shutil
import site
import sys
import tempfile

from setuptools.command.develop import develop
from setuptools.dist import Distribution

SETUP_PY = """\
from setuptools import setup

setup(name='foo',
    packages=['foo'],
    use_2to3=True,
)
"""

INIT_PY = """print "foo"
"""

class TestDevelopTest:

    def setup_method(self, method):
        if hasattr(sys, 'real_prefix'):
            return

        # Directory structure
        self.dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.dir, 'foo'))
        # setup.py
        setup = os.path.join(self.dir, 'setup.py')
        f = open(setup, 'w')
        f.write(SETUP_PY)
        f.close()
        self.old_cwd = os.getcwd()
        # foo/__init__.py
        init = os.path.join(self.dir, 'foo', '__init__.py')
        f = open(init, 'w')
        f.write(INIT_PY)
        f.close()

        os.chdir(self.dir)
        self.old_base = site.USER_BASE
        site.USER_BASE = tempfile.mkdtemp()
        self.old_site = site.USER_SITE
        site.USER_SITE = tempfile.mkdtemp()

    def teardown_method(self, method):
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            return

        os.chdir(self.old_cwd)
        shutil.rmtree(self.dir)
        shutil.rmtree(site.USER_BASE)
        shutil.rmtree(site.USER_SITE)
        site.USER_BASE = self.old_base
        site.USER_SITE = self.old_site

    def test_develop(self):
        if hasattr(sys, 'real_prefix'):
            return
        dist = Distribution(
            dict(name='foo',
                 packages=['foo'],
                 use_2to3=True,
                 version='0.0',
                 ))
        dist.script_name = 'setup.py'
        cmd = develop(dist)
        cmd.user = 1
        cmd.ensure_finalized()
        cmd.install_dir = site.USER_SITE
        cmd.user = 1
        old_stdout = sys.stdout
        #sys.stdout = StringIO()
        try:
            cmd.run()
        finally:
            sys.stdout = old_stdout

        # let's see if we got our egg link at the right place
        content = os.listdir(site.USER_SITE)
        content.sort()
        assert content == ['easy-install.pth', 'foo.egg-link']

        # Check that we are using the right code.
        egg_link_file = open(os.path.join(site.USER_SITE, 'foo.egg-link'), 'rt')
        try:
            path = egg_link_file.read().split()[0].strip()
        finally:
            egg_link_file.close()
        init_file = open(os.path.join(path, 'foo', '__init__.py'), 'rt')
        try:
            init = init_file.read().strip()
        finally:
            init_file.close()
        if sys.version < "3":
            assert init == 'print "foo"'
        else:
            assert init == 'print("foo")'
