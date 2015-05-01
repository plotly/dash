import distutils.command.build_ext as orig

from setuptools.command.build_ext import build_ext
from setuptools.dist import Distribution

class TestBuildExt:
    def test_get_ext_filename(self):
        """
        Setuptools needs to give back the same
        result as distutils, even if the fullname
        is not in ext_map.
        """
        dist = Distribution()
        cmd = build_ext(dist)
        cmd.ext_map['foo/bar'] = ''
        res = cmd.get_ext_filename('foo')
        wanted = orig.build_ext.get_ext_filename(cmd, 'foo')
        assert res == wanted
