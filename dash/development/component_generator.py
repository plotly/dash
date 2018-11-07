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
        print(err.decode(), file=sys.stderr)

    if not out:
        print(
            'Error generating {} metadata in {} (status={})'.format(
                namespace, output_dir, status),
            file=sys.stderr)
        sys.exit(1)

    metadata = json.loads(out.decode())

    for component_path, component_data in metadata.items():
        name = component_path.split('/')[-1].split('.')[0]
        generate_class_file(
            name,
            component_data['props'],
            component_data['description'],
            namespace
        )
        print('Generated {}/{}.py'.format(namespace, name))

    with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f)


def cli():
    if len(sys.argv) != 3:
        print(
            'Invalid number of arguments'
            ' expected 2 but got {}\n\n'
            'Arguments: src output_directory'.format(len(sys.argv) - 1),
            file=sys.stderr
        )
        sys.exit(1)
    # pylint: disable=unbalanced-tuple-unpacking
    src, out = sys.argv[1:]
    generate_components(src, out)


if __name__ == '__main__':
    cli()
