from collections import OrderedDict
import glob
import json
import os
import pkg_resources
import shlex
import shutil
import subprocess
import sys

# pylint: disable=undefined-variable
def byteify(input_object):
    if isinstance(input_object, dict):
        return OrderedDict([
            (byteify(key), byteify(value))
            for key, value in input_object.iteritems()
        ])
    elif isinstance(input_object, list):
        return [byteify(element) for element in input_object]
    elif isinstance(input_object, unicode):  # noqa:F821
        return input_object.encode('utf-8')
    return input_object

def compile(project_shortname, metadata, compiler):
    components = []
    results = []
    for component_path, component_data in metadata.items():
        component_name = component_path.split('/')[-1].split('.')[0]
        components.append(component_name)

        results.append(
            compiler(
                component_name,
                component_data['props'],
                component_data['description'],
                project_shortname
            ) if compiler is not None else None
        )

    return components, results

def extract_metadata(components_source, ignore):
    extract_path = pkg_resources.resource_filename('dash', 'extract-meta.js')
    is_windows = sys.platform == 'win32'

    os.environ['NODE_PATH'] = 'node_modules'
    cmd = shlex.split(
        'node {} {} {}'.format(extract_path, ignore, components_source),
        posix=not is_windows
    )

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

    jsondata_unicode = json.loads(out.decode(), object_pairs_hook=OrderedDict)

    if sys.version_info[0] >= 3:
        metadata = jsondata_unicode
    else:
        metadata = byteify(jsondata_unicode)

    return metadata

def get_package_data():
    with open('package.json', 'r') as f:
        jsondata_unicode = json.load(f, object_pairs_hook=OrderedDict)

    return jsondata_unicode if sys.version_info[0] >= 3 else byteify(jsondata_unicode)

def glob_js(source, target):
    for javascript in glob.glob(source + '/*.js'):
        shutil.copy(javascript, target)

    for css in glob.glob(source + '{}/*.css'):
        shutil.copy(css, target)

    for sourcemap in glob.glob(source + '/*.map'):
        shutil.copy(sourcemap, target)