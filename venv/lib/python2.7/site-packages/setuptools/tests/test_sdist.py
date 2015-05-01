# -*- coding: utf-8 -*-
"""sdist tests"""

import locale
import os
import shutil
import sys
import tempfile
import unicodedata
import contextlib

import pytest

import pkg_resources
from setuptools.compat import StringIO, unicode, PY3, PY2
from setuptools.command.sdist import sdist
from setuptools.command.egg_info import manifest_maker
from setuptools.dist import Distribution

SETUP_ATTRS = {
    'name': 'sdist_test',
    'version': '0.0',
    'packages': ['sdist_test'],
    'package_data': {'sdist_test': ['*.txt']}
}


SETUP_PY = """\
from setuptools import setup

setup(**%r)
""" % SETUP_ATTRS


if PY3:
    LATIN1_FILENAME = 'smörbröd.py'.encode('latin-1')
else:
    LATIN1_FILENAME = 'sm\xf6rbr\xf6d.py'


# Cannot use context manager because of Python 2.4
@contextlib.contextmanager
def quiet():
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = StringIO(), StringIO()
    try:
        yield
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


# Fake byte literals for Python <= 2.5
def b(s, encoding='utf-8'):
    if PY3:
        return s.encode(encoding)
    return s


# Convert to POSIX path
def posix(path):
    if PY3 and not isinstance(path, str):
        return path.replace(os.sep.encode('ascii'), b('/'))
    else:
        return path.replace(os.sep, '/')


# HFS Plus uses decomposed UTF-8
def decompose(path):
    if isinstance(path, unicode):
        return unicodedata.normalize('NFD', path)
    try:
        path = path.decode('utf-8')
        path = unicodedata.normalize('NFD', path)
        path = path.encode('utf-8')
    except UnicodeError:
        pass  # Not UTF-8
    return path


class TestSdistTest:

    def setup_method(self, method):
        self.temp_dir = tempfile.mkdtemp()
        f = open(os.path.join(self.temp_dir, 'setup.py'), 'w')
        f.write(SETUP_PY)
        f.close()

        # Set up the rest of the test package
        test_pkg = os.path.join(self.temp_dir, 'sdist_test')
        os.mkdir(test_pkg)
        # *.rst was not included in package_data, so c.rst should not be
        # automatically added to the manifest when not under version control
        for fname in ['__init__.py', 'a.txt', 'b.txt', 'c.rst']:
            # Just touch the files; their contents are irrelevant
            open(os.path.join(test_pkg, fname), 'w').close()

        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def teardown_method(self, method):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.temp_dir)

    def test_package_data_in_sdist(self):
        """Regression test for pull request #4: ensures that files listed in
        package_data are included in the manifest even if they're not added to
        version control.
        """

        dist = Distribution(SETUP_ATTRS)
        dist.script_name = 'setup.py'
        cmd = sdist(dist)
        cmd.ensure_finalized()

        with quiet():
            cmd.run()

        manifest = cmd.filelist.files
        assert os.path.join('sdist_test', 'a.txt') in manifest
        assert os.path.join('sdist_test', 'b.txt') in manifest
        assert os.path.join('sdist_test', 'c.rst') not in manifest


    def test_defaults_case_sensitivity(self):
        """
            Make sure default files (README.*, etc.) are added in a case-sensitive
            way to avoid problems with packages built on Windows.
        """

        open(os.path.join(self.temp_dir, 'readme.rst'), 'w').close()
        open(os.path.join(self.temp_dir, 'SETUP.cfg'), 'w').close()

        dist = Distribution(SETUP_ATTRS)
        # the extension deliberately capitalized for this test
        # to make sure the actual filename (not capitalized) gets added
        # to the manifest
        dist.script_name = 'setup.PY'
        cmd = sdist(dist)
        cmd.ensure_finalized()

        with quiet():
            cmd.run()

        # lowercase all names so we can test in a case-insensitive way to make sure the files are not included
        manifest = map(lambda x: x.lower(), cmd.filelist.files)
        assert 'readme.rst' not in manifest, manifest
        assert 'setup.py' not in manifest, manifest
        assert 'setup.cfg' not in manifest, manifest

    def test_manifest_is_written_with_utf8_encoding(self):
        # Test for #303.
        dist = Distribution(SETUP_ATTRS)
        dist.script_name = 'setup.py'
        mm = manifest_maker(dist)
        mm.manifest = os.path.join('sdist_test.egg-info', 'SOURCES.txt')
        os.mkdir('sdist_test.egg-info')

        # UTF-8 filename
        filename = os.path.join('sdist_test', 'smörbröd.py')

        # Must create the file or it will get stripped.
        open(filename, 'w').close()

        # Add UTF-8 filename and write manifest
        with quiet():
            mm.run()
            mm.filelist.append(filename)
            mm.write_manifest()

        manifest = open(mm.manifest, 'rbU')
        contents = manifest.read()
        manifest.close()

        # The manifest should be UTF-8 encoded
        u_contents = contents.decode('UTF-8')

        # The manifest should contain the UTF-8 filename
        if PY2:
            fs_enc = sys.getfilesystemencoding()
            filename = filename.decode(fs_enc)

        assert posix(filename) in u_contents

    # Python 3 only
    if PY3:

        def test_write_manifest_allows_utf8_filenames(self):
            # Test for #303.
            dist = Distribution(SETUP_ATTRS)
            dist.script_name = 'setup.py'
            mm = manifest_maker(dist)
            mm.manifest = os.path.join('sdist_test.egg-info', 'SOURCES.txt')
            os.mkdir('sdist_test.egg-info')

            # UTF-8 filename
            filename = os.path.join(b('sdist_test'), b('smörbröd.py'))

            # Must touch the file or risk removal
            open(filename, "w").close()

            # Add filename and write manifest
            with quiet():
                mm.run()
                u_filename = filename.decode('utf-8')
                mm.filelist.files.append(u_filename)
                # Re-write manifest
                mm.write_manifest()

            manifest = open(mm.manifest, 'rbU')
            contents = manifest.read()
            manifest.close()

            # The manifest should be UTF-8 encoded
            contents.decode('UTF-8')

            # The manifest should contain the UTF-8 filename
            assert posix(filename) in contents

            # The filelist should have been updated as well
            assert u_filename in mm.filelist.files

        def test_write_manifest_skips_non_utf8_filenames(self):
            """
            Files that cannot be encoded to UTF-8 (specifically, those that
            weren't originally successfully decoded and have surrogate
            escapes) should be omitted from the manifest.
            See https://bitbucket.org/tarek/distribute/issue/303 for history.
            """
            dist = Distribution(SETUP_ATTRS)
            dist.script_name = 'setup.py'
            mm = manifest_maker(dist)
            mm.manifest = os.path.join('sdist_test.egg-info', 'SOURCES.txt')
            os.mkdir('sdist_test.egg-info')

            # Latin-1 filename
            filename = os.path.join(b('sdist_test'), LATIN1_FILENAME)

            # Add filename with surrogates and write manifest
            with quiet():
                mm.run()
                u_filename = filename.decode('utf-8', 'surrogateescape')
                mm.filelist.append(u_filename)
                # Re-write manifest
                mm.write_manifest()

            manifest = open(mm.manifest, 'rbU')
            contents = manifest.read()
            manifest.close()

            # The manifest should be UTF-8 encoded
            contents.decode('UTF-8')

            # The Latin-1 filename should have been skipped
            assert posix(filename) not in contents

            # The filelist should have been updated as well
            assert u_filename not in mm.filelist.files

    def test_manifest_is_read_with_utf8_encoding(self):
        # Test for #303.
        dist = Distribution(SETUP_ATTRS)
        dist.script_name = 'setup.py'
        cmd = sdist(dist)
        cmd.ensure_finalized()

        # Create manifest
        with quiet():
            cmd.run()

        # Add UTF-8 filename to manifest
        filename = os.path.join(b('sdist_test'), b('smörbröd.py'))
        cmd.manifest = os.path.join('sdist_test.egg-info', 'SOURCES.txt')
        manifest = open(cmd.manifest, 'ab')
        manifest.write(b('\n') + filename)
        manifest.close()

        # The file must exist to be included in the filelist
        open(filename, 'w').close()

        # Re-read manifest
        cmd.filelist.files = []
        with quiet():
            cmd.read_manifest()

        # The filelist should contain the UTF-8 filename
        if PY3:
            filename = filename.decode('utf-8')
        assert filename in cmd.filelist.files

    # Python 3 only
    if PY3:

        def test_read_manifest_skips_non_utf8_filenames(self):
            # Test for #303.
            dist = Distribution(SETUP_ATTRS)
            dist.script_name = 'setup.py'
            cmd = sdist(dist)
            cmd.ensure_finalized()

            # Create manifest
            with quiet():
                cmd.run()

            # Add Latin-1 filename to manifest
            filename = os.path.join(b('sdist_test'), LATIN1_FILENAME)
            cmd.manifest = os.path.join('sdist_test.egg-info', 'SOURCES.txt')
            manifest = open(cmd.manifest, 'ab')
            manifest.write(b('\n') + filename)
            manifest.close()

            # The file must exist to be included in the filelist
            open(filename, 'w').close()

            # Re-read manifest
            cmd.filelist.files = []
            with quiet():
                cmd.read_manifest()

            # The Latin-1 filename should have been skipped
            filename = filename.decode('latin-1')
            assert filename not in cmd.filelist.files

    @pytest.mark.skipif(PY3 and locale.getpreferredencoding() != 'UTF-8',
        reason='Unittest fails if locale is not utf-8 but the manifests is '
            'recorded correctly')
    def test_sdist_with_utf8_encoded_filename(self):
        # Test for #303.
        dist = Distribution(SETUP_ATTRS)
        dist.script_name = 'setup.py'
        cmd = sdist(dist)
        cmd.ensure_finalized()

        # UTF-8 filename
        filename = os.path.join(b('sdist_test'), b('smörbröd.py'))
        open(filename, 'w').close()

        with quiet():
            cmd.run()

        if sys.platform == 'darwin':
            filename = decompose(filename)

        if PY3:
            fs_enc = sys.getfilesystemencoding()

            if sys.platform == 'win32':
                if fs_enc == 'cp1252':
                    # Python 3 mangles the UTF-8 filename
                    filename = filename.decode('cp1252')
                    assert filename in cmd.filelist.files
                else:
                    filename = filename.decode('mbcs')
                    assert filename in cmd.filelist.files
            else:
                filename = filename.decode('utf-8')
                assert filename in cmd.filelist.files
        else:
            assert filename in cmd.filelist.files

    def test_sdist_with_latin1_encoded_filename(self):
        # Test for #303.
        dist = Distribution(SETUP_ATTRS)
        dist.script_name = 'setup.py'
        cmd = sdist(dist)
        cmd.ensure_finalized()

        # Latin-1 filename
        filename = os.path.join(b('sdist_test'), LATIN1_FILENAME)
        open(filename, 'w').close()
        assert os.path.isfile(filename)

        with quiet():
            cmd.run()

        if PY3:
            # not all windows systems have a default FS encoding of cp1252
            if sys.platform == 'win32':
                # Latin-1 is similar to Windows-1252 however
                # on mbcs filesys it is not in latin-1 encoding
                fs_enc = sys.getfilesystemencoding()
                if fs_enc == 'mbcs':
                    filename = filename.decode('mbcs')
                else:
                    filename = filename.decode('latin-1')

                assert filename in cmd.filelist.files
            else:
                # The Latin-1 filename should have been skipped
                filename = filename.decode('latin-1')
                filename not in cmd.filelist.files
        else:
            # Under Python 2 there seems to be no decoded string in the
            # filelist.  However, due to decode and encoding of the
            # file name to get utf-8 Manifest the latin1 maybe excluded
            try:
                # fs_enc should match how one is expect the decoding to
                # be proformed for the manifest output.
                fs_enc = sys.getfilesystemencoding()
                filename.decode(fs_enc)
                assert filename in cmd.filelist.files
            except UnicodeDecodeError:
                filename not in cmd.filelist.files


def test_default_revctrl():
    """
    When _default_revctrl was removed from the `setuptools.command.sdist`
    module in 10.0, it broke some systems which keep an old install of
    setuptools (Distribute) around. Those old versions require that the
    setuptools package continue to implement that interface, so this
    function provides that interface, stubbed. See #320 for details.

    This interface must be maintained until Ubuntu 12.04 is no longer
    supported (by Setuptools).
    """
    ep_def = 'svn_cvs = setuptools.command.sdist:_default_revctrl'
    ep = pkg_resources.EntryPoint.parse(ep_def)
    res = ep.resolve()
    assert hasattr(res, '__iter__')
