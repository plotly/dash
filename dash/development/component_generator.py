import os
import argparse

from .plugins.helpers import extract_metadata

from .plugins.R.generate import generate as r_generate
from .plugins.python.generate import generate as py_generate

class _CombinedFormatter(argparse.ArgumentDefaultsHelpFormatter,
                         argparse.RawDescriptionHelpFormatter):
    pass


def cli():
    parser = argparse.ArgumentParser(
        prog='dash-generate-components',
        formatter_class=_CombinedFormatter,
        description='Generate dash components by extracting the metadata '
        'using react-docgen. Then map the metadata to python classes.'
    )
    parser.add_argument('components_source',
                        help='React components source directory.')
    parser.add_argument(
        'project_shortname',
        help='Name of the project to export the classes files.'
    )
    parser.add_argument(
        '-p', '--package-info-filename',
        default='package.json',
        help='The filename of the copied `package.json` to `project_shortname`'
    )
    parser.add_argument(
        '-i', '--ignore',
        default='^_',
        help='Files/directories matching the pattern will be ignored'
    )
    parser.add_argument(
        '--r-prefix',
        help='Experimental: specify a prefix for DashR component names, write'
             'DashR components to R dir, create R package.'
    )
    parser.add_argument(
        '-d', '--dist',
        default=False,
        action='store_true',
        help='Generate into /dist folder'
    )

    args = parser.parse_args()
    generate_components(
        args.components_source,
        args.project_shortname,
        args.package_info_filename,
        ignore=args.ignore,
        r_prefix=args.r_prefix,
        use_dist=args.dist)


def generate_components(
    components_source,
    project_shortname,
    package_info_filename,
    ignore='^_',
    r_prefix=None,
    use_dist=False
):

    metadata = extract_metadata(components_source, ignore)
    project_shortname = project_shortname.replace('-', '_').rstrip('/\\')

    dist_python = os.path.join('dist', 'python') if use_dist else os.path.join('')
    dist_r = os.path.join('dist', 'R') if use_dist else os.path.join('')

    py_generate(project_shortname, package_info_filename, metadata, dist_python)
    r_generate(project_shortname, metadata, r_prefix, dist_r)


if __name__ == '__main__':
    cli()
