"""
Tests for msvc9compiler.
"""

import os
import contextlib
import distutils.errors

import pytest
try:
    from unittest import mock
except ImportError:
    import mock

from . import contexts

# importing only setuptools should apply the patch
__import__('setuptools')

pytest.importorskip("distutils.msvc9compiler")


def mock_reg(hkcu=None, hklm=None):
    """
    Return a mock for distutils.msvc9compiler.Reg, patched
    to mock out the functions that access the registry.
    """

    _winreg = getattr(distutils.msvc9compiler, '_winreg', None)
    winreg = getattr(distutils.msvc9compiler, 'winreg', _winreg)

    hives = {
        winreg.HKEY_CURRENT_USER: hkcu or {},
        winreg.HKEY_LOCAL_MACHINE: hklm or {},
    }

    @classmethod
    def read_keys(cls, base, key):
        """Return list of registry keys."""
        hive = hives.get(base, {})
        return [
            k.rpartition('\\')[2]
            for k in hive if k.startswith(key.lower())
        ]

    @classmethod
    def read_values(cls, base, key):
        """Return dict of registry keys and values."""
        hive = hives.get(base, {})
        return dict(
            (k.rpartition('\\')[2], hive[k])
            for k in hive if k.startswith(key.lower())
        )

    return mock.patch.multiple(distutils.msvc9compiler.Reg,
        read_keys=read_keys, read_values=read_values)


class TestModulePatch:
    """
    Ensure that importing setuptools is sufficient to replace
    the standard find_vcvarsall function with a version that
    recognizes the "Visual C++ for Python" package.
    """

    key_32 = r'software\microsoft\devdiv\vcforpython\9.0\installdir'
    key_64 = r'software\wow6432node\microsoft\devdiv\vcforpython\9.0\installdir'

    def test_patched(self):
        "Test the module is actually patched"
        mod_name = distutils.msvc9compiler.find_vcvarsall.__module__
        assert mod_name == "setuptools.msvc9_support", "find_vcvarsall unpatched"

    def test_no_registry_entryies_means_nothing_found(self):
        """
        No registry entries or environment variable should lead to an error
        directing the user to download vcpython27.
        """
        find_vcvarsall = distutils.msvc9compiler.find_vcvarsall
        query_vcvarsall = distutils.msvc9compiler.query_vcvarsall

        with contexts.environment(VS90COMNTOOLS=None):
            with mock_reg():
                assert find_vcvarsall(9.0) is None

                expected = distutils.errors.DistutilsPlatformError
                with pytest.raises(expected) as exc:
                    query_vcvarsall(9.0)
                assert 'aka.ms/vcpython27' in str(exc)

    @pytest.yield_fixture
    def user_preferred_setting(self):
        """
        Set up environment with different install dirs for user vs. system
        and yield the user_install_dir for the expected result.
        """
        with self.mock_install_dir() as user_install_dir:
            with self.mock_install_dir() as system_install_dir:
                reg = mock_reg(
                    hkcu={
                        self.key_32: user_install_dir,
                    },
                    hklm={
                        self.key_32: system_install_dir,
                        self.key_64: system_install_dir,
                    },
                )
                with reg:
                    yield user_install_dir

    def test_prefer_current_user(self, user_preferred_setting):
        """
        Ensure user's settings are preferred.
        """
        result = distutils.msvc9compiler.find_vcvarsall(9.0)
        expected = os.path.join(user_preferred_setting, 'vcvarsall.bat')
        assert expected == result

    @pytest.yield_fixture
    def local_machine_setting(self):
        """
        Set up environment with only the system environment configured.
        """
        with self.mock_install_dir() as system_install_dir:
            reg = mock_reg(
                hklm={
                    self.key_32: system_install_dir,
                },
            )
            with reg:
                yield system_install_dir

    def test_local_machine_recognized(self, local_machine_setting):
        """
        Ensure machine setting is honored if user settings are not present.
        """
        result = distutils.msvc9compiler.find_vcvarsall(9.0)
        expected = os.path.join(local_machine_setting, 'vcvarsall.bat')
        assert expected == result

    @pytest.yield_fixture
    def x64_preferred_setting(self):
        """
        Set up environment with 64-bit and 32-bit system settings configured
        and yield the canonical location.
        """
        with self.mock_install_dir() as x32_dir:
            with self.mock_install_dir() as x64_dir:
                reg = mock_reg(
                    hklm={
                        # This *should* only exist on 32-bit machines
                        self.key_32: x32_dir,
                        # This *should* only exist on 64-bit machines
                        self.key_64: x64_dir,
                    },
                )
                with reg:
                    yield x32_dir

    def test_ensure_64_bit_preferred(self, x64_preferred_setting):
        """
        Ensure 64-bit system key is preferred.
        """
        result = distutils.msvc9compiler.find_vcvarsall(9.0)
        expected = os.path.join(x64_preferred_setting, 'vcvarsall.bat')
        assert expected == result

    @staticmethod
    @contextlib.contextmanager
    def mock_install_dir():
        """
        Make a mock install dir in a unique location so that tests can
        distinguish which dir was detected in a given scenario.
        """
        with contexts.tempdir() as result:
            vcvarsall = os.path.join(result, 'vcvarsall.bat')
            with open(vcvarsall, 'w'):
                pass
            yield result
