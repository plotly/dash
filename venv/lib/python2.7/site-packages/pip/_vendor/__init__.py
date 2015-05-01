"""
pip._vendor is for vendoring dependencies of pip to prevent needing pip to
depend on something external.

Files inside of pip._vendor should be considered immutable and should only be
updated to versions from upstream.
"""
from __future__ import absolute_import

import glob
import os.path
import sys


# By default, look in this directory for a bunch of .whl files which we will
# add to the beginning of sys.path before attempting to import anything. This
# is done to support downstream re-distributors like Debian and Fedora who
# wish to create their own Wheels for our dependencies to aid in debundling.
WHEEL_DIR = os.path.abspath(os.path.dirname(__file__))

# Actually look inside of WHEEL_DIR to find .whl files and add them to the
# front of our sys.path.
sys.path = glob.glob(os.path.join(WHEEL_DIR, "*.whl")) + sys.path


class VendorAlias(object):

    def __init__(self, package_names):
        self._package_names = package_names
        self._vendor_name = __name__
        self._vendor_pkg = self._vendor_name + "."
        self._vendor_pkgs = [
            self._vendor_pkg + name for name in self._package_names
        ]

    def find_module(self, fullname, path=None):
        if fullname.startswith(self._vendor_pkg):
            return self

    def load_module(self, name):
        # Ensure that this only works for the vendored name
        if not name.startswith(self._vendor_pkg):
            raise ImportError(
                "Cannot import %s, must be a subpackage of '%s'." % (
                    name, self._vendor_name,
                )
            )
        if not (name == self._vendor_name or
                any(name.startswith(pkg) for pkg in self._vendor_pkgs)):
            raise ImportError(
                "Cannot import %s, must be one of %s." % (
                    name, self._vendor_pkgs
                )
            )

        # Check to see if we already have this item in sys.modules, if we do
        # then simply return that.
        if name in sys.modules:
            return sys.modules[name]

        # Check to see if we can import the vendor name
        try:
            # We do this dance here because we want to try and import this
            # module without hitting a recursion error because of a bunch of
            # VendorAlias instances on sys.meta_path
            real_meta_path = sys.meta_path[:]
            try:
                sys.meta_path = [
                    m for m in sys.meta_path
                    if not isinstance(m, VendorAlias)
                ]
                __import__(name)
                module = sys.modules[name]
            finally:
                # Re-add any additions to sys.meta_path that were made while
                # during the import we just did, otherwise things like
                # pip._vendor.six.moves will fail.
                for m in sys.meta_path:
                    if m not in real_meta_path:
                        real_meta_path.append(m)

                # Restore sys.meta_path with any new items.
                sys.meta_path = real_meta_path
        except ImportError:
            # We can't import the vendor name, so we'll try to import the
            # "real" name.
            real_name = name[len(self._vendor_pkg):]
            try:
                __import__(real_name)
                module = sys.modules[real_name]
            except ImportError:
                raise ImportError("No module named '%s'" % (name,))

        # If we've gotten here we've found the module we're looking for, either
        # as part of our vendored package, or as the real name, so we'll add
        # it to sys.modules as the vendored name so that we don't have to do
        # the lookup again.
        sys.modules[name] = module

        # Finally, return the loaded module
        return module


sys.meta_path.append(VendorAlias([
    "_markerlib", "cachecontrol", "certifi", "colorama", "distlib", "html5lib",
    "ipaddress", "lockfile", "packaging", "pkg_resources", "progress",
    "requests", "retrying", "six",
]))
