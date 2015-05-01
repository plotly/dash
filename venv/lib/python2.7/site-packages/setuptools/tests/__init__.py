"""Tests for the 'setuptools' package"""
import sys
import os
import distutils.core
import distutils.cmd
from distutils.errors import DistutilsOptionError, DistutilsPlatformError
from distutils.errors import DistutilsSetupError
from distutils.core import Extension
from distutils.version import LooseVersion
from setuptools.compat import func_code

import pytest

import setuptools.dist
import setuptools.depends as dep
from setuptools import Feature
from setuptools.depends import Require

def makeSetup(**args):
    """Return distribution from 'setup(**args)', without executing commands"""

    distutils.core._setup_stop_after = "commandline"

    # Don't let system command line leak into tests!
    args.setdefault('script_args',['install'])

    try:
        return setuptools.setup(**args)
    finally:
        distutils.core._setup_stop_after = None


needs_bytecode = pytest.mark.skipif(
    not hasattr(dep, 'get_module_constant'),
    reason="bytecode support not available",
)

class TestDepends:

    def testExtractConst(self):
        if not hasattr(dep, 'extract_constant'):
            # skip on non-bytecode platforms
            return

        def f1():
            global x, y, z
            x = "test"
            y = z

        fc = func_code(f1)

        # unrecognized name
        assert dep.extract_constant(fc,'q', -1) is None

        # constant assigned
        dep.extract_constant(fc,'x', -1) == "test"

        # expression assigned
        dep.extract_constant(fc,'y', -1) == -1

        # recognized name, not assigned
        dep.extract_constant(fc,'z', -1) is None

    def testFindModule(self):
        with pytest.raises(ImportError):
            dep.find_module('no-such.-thing')
        with pytest.raises(ImportError):
            dep.find_module('setuptools.non-existent')
        f,p,i = dep.find_module('setuptools.tests')
        f.close()

    @needs_bytecode
    def testModuleExtract(self):
        from email import __version__
        assert dep.get_module_constant('email','__version__') == __version__
        assert dep.get_module_constant('sys','version') == sys.version
        assert dep.get_module_constant('setuptools.tests','__doc__') == __doc__

    @needs_bytecode
    def testRequire(self):
        req = Require('Email','1.0.3','email')

        assert req.name == 'Email'
        assert req.module == 'email'
        assert req.requested_version == '1.0.3'
        assert req.attribute == '__version__'
        assert req.full_name() == 'Email-1.0.3'

        from email import __version__
        assert req.get_version() == __version__
        assert req.version_ok('1.0.9')
        assert not req.version_ok('0.9.1')
        assert not req.version_ok('unknown')

        assert req.is_present()
        assert req.is_current()

        req = Require('Email 3000','03000','email',format=LooseVersion)
        assert req.is_present()
        assert not req.is_current()
        assert not req.version_ok('unknown')

        req = Require('Do-what-I-mean','1.0','d-w-i-m')
        assert not req.is_present()
        assert not req.is_current()

        req = Require('Tests', None, 'tests', homepage="http://example.com")
        assert req.format is None
        assert req.attribute is None
        assert req.requested_version is None
        assert req.full_name() == 'Tests'
        assert req.homepage == 'http://example.com'

        paths = [os.path.dirname(p) for p in __path__]
        assert req.is_present(paths)
        assert req.is_current(paths)


class TestDistro:

    def setup_method(self, method):
        self.e1 = Extension('bar.ext',['bar.c'])
        self.e2 = Extension('c.y', ['y.c'])

        self.dist = makeSetup(
            packages=['a', 'a.b', 'a.b.c', 'b', 'c'],
            py_modules=['b.d','x'],
            ext_modules = (self.e1, self.e2),
            package_dir = {},
        )

    def testDistroType(self):
        assert isinstance(self.dist,setuptools.dist.Distribution)

    def testExcludePackage(self):
        self.dist.exclude_package('a')
        assert self.dist.packages == ['b','c']

        self.dist.exclude_package('b')
        assert self.dist.packages == ['c']
        assert self.dist.py_modules == ['x']
        assert self.dist.ext_modules == [self.e1, self.e2]

        self.dist.exclude_package('c')
        assert self.dist.packages == []
        assert self.dist.py_modules == ['x']
        assert self.dist.ext_modules == [self.e1]

        # test removals from unspecified options
        makeSetup().exclude_package('x')

    def testIncludeExclude(self):
        # remove an extension
        self.dist.exclude(ext_modules=[self.e1])
        assert self.dist.ext_modules == [self.e2]

        # add it back in
        self.dist.include(ext_modules=[self.e1])
        assert self.dist.ext_modules == [self.e2, self.e1]

        # should not add duplicate
        self.dist.include(ext_modules=[self.e1])
        assert self.dist.ext_modules == [self.e2, self.e1]

    def testExcludePackages(self):
        self.dist.exclude(packages=['c','b','a'])
        assert self.dist.packages == []
        assert self.dist.py_modules == ['x']
        assert self.dist.ext_modules == [self.e1]

    def testEmpty(self):
        dist = makeSetup()
        dist.include(packages=['a'], py_modules=['b'], ext_modules=[self.e2])
        dist = makeSetup()
        dist.exclude(packages=['a'], py_modules=['b'], ext_modules=[self.e2])

    def testContents(self):
        assert self.dist.has_contents_for('a')
        self.dist.exclude_package('a')
        assert not self.dist.has_contents_for('a')

        assert self.dist.has_contents_for('b')
        self.dist.exclude_package('b')
        assert not self.dist.has_contents_for('b')

        assert self.dist.has_contents_for('c')
        self.dist.exclude_package('c')
        assert not self.dist.has_contents_for('c')

    def testInvalidIncludeExclude(self):
        with pytest.raises(DistutilsSetupError):
            self.dist.include(nonexistent_option='x')
        with pytest.raises(DistutilsSetupError):
            self.dist.exclude(nonexistent_option='x')
        with pytest.raises(DistutilsSetupError):
            self.dist.include(packages={'x':'y'})
        with pytest.raises(DistutilsSetupError):
            self.dist.exclude(packages={'x':'y'})
        with pytest.raises(DistutilsSetupError):
            self.dist.include(ext_modules={'x':'y'})
        with pytest.raises(DistutilsSetupError):
            self.dist.exclude(ext_modules={'x':'y'})

        with pytest.raises(DistutilsSetupError):
            self.dist.include(package_dir=['q'])
        with pytest.raises(DistutilsSetupError):
            self.dist.exclude(package_dir=['q'])


class TestFeatures:

    def setup_method(self, method):
        self.req = Require('Distutils','1.0.3','distutils')
        self.dist = makeSetup(
            features={
                'foo': Feature("foo",standard=True,require_features=['baz',self.req]),
                'bar': Feature("bar",  standard=True, packages=['pkg.bar'],
                               py_modules=['bar_et'], remove=['bar.ext'],
                       ),
                'baz': Feature(
                        "baz", optional=False, packages=['pkg.baz'],
                        scripts = ['scripts/baz_it'],
                        libraries=[('libfoo','foo/foofoo.c')]
                       ),
                'dwim': Feature("DWIM", available=False, remove='bazish'),
            },
            script_args=['--without-bar', 'install'],
            packages = ['pkg.bar', 'pkg.foo'],
            py_modules = ['bar_et', 'bazish'],
            ext_modules = [Extension('bar.ext',['bar.c'])]
        )

    def testDefaults(self):
        assert not Feature(
            "test",standard=True,remove='x',available=False
        ).include_by_default()
        assert Feature("test",standard=True,remove='x').include_by_default()
        # Feature must have either kwargs, removes, or require_features
        with pytest.raises(DistutilsSetupError):
            Feature("test")

    def testAvailability(self):
        with pytest.raises(DistutilsPlatformError):
            self.dist.features['dwim'].include_in(self.dist)

    def testFeatureOptions(self):
        dist = self.dist
        assert (
            ('with-dwim',None,'include DWIM') in dist.feature_options
        )
        assert (
            ('without-dwim',None,'exclude DWIM (default)') in dist.feature_options
        )
        assert (
            ('with-bar',None,'include bar (default)') in dist.feature_options
        )
        assert (
            ('without-bar',None,'exclude bar') in dist.feature_options
        )
        assert dist.feature_negopt['without-foo'] == 'with-foo'
        assert dist.feature_negopt['without-bar'] == 'with-bar'
        assert dist.feature_negopt['without-dwim'] == 'with-dwim'
        assert (not 'without-baz' in dist.feature_negopt)

    def testUseFeatures(self):
        dist = self.dist
        assert dist.with_foo == 1
        assert dist.with_bar == 0
        assert dist.with_baz == 1
        assert (not 'bar_et' in dist.py_modules)
        assert (not 'pkg.bar' in dist.packages)
        assert ('pkg.baz' in dist.packages)
        assert ('scripts/baz_it' in dist.scripts)
        assert (('libfoo','foo/foofoo.c') in dist.libraries)
        assert dist.ext_modules == []
        assert dist.require_features == [self.req]

        # If we ask for bar, it should fail because we explicitly disabled
        # it on the command line
        with pytest.raises(DistutilsOptionError):
            dist.include_feature('bar')

    def testFeatureWithInvalidRemove(self):
        with pytest.raises(SystemExit):
            makeSetup(features={'x':Feature('x', remove='y')})

class TestCommandTests:

    def testTestIsCommand(self):
        test_cmd = makeSetup().get_command_obj('test')
        assert (isinstance(test_cmd, distutils.cmd.Command))

    def testLongOptSuiteWNoDefault(self):
        ts1 = makeSetup(script_args=['test','--test-suite=foo.tests.suite'])
        ts1 = ts1.get_command_obj('test')
        ts1.ensure_finalized()
        assert ts1.test_suite == 'foo.tests.suite'

    def testDefaultSuite(self):
        ts2 = makeSetup(test_suite='bar.tests.suite').get_command_obj('test')
        ts2.ensure_finalized()
        assert ts2.test_suite == 'bar.tests.suite'

    def testDefaultWModuleOnCmdLine(self):
        ts3 = makeSetup(
            test_suite='bar.tests',
            script_args=['test','-m','foo.tests']
        ).get_command_obj('test')
        ts3.ensure_finalized()
        assert ts3.test_module == 'foo.tests'
        assert ts3.test_suite == 'foo.tests.test_suite'

    def testConflictingOptions(self):
        ts4 = makeSetup(
            script_args=['test','-m','bar.tests', '-s','foo.tests.suite']
        ).get_command_obj('test')
        with pytest.raises(DistutilsOptionError):
            ts4.ensure_finalized()

    def testNoSuite(self):
        ts5 = makeSetup().get_command_obj('test')
        ts5.ensure_finalized()
        assert ts5.test_suite == None
