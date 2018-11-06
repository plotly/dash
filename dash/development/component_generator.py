from __future__ import print_function

import json
import sys
import subprocess
import shlex
import os

from .base_component import generate_class_file


def generate_components(component_src, output_dir):
    is_windows = sys.platform == 'win32'

    extract_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'extract-meta.js'
    ))

    os.environ['NODE_PATH'] = 'node_modules'
    cmd = shlex.split('node {} {}'.format(extract_path, component_src),
                      posix=not is_windows)

    namespace = os.path.basename(output_dir)

    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=not is_windows)
    out, err = proc.communicate()
    status = proc.poll()

    if err:
        print(err.decode())

    if not out:
        print(
            'Error generating {} metadata in {} (status={})'.format(
                namespace, output_dir, status),
            file=sys.stderr)
        sys.exit(-1)
    metadata = json.loads(out.decode())
    for component_path, component_data in metadata.items():
        name = component_path.split('/').pop().split('.')[0]
        generate_class_file(
            name,
            component_data['props'],
            component_data['description'],
            namespace
        )
        print('Generated {}/{}.py'.format(namespace, name))


def cli():
    # pylint: disable=unbalanced-tuple-unpacking
    src, out = sys.argv[1:]
    generate_components(src, out)


if __name__ == '__main__':
    cli()
