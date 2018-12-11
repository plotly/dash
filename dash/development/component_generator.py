from __future__ import print_function

import json
import sys
import subprocess
import shlex
import os
import argparse
import shutil
import importlib
import functools

import pkg_resources

from ._r_components_generation import write_class_file_r
from ._r_components_generation import generate_exports_r
from ._py_components_generation import generate_class_file
from ._py_components_generation import generate_imports
from ._py_components_generation import generate_classes_files


class _CombinedFormatter(argparse.ArgumentDefaultsHelpFormatter,
                         argparse.RawDescriptionHelpFormatter):
    pass


# pylint: disable=too-many-locals
def generate_components(components_source, project_shortname,
                        package_info_filename='package.json',
                        generate_r_components=False,
                        rprefix=None):
    project_shortname = project_shortname.replace('-', '_').rstrip('/\\')

    # import component library module
    importlib.import_module(project_shortname)

    if rprefix:
        prefix = rprefix
    else:
        s = [
            x for x in project_shortname.split('_')
            if x not in ('dash', 'component', 'components')
        ]
        prefix = s[-1]
        print(
            'Warning: a component prefix was '
            'not provided. Using `{}`.'.format(prefix),
            file=sys.stderr
        )

    is_windows = sys.platform == 'win32'

    extract_path = pkg_resources.resource_filename('dash', 'extract-meta.js')

    os.environ['NODE_PATH'] = 'node_modules'
    cmd = shlex.split('node {} {}'.format(extract_path, components_source),
                      posix=not is_windows)

    shutil.copyfile('package.json',
                    os.path.join(project_shortname, package_info_filename))

    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=is_windows)
    out, err = proc.communicate()
    status = proc.poll()

    if err:
        print(err.decode(), file=sys.stderr)

    if not out:
        print(
            'Error generating metadata in {} (status={})'.format(
                project_shortname, status),
            file=sys.stderr)
        sys.exit(1)

    metadata = json.loads(out.decode())
    generator_methods = [generate_class_file]

    if generate_r_components:
        if not os.path.exists('man'):
            os.makedirs('man')
        if not os.path.exists('R'):
            os.makedirs('R')
        generator_methods.append(
            functools.partial(write_class_file_r, prefix=prefix))

    components = generate_classes_files(
        project_shortname,
        metadata,
        *generator_methods
    )

    with open(os.path.join(project_shortname, 'metadata.json'), 'w') as f:
        json.dump(metadata, f)

    generate_imports(project_shortname, components)

    if generate_r_components:
        with open('package.json', 'r') as f:
            pkg_data = json.load(f)

        generate_exports_r(
            project_shortname, components, metadata, pkg_data, prefix
        )


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
        '-r', '--rlang',
        action='store_true',
        help='Experimental: write DashR components to R dir, create R package'
    )
    parser.add_argument(
        '--r-prefix',
        help='Inserts a prefix string that will be prepended to DashR'
             'component names at generation time.'
    )

    args = parser.parse_args()
    generate_components(args.components_source, args.project_shortname,
                        package_info_filename=args.package_info_filename,
                        generate_r_components=args.rlang,
                        rprefix=args.r_prefix)


if __name__ == '__main__':
    cli()
