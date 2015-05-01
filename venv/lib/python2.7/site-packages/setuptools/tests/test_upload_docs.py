import os
import zipfile
import contextlib

import pytest

from setuptools.command.upload_docs import upload_docs
from setuptools.dist import Distribution

from .textwrap import DALS
from . import contexts


SETUP_PY = DALS(
    """
    from setuptools import setup

    setup(name='foo')
    """)


@pytest.fixture
def sample_project(tmpdir_cwd):
    # setup.py
    with open('setup.py', 'wt') as f:
        f.write(SETUP_PY)

    os.mkdir('build')

    # A test document.
    with open('build/index.html', 'w') as f:
        f.write("Hello world.")

    # An empty folder.
    os.mkdir('build/empty')


@pytest.mark.usefixtures('sample_project')
@pytest.mark.usefixtures('user_override')
class TestUploadDocsTest:

    def test_create_zipfile(self):
        """
        Ensure zipfile creation handles common cases, including a folder
        containing an empty folder.
        """

        dist = Distribution()

        cmd = upload_docs(dist)
        cmd.target_dir = cmd.upload_dir = 'build'
        with contexts.tempdir() as tmp_dir:
            tmp_file = os.path.join(tmp_dir, 'foo.zip')
            zip_file = cmd.create_zipfile(tmp_file)

            assert zipfile.is_zipfile(tmp_file)

            with contextlib.closing(zipfile.ZipFile(tmp_file)) as zip_file:
                assert zip_file.namelist() == ['index.html']
