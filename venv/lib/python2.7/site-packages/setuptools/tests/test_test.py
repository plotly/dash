# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import os
import site

import pytest

from setuptools.command.test import test
from setuptools.dist import Distribution

from .textwrap import DALS
from . import contexts

SETUP_PY = DALS("""
    from setuptools import setup

    setup(name='foo',
        packages=['name', 'name.space', 'name.space.tests'],
        namespace_packages=['name'],
        test_suite='name.space.tests.test_suite',
    )
    """)

NS_INIT = DALS("""
    # -*- coding: Latin-1 -*-
    # Söme Arbiträry Ünicode to test Distribute Issüé 310
    try:
        __import__('pkg_resources').declare_namespace(__name__)
    except ImportError:
        from pkgutil import extend_path
        __path__ = extend_path(__path__, __name__)
    """)

TEST_PY = DALS("""
    import unittest

    class TestTest(unittest.TestCase):
        def test_test(self):
            print "Foo" # Should fail under Python 3 unless 2to3 is used

    test_suite = unittest.makeSuite(TestTest)
    """)


@pytest.fixture
def sample_test(tmpdir_cwd):
    os.makedirs('name/space/tests')

    # setup.py
    with open('setup.py', 'wt') as f:
        f.write(SETUP_PY)

    # name/__init__.py
    with open('name/__init__.py', 'wb') as f:
        f.write(NS_INIT.encode('Latin-1'))

    # name/space/__init__.py
    with open('name/space/__init__.py', 'wt') as f:
        f.write('#empty\n')

    # name/space/tests/__init__.py
    with open('name/space/tests/__init__.py', 'wt') as f:
        f.write(TEST_PY)


@pytest.mark.skipif('hasattr(sys, "real_prefix")')
@pytest.mark.usefixtures('user_override')
@pytest.mark.usefixtures('sample_test')
class TestTestTest:

    def test_test(self):
        params = dict(
            name='foo',
            packages=['name', 'name.space', 'name.space.tests'],
            namespace_packages=['name'],
            test_suite='name.space.tests.test_suite',
            use_2to3=True,
        )
        dist = Distribution(params)
        dist.script_name = 'setup.py'
        cmd = test(dist)
        cmd.user = 1
        cmd.ensure_finalized()
        cmd.install_dir = site.USER_SITE
        cmd.user = 1
        with contexts.quiet():
            # The test runner calls sys.exit
            with contexts.suppress_exceptions(SystemExit):
                cmd.run()
