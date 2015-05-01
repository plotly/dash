# -*- coding: utf-8 -*-

"""Easy install Tests
"""
from __future__ import absolute_import

import sys
import os
import shutil
import tempfile
import site
import contextlib
import tarfile
import logging
import itertools
import distutils.errors

import pytest
try:
    from unittest import mock
except ImportError:
    import mock

from setuptools import sandbox
from setuptools import compat
from setuptools.compat import StringIO, BytesIO, urlparse
from setuptools.sandbox import run_setup
import setuptools.command.easy_install as ei
from setuptools.command.easy_install import PthDistributions
from setuptools.command import easy_install as easy_install_pkg
from setuptools.dist import Distribution
from pkg_resources import working_set
from pkg_resources import Distribution as PRDistribution
import setuptools.tests.server
import pkg_resources

from .py26compat import tarfile_open
from . import contexts
from .textwrap import DALS


class FakeDist(object):
    def get_entry_map(self, group):
        if group != 'console_scripts':
            return {}
        return {'name': 'ep'}

    def as_requirement(self):
        return 'spec'

SETUP_PY = DALS("""
    from setuptools import setup

    setup(name='foo')
    """)

class TestEasyInstallTest:

    def test_install_site_py(self):
        dist = Distribution()
        cmd = ei.easy_install(dist)
        cmd.sitepy_installed = False
        cmd.install_dir = tempfile.mkdtemp()
        try:
            cmd.install_site_py()
            sitepy = os.path.join(cmd.install_dir, 'site.py')
            assert os.path.exists(sitepy)
        finally:
            shutil.rmtree(cmd.install_dir)

    def test_get_script_args(self):
        header = ei.CommandSpec.best().from_environment().as_header()
        expected = header + DALS("""
            # EASY-INSTALL-ENTRY-SCRIPT: 'spec','console_scripts','name'
            __requires__ = 'spec'
            import sys
            from pkg_resources import load_entry_point

            if __name__ == '__main__':
                sys.exit(
                    load_entry_point('spec', 'console_scripts', 'name')()
                )
            """)
        dist = FakeDist()

        args = next(ei.ScriptWriter.get_args(dist))
        name, script = itertools.islice(args, 2)

        assert script == expected

    def test_no_find_links(self):
        # new option '--no-find-links', that blocks find-links added at
        # the project level
        dist = Distribution()
        cmd = ei.easy_install(dist)
        cmd.check_pth_processing = lambda: True
        cmd.no_find_links = True
        cmd.find_links = ['link1', 'link2']
        cmd.install_dir = os.path.join(tempfile.mkdtemp(), 'ok')
        cmd.args = ['ok']
        cmd.ensure_finalized()
        assert cmd.package_index.scanned_urls == {}

        # let's try without it (default behavior)
        cmd = ei.easy_install(dist)
        cmd.check_pth_processing = lambda: True
        cmd.find_links = ['link1', 'link2']
        cmd.install_dir = os.path.join(tempfile.mkdtemp(), 'ok')
        cmd.args = ['ok']
        cmd.ensure_finalized()
        keys = sorted(cmd.package_index.scanned_urls.keys())
        assert keys == ['link1', 'link2']

    def test_write_exception(self):
        """
        Test that `cant_write_to_target` is rendered as a DistutilsError.
        """
        dist = Distribution()
        cmd = ei.easy_install(dist)
        cmd.install_dir = os.getcwd()
        with pytest.raises(distutils.errors.DistutilsError):
            cmd.cant_write_to_target()


class TestPTHFileWriter:
    def test_add_from_cwd_site_sets_dirty(self):
        '''a pth file manager should set dirty
        if a distribution is in site but also the cwd
        '''
        pth = PthDistributions('does-not_exist', [os.getcwd()])
        assert not pth.dirty
        pth.add(PRDistribution(os.getcwd()))
        assert pth.dirty

    def test_add_from_site_is_ignored(self):
        location = '/test/location/does-not-have-to-exist'
        # PthDistributions expects all locations to be normalized
        location = pkg_resources.normalize_path(location)
        pth = PthDistributions('does-not_exist', [location, ])
        assert not pth.dirty
        pth.add(PRDistribution(location))
        assert not pth.dirty


@pytest.yield_fixture
def setup_context(tmpdir):
    with (tmpdir/'setup.py').open('w') as f:
        f.write(SETUP_PY)
    with tmpdir.as_cwd():
        yield tmpdir


@pytest.mark.usefixtures("user_override")
@pytest.mark.usefixtures("setup_context")
class TestUserInstallTest:

    # prevent check that site-packages is writable. easy_install
    # shouldn't be writing to system site-packages during finalize
    # options, but while it does, bypass the behavior.
    prev_sp_write = mock.patch(
        'setuptools.command.easy_install.easy_install.check_site_dir',
        mock.Mock(),
    )

    # simulate setuptools installed in user site packages
    @mock.patch('setuptools.command.easy_install.__file__', site.USER_SITE)
    @mock.patch('site.ENABLE_USER_SITE', True)
    @prev_sp_write
    def test_user_install_not_implied_user_site_enabled(self):
        self.assert_not_user_site()

    @mock.patch('site.ENABLE_USER_SITE', False)
    @prev_sp_write
    def test_user_install_not_implied_user_site_disabled(self):
        self.assert_not_user_site()

    @staticmethod
    def assert_not_user_site():
        # create a finalized easy_install command
        dist = Distribution()
        dist.script_name = 'setup.py'
        cmd = ei.easy_install(dist)
        cmd.args = ['py']
        cmd.ensure_finalized()
        assert not cmd.user, 'user should not be implied'

    def test_multiproc_atexit(self):
        pytest.importorskip('multiprocessing')

        log = logging.getLogger('test_easy_install')
        logging.basicConfig(level=logging.INFO, stream=sys.stderr)
        log.info('this should not break')

    @pytest.fixture()
    def foo_package(self, tmpdir):
        egg_file = tmpdir / 'foo-1.0.egg-info'
        with egg_file.open('w') as f:
            f.write('Name: foo\n')
        return str(tmpdir)

    @pytest.yield_fixture()
    def install_target(self, tmpdir):
        target = str(tmpdir)
        with mock.patch('sys.path', sys.path + [target]):
            python_path = os.path.pathsep.join(sys.path)
            with mock.patch.dict(os.environ, PYTHONPATH=python_path):
                yield target

    def test_local_index(self, foo_package, install_target):
        """
        The local index must be used when easy_install locates installed
        packages.
        """
        dist = Distribution()
        dist.script_name = 'setup.py'
        cmd = ei.easy_install(dist)
        cmd.install_dir = install_target
        cmd.args = ['foo']
        cmd.ensure_finalized()
        cmd.local_index.scan([foo_package])
        res = cmd.easy_install('foo')
        actual = os.path.normcase(os.path.realpath(res.location))
        expected = os.path.normcase(os.path.realpath(foo_package))
        assert actual == expected

    @contextlib.contextmanager
    def user_install_setup_context(self, *args, **kwargs):
        """
        Wrap sandbox.setup_context to patch easy_install in that context to
        appear as user-installed.
        """
        with self.orig_context(*args, **kwargs):
            import setuptools.command.easy_install as ei
            ei.__file__ = site.USER_SITE
            yield

    def patched_setup_context(self):
        self.orig_context = sandbox.setup_context

        return mock.patch(
            'setuptools.sandbox.setup_context',
            self.user_install_setup_context,
        )


@pytest.yield_fixture
def distutils_package():
    distutils_setup_py = SETUP_PY.replace(
        'from setuptools import setup',
        'from distutils.core import setup',
    )
    with contexts.tempdir(cd=os.chdir):
        with open('setup.py', 'w') as f:
            f.write(distutils_setup_py)
        yield


class TestDistutilsPackage:
    def test_bdist_egg_available_on_distutils_pkg(self, distutils_package):
        run_setup('setup.py', ['bdist_egg'])


class TestSetupRequires:

    def test_setup_requires_honors_fetch_params(self):
        """
        When easy_install installs a source distribution which specifies
        setup_requires, it should honor the fetch parameters (such as
        allow-hosts, index-url, and find-links).
        """
        # set up a server which will simulate an alternate package index.
        p_index = setuptools.tests.server.MockServer()
        p_index.start()
        netloc = 1
        p_index_loc = urlparse(p_index.url)[netloc]
        if p_index_loc.endswith(':0'):
            # Some platforms (Jython) don't find a port to which to bind,
            #  so skip this test for them.
            return
        with contexts.quiet():
            # create an sdist that has a build-time dependency.
            with TestSetupRequires.create_sdist() as dist_file:
                with contexts.tempdir() as temp_install_dir:
                    with contexts.environment(PYTHONPATH=temp_install_dir):
                        ei_params = [
                            '--index-url', p_index.url,
                            '--allow-hosts', p_index_loc,
                            '--exclude-scripts',
                            '--install-dir', temp_install_dir,
                            dist_file,
                        ]
                        with sandbox.save_argv(['easy_install']):
                            # attempt to install the dist. It should fail because
                            #  it doesn't exist.
                            with pytest.raises(SystemExit):
                                easy_install_pkg.main(ei_params)
        # there should have been two or three requests to the server
        #  (three happens on Python 3.3a)
        assert 2 <= len(p_index.requests) <= 3
        assert p_index.requests[0].path == '/does-not-exist/'

    @staticmethod
    @contextlib.contextmanager
    def create_sdist():
        """
        Return an sdist with a setup_requires dependency (of something that
        doesn't exist)
        """
        with contexts.tempdir() as dir:
            dist_path = os.path.join(dir, 'setuptools-test-fetcher-1.0.tar.gz')
            script = DALS("""
                import setuptools
                setuptools.setup(
                    name="setuptools-test-fetcher",
                    version="1.0",
                    setup_requires = ['does-not-exist'],
                )
                """)
            make_trivial_sdist(dist_path, script)
            yield dist_path

    def test_setup_requires_overrides_version_conflict(self):
        """
        Regression test for issue #323.

        Ensures that a distribution's setup_requires requirements can still be
        installed and used locally even if a conflicting version of that
        requirement is already on the path.
        """

        pr_state = pkg_resources.__getstate__()
        fake_dist = PRDistribution('does-not-matter', project_name='foobar',
                                   version='0.0')
        working_set.add(fake_dist)

        try:
            with contexts.tempdir() as temp_dir:
                test_pkg = create_setup_requires_package(temp_dir)
                test_setup_py = os.path.join(test_pkg, 'setup.py')
                with contexts.quiet() as (stdout, stderr):
                    # Don't even need to install the package, just
                    # running the setup.py at all is sufficient
                    run_setup(test_setup_py, ['--name'])

                lines = stdout.readlines()
                assert len(lines) > 0
                assert lines[-1].strip(), 'test_pkg'
        finally:
            pkg_resources.__setstate__(pr_state)


def create_setup_requires_package(path):
    """Creates a source tree under path for a trivial test package that has a
    single requirement in setup_requires--a tarball for that requirement is
    also created and added to the dependency_links argument.
    """

    test_setup_attrs = {
        'name': 'test_pkg', 'version': '0.0',
        'setup_requires': ['foobar==0.1'],
        'dependency_links': [os.path.abspath(path)]
    }

    test_pkg = os.path.join(path, 'test_pkg')
    test_setup_py = os.path.join(test_pkg, 'setup.py')
    os.mkdir(test_pkg)

    with open(test_setup_py, 'w') as f:
        f.write(DALS("""
            import setuptools
            setuptools.setup(**%r)
        """ % test_setup_attrs))

    foobar_path = os.path.join(path, 'foobar-0.1.tar.gz')
    make_trivial_sdist(
        foobar_path,
        DALS("""
            import setuptools
            setuptools.setup(
                name='foobar',
                version='0.1'
            )
        """))

    return test_pkg


def make_trivial_sdist(dist_path, setup_py):
    """Create a simple sdist tarball at dist_path, containing just a
    setup.py, the contents of which are provided by the setup_py string.
    """

    setup_py_file = tarfile.TarInfo(name='setup.py')
    try:
        # Python 3 (StringIO gets converted to io module)
        MemFile = BytesIO
    except AttributeError:
        MemFile = StringIO
    setup_py_bytes = MemFile(setup_py.encode('utf-8'))
    setup_py_file.size = len(setup_py_bytes.getvalue())
    with tarfile_open(dist_path, 'w:gz') as dist:
        dist.addfile(setup_py_file, fileobj=setup_py_bytes)


class TestScriptHeader:
    non_ascii_exe = '/Users/José/bin/python'
    exe_with_spaces = r'C:\Program Files\Python33\python.exe'

    @pytest.mark.skipif(
        sys.platform.startswith('java') and ei.is_sh(sys.executable),
        reason="Test cannot run under java when executable is sh"
    )
    def test_get_script_header(self):
        expected = '#!%s\n' % ei.nt_quote_arg(os.path.normpath(sys.executable))
        actual = ei.ScriptWriter.get_script_header('#!/usr/local/bin/python')
        assert actual == expected

        expected = '#!%s -x\n' % ei.nt_quote_arg(os.path.normpath
            (sys.executable))
        actual = ei.ScriptWriter.get_script_header('#!/usr/bin/python -x')
        assert actual == expected

        actual = ei.ScriptWriter.get_script_header('#!/usr/bin/python',
            executable=self.non_ascii_exe)
        expected = '#!%s -x\n' % self.non_ascii_exe
        assert actual == expected

        actual = ei.ScriptWriter.get_script_header('#!/usr/bin/python',
            executable='"'+self.exe_with_spaces+'"')
        expected = '#!"%s"\n' % self.exe_with_spaces
        assert actual == expected

    @pytest.mark.xfail(
        compat.PY3 and os.environ.get("LC_CTYPE") in ("C", "POSIX"),
        reason="Test fails in this locale on Python 3"
    )
    @mock.patch.dict(sys.modules, java=mock.Mock(lang=mock.Mock(System=
        mock.Mock(getProperty=mock.Mock(return_value="")))))
    @mock.patch('sys.platform', 'java1.5.0_13')
    def test_get_script_header_jython_workaround(self, tmpdir):
        # Create a mock sys.executable that uses a shebang line
        header = DALS("""
            #!/usr/bin/python
            # -*- coding: utf-8 -*-
            """)
        exe = tmpdir / 'exe.py'
        with exe.open('w') as f:
            f.write(header)
        exe = str(exe)

        header = ei.ScriptWriter.get_script_header('#!/usr/local/bin/python',
            executable=exe)
        assert header == '#!/usr/bin/env %s\n' % exe

        expect_out = 'stdout' if sys.version_info < (2,7) else 'stderr'

        with contexts.quiet() as (stdout, stderr):
            # When options are included, generate a broken shebang line
            # with a warning emitted
            candidate = ei.ScriptWriter.get_script_header('#!/usr/bin/python -x',
                executable=exe)
            assert candidate == '#!%s -x\n' % exe
            output = locals()[expect_out]
            assert 'Unable to adapt shebang line' in output.getvalue()

        with contexts.quiet() as (stdout, stderr):
            candidate = ei.ScriptWriter.get_script_header('#!/usr/bin/python',
                executable=self.non_ascii_exe)
            assert candidate == '#!%s -x\n' % self.non_ascii_exe
            output = locals()[expect_out]
            assert 'Unable to adapt shebang line' in output.getvalue()


class TestCommandSpec:
    def test_custom_launch_command(self):
        """
        Show how a custom CommandSpec could be used to specify a #! executable
        which takes parameters.
        """
        cmd = ei.CommandSpec(['/usr/bin/env', 'python3'])
        assert cmd.as_header() == '#!/usr/bin/env python3\n'

    def test_from_param_for_CommandSpec_is_passthrough(self):
        """
        from_param should return an instance of a CommandSpec
        """
        cmd = ei.CommandSpec(['python'])
        cmd_new = ei.CommandSpec.from_param(cmd)
        assert cmd is cmd_new

    def test_from_environment_with_spaces_in_executable(self):
        with mock.patch('sys.executable', TestScriptHeader.exe_with_spaces):
            cmd = ei.CommandSpec.from_environment()
        assert len(cmd) == 1
        assert cmd.as_header().startswith('#!"')

    def test_from_simple_string_uses_shlex(self):
        """
        In order to support `executable = /usr/bin/env my-python`, make sure
        from_param invokes shlex on that input.
        """
        cmd = ei.CommandSpec.from_param('/usr/bin/env my-python')
        assert len(cmd) == 2
        assert '"' not in cmd.as_header()

    def test_sys_executable(self):
        """
        CommandSpec.from_string(sys.executable) should contain just that param.
        """
        writer = ei.ScriptWriter.best()
        cmd = writer.command_spec_class.from_string(sys.executable)
        assert len(cmd) == 1
        assert cmd[0] == sys.executable


class TestWindowsScriptWriter:
    def test_header(self):
        hdr = ei.WindowsScriptWriter.get_script_header('')
        assert hdr.startswith('#!')
        assert hdr.endswith('\n')
        hdr = hdr.lstrip('#!')
        hdr = hdr.rstrip('\n')
        # header should not start with an escaped quote
        assert not hdr.startswith('\\"')
