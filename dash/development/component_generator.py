from __future__ import print_function

import json
import sys
import subprocess
import shlex
import os
import textwrap

from .base_component import generate_class_file


# pylint: disable=too-many-locals
def generate_components(component_src, project_shortname):
    is_windows = sys.platform == 'win32'

    extract_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'extract-meta.js'
    ))

    os.environ['NODE_PATH'] = 'node_modules'
    cmd = shlex.split('node {} {}'.format(extract_path, component_src),
                      posix=not is_windows)

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

    components = []

    for component_path, component_data in metadata.items():
        name = component_path.split('/')[-1].split('.')[0]
        components.append(name)
        generate_class_file(
            name,
            component_data['props'],
            component_data['description'],
            project_shortname
        )
        print('Generated {}/{}.py'.format(project_shortname, name))

    with open(os.path.join(project_shortname, 'metadata.json'), 'w') as f:
        json.dump(metadata, f)

    with open(os.path.join(project_shortname, '_imports_.py'), 'w') as f:
        f.write(textwrap.dedent(
            '''
            {}

            __all__ = [
            {}
            ]
            '''.format(
                '\n'.join('from {0} import {0}'.format(x) for x in components),
                ',\n'.join('    "{}"'.format(x) for x in components)
            )
        ).lstrip())


def cli():
    if len(sys.argv) != 3:
        print(
            'Invalid number of arguments'
            ' expected 2 but got {}\n\n'
            'Arguments: src project_shortname'.format(len(sys.argv) - 1),
            file=sys.stderr
        )
        sys.exit(1)
    # pylint: disable=unbalanced-tuple-unpacking
    src, project_shortname = sys.argv[1:]
    generate_components(src, project_shortname)


if __name__ == '__main__':
    cli()
