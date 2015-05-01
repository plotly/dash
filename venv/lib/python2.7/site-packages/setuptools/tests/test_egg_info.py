import os
import stat

import pytest

from . import environment
from .textwrap import DALS
from . import contexts


class TestEggInfo:

    setup_script = DALS("""
        from setuptools import setup

        setup(
            name='foo',
            py_modules=['hello'],
            entry_points={'console_scripts': ['hi = hello.run']},
            zip_safe=False,
        )
        """)

    def _create_project(self):
        with open('setup.py', 'w') as f:
            f.write(self.setup_script)

        with open('hello.py', 'w') as f:
            f.write(DALS("""
                def run():
                    print('hello')
                """))

    @pytest.yield_fixture
    def env(self):
        class Environment(str): pass

        with contexts.tempdir(prefix='setuptools-test.') as env_dir:
            env = Environment(env_dir)
            os.chmod(env_dir, stat.S_IRWXU)
            subs = 'home', 'lib', 'scripts', 'data', 'egg-base'
            env.paths = dict(
                (dirname, os.path.join(env_dir, dirname))
                for dirname in subs
            )
            list(map(os.mkdir, env.paths.values()))
            config = os.path.join(env.paths['home'], '.pydistutils.cfg')
            with open(config, 'w') as f:
                f.write(DALS("""
                    [egg_info]
                    egg-base = %(egg-base)s
                    """ % env.paths
                ))
            yield env

    def test_egg_base_installed_egg_info(self, tmpdir_cwd, env):
        self._create_project()

        environ = os.environ.copy().update(
            HOME=env.paths['home'],
        )
        cmd = [
            'install',
            '--home', env.paths['home'],
            '--install-lib', env.paths['lib'],
            '--install-scripts', env.paths['scripts'],
            '--install-data', env.paths['data'],
        ]
        code, data = environment.run_setup_py(
            cmd=cmd,
            pypath=os.pathsep.join([env.paths['lib'], str(tmpdir_cwd)]),
            data_stream=1,
            env=environ,
        )
        if code:
            raise AssertionError(data)

        actual = self._find_egg_info_files(env.paths['lib'])

        expected = [
            'PKG-INFO',
            'SOURCES.txt',
            'dependency_links.txt',
            'entry_points.txt',
            'not-zip-safe',
            'top_level.txt',
        ]
        assert sorted(actual) == expected

    def _find_egg_info_files(self, root):
        results = (
            filenames
            for dirpath, dirnames, filenames in os.walk(root)
            if os.path.basename(dirpath) == 'EGG-INFO'
        )
        # expect exactly one result
        result, = results
        return result
