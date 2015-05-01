"""develop tests
"""
import os
import re

import pytest

from setuptools.dist import Distribution

from . import contexts

SETUP_PY = """\
from setuptools import setup

setup(name='foo', py_modules=['hi'])
"""

@pytest.yield_fixture
def setup_context(tmpdir):
    with (tmpdir/'setup.py').open('w') as f:
        f.write(SETUP_PY)
    with (tmpdir/'hi.py').open('w') as f:
        f.write('1\n')
    with tmpdir.as_cwd():
        yield tmpdir


class Test:
    def test_bdist_egg(self, setup_context, user_override):
        dist = Distribution(dict(
            script_name='setup.py',
            script_args=['bdist_egg'],
            name='foo',
            py_modules=['hi']
            ))
        os.makedirs(os.path.join('build', 'src'))
        with contexts.quiet():
            dist.parse_command_line()
            dist.run_commands()

        # let's see if we got our egg link at the right place
        [content] = os.listdir('dist')
        assert re.match('foo-0.0.0-py[23].\d.egg$', content)
