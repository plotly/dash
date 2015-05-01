"""develop tests
"""
import os
import types

import pytest

import pkg_resources
import setuptools.sandbox
from setuptools.sandbox import DirectorySandbox


class TestSandbox:

    def test_devnull(self, tmpdir):
        sandbox = DirectorySandbox(str(tmpdir))
        sandbox.run(self._file_writer(os.devnull))

    @staticmethod
    def _file_writer(path):
        def do_write():
            with open(path, 'w') as f:
                f.write('xxx')
        return do_write

    def test_win32com(self, tmpdir):
        """
        win32com should not be prevented from caching COM interfaces
        in gen_py.
        """
        win32com = pytest.importorskip('win32com')
        gen_py = win32com.__gen_path__
        target = os.path.join(gen_py, 'test_write')
        sandbox = DirectorySandbox(str(tmpdir))
        try:
            # attempt to create gen_py file
            sandbox.run(self._file_writer(target))
        finally:
            if os.path.exists(target):
                os.remove(target)

    def test_setup_py_with_BOM(self):
        """
        It should be possible to execute a setup.py with a Byte Order Mark
        """
        target = pkg_resources.resource_filename(__name__,
            'script-with-bom.py')
        namespace = types.ModuleType('namespace')
        setuptools.sandbox._execfile(target, vars(namespace))
        assert namespace.result == 'passed'

    def test_setup_py_with_CRLF(self, tmpdir):
        setup_py = tmpdir / 'setup.py'
        with setup_py.open('wb') as stream:
            stream.write(b'"degenerate script"\r\n')
        setuptools.sandbox._execfile(str(setup_py), globals())


class TestExceptionSaver:
    def test_exception_trapped(self):
        with setuptools.sandbox.ExceptionSaver():
            raise ValueError("details")

    def test_exception_resumed(self):
        with setuptools.sandbox.ExceptionSaver() as saved_exc:
            raise ValueError("details")

        with pytest.raises(ValueError) as caught:
            saved_exc.resume()

        assert isinstance(caught.value, ValueError)
        assert str(caught.value) == 'details'

    def test_exception_reconstructed(self):
        orig_exc = ValueError("details")

        with setuptools.sandbox.ExceptionSaver() as saved_exc:
            raise orig_exc

        with pytest.raises(ValueError) as caught:
            saved_exc.resume()

        assert isinstance(caught.value, ValueError)
        assert caught.value is not orig_exc

    def test_no_exception_passes_quietly(self):
        with setuptools.sandbox.ExceptionSaver() as saved_exc:
            pass

        saved_exc.resume()

    def test_unpickleable_exception(self):
        class CantPickleThis(Exception):
            "This Exception is unpickleable because it's not in globals"

        with setuptools.sandbox.ExceptionSaver() as saved_exc:
            raise CantPickleThis('detail')

        with pytest.raises(setuptools.sandbox.UnpickleableException) as caught:
            saved_exc.resume()

        assert str(caught.value) == "CantPickleThis('detail',)"
