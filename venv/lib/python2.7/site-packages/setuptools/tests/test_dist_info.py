"""Test .dist-info style distributions.
"""
import os
import shutil
import tempfile

import pytest

import pkg_resources
from .textwrap import DALS


class TestDistInfo:

    def test_distinfo(self):
        dists = dict(
            (d.project_name, d)
            for d in pkg_resources.find_distributions(self.tmpdir)
        )

        assert len(dists) == 2, dists

        unversioned = dists['UnversionedDistribution']
        versioned = dists['VersionedDistribution']

        assert versioned.version == '2.718' # from filename
        assert unversioned.version == '0.3' # from METADATA

    @pytest.mark.importorskip('ast')
    def test_conditional_dependencies(self):
        specs = 'splort==4', 'quux>=1.1'
        requires = list(map(pkg_resources.Requirement.parse, specs))

        for d in pkg_resources.find_distributions(self.tmpdir):
            assert d.requires() == requires[:1]
            assert d.requires(extras=('baz',)) == requires
            assert d.extras == ['baz']

    metadata_template = DALS("""
        Metadata-Version: 1.2
        Name: {name}
        {version}
        Requires-Dist: splort (==4)
        Provides-Extra: baz
        Requires-Dist: quux (>=1.1); extra == 'baz'
        """)

    def setup_method(self, method):
        self.tmpdir = tempfile.mkdtemp()
        dist_info_name = 'VersionedDistribution-2.718.dist-info'
        versioned = os.path.join(self.tmpdir, dist_info_name)
        os.mkdir(versioned)
        with open(os.path.join(versioned, 'METADATA'), 'w+') as metadata_file:
            metadata = self.metadata_template.format(
                name='VersionedDistribution',
                version='',
            ).replace('\n\n', '\n')
            metadata_file.write(metadata)
        dist_info_name = 'UnversionedDistribution.dist-info'
        unversioned = os.path.join(self.tmpdir, dist_info_name)
        os.mkdir(unversioned)
        with open(os.path.join(unversioned, 'METADATA'), 'w+') as metadata_file:
            metadata = self.metadata_template.format(
                name='UnversionedDistribution',
                version='Version: 0.3',
            )
            metadata_file.write(metadata)

    def teardown_method(self, method):
        shutil.rmtree(self.tmpdir)
