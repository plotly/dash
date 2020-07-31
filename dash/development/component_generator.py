from __future__ import print_function
from collections import OrderedDict

import json
import sys
import subprocess
import shlex
import os
import argparse
import shutil
import functools

import pkg_resources
import yaml

from ._r_components_generation import write_class_file
from ._r_components_generation import generate_exports
from ._py_components_generation import generate_class_file
from ._py_components_generation import generate_imports
from ._py_components_generation import generate_classes_files
from ._jl_components_generation import generate_struct_file
from ._jl_components_generation import generate_module


reserved_words = [
    "UNDEFINED",
    "REQUIRED",
    "to_plotly_json",
    "available_properties",
    "available_wildcard_properties",
    "_.*",
]


class _CombinedFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


# pylint: disable=too-many-locals, too-many-arguments
def generate_components(
    components_source,
    project_shortname,
    package_info_filename="package.json",
    ignore="^_",
    rprefix=None,
    rdepends="",
    rimports="",
    rsuggests="",
    jlprefix=None,
):

    project_shortname = project_shortname.replace("-", "_").rstrip("/\\")

    is_windows = sys.platform == "win32"

    extract_path = pkg_resources.resource_filename("dash", "extract-meta.js")

    reserved_patterns = "|".join("^{}$".format(p) for p in reserved_words)

    os.environ["NODE_PATH"] = "node_modules"

    cmd = shlex.split(
        'node {} "{}" "{}" {}'.format(
            extract_path, ignore, reserved_patterns, components_source
        ),
        posix=not is_windows,
    )

    shutil.copyfile(
        "package.json", os.path.join(project_shortname, package_info_filename)
    )

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_windows
    )
    out, err = proc.communicate()
    status = proc.poll()

    if err:
        print(err.decode(), file=sys.stderr)

    if not out:
        print(
            "Error generating metadata in {} (status={})".format(
                project_shortname, status
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    metadata = safe_json_loads(out.decode("utf-8"))

    generator_methods = [generate_class_file]

    if rprefix is not None or jlprefix is not None:
        with open("package.json", "r") as f:
            pkg_data = safe_json_loads(f.read())

    if rprefix is not None:
        if not os.path.exists("man"):
            os.makedirs("man")
        if not os.path.exists("R"):
            os.makedirs("R")
        if os.path.isfile("dash-info.yaml"):
            with open("dash-info.yaml") as yamldata:
                rpkg_data = yaml.safe_load(yamldata)
        else:
            rpkg_data = None
        generator_methods.append(
            functools.partial(write_class_file, prefix=rprefix, rpkg_data=rpkg_data)
        )

    if jlprefix is not None:
        generator_methods.append(
            functools.partial(generate_struct_file, prefix=jlprefix)
        )

    components = generate_classes_files(project_shortname, metadata, *generator_methods)

    with open(os.path.join(project_shortname, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    generate_imports(project_shortname, components)

    if rprefix is not None:
        generate_exports(
            project_shortname,
            components,
            metadata,
            pkg_data,
            rpkg_data,
            rprefix,
            rdepends,
            rimports,
            rsuggests,
        )

    if jlprefix is not None:
        generate_module(project_shortname, components, metadata, pkg_data, jlprefix)


def safe_json_loads(s):
    jsondata_unicode = json.loads(s, object_pairs_hook=OrderedDict)
    if sys.version_info[0] >= 3:
        return jsondata_unicode
    return byteify(jsondata_unicode)


def cli():
    parser = argparse.ArgumentParser(
        prog="dash-generate-components",
        formatter_class=_CombinedFormatter,
        description="Generate dash components by extracting the metadata "
        "using react-docgen. Then map the metadata to Python classes.",
    )
    parser.add_argument("components_source", help="React components source directory.")
    parser.add_argument(
        "project_shortname", help="Name of the project to export the classes files."
    )
    parser.add_argument(
        "-p",
        "--package-info-filename",
        default="package.json",
        help="The filename of the copied `package.json` to `project_shortname`",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        default="^_",
        help="Files/directories matching the pattern will be ignored",
    )
    parser.add_argument(
        "--r-prefix",
        help="Specify a prefix for Dash for R component names, write "
        "components to R dir, create R package.",
    )
    parser.add_argument(
        "--r-depends",
        default="",
        help="Specify a comma-separated list of R packages to be "
        "inserted into the Depends field of the DESCRIPTION file.",
    )
    parser.add_argument(
        "--r-imports",
        default="",
        help="Specify a comma-separated list of R packages to be "
        "inserted into the Imports field of the DESCRIPTION file.",
    )
    parser.add_argument(
        "--r-suggests",
        default="",
        help="Specify a comma-separated list of R packages to be "
        "inserted into the Suggests field of the DESCRIPTION file.",
    )
    parser.add_argument(
        "--jl-prefix",
        help="Specify a prefix for Dash for R component names, write "
        "components to R dir, create R package.",
    )

    args = parser.parse_args()
    generate_components(
        args.components_source,
        args.project_shortname,
        package_info_filename=args.package_info_filename,
        ignore=args.ignore,
        rprefix=args.r_prefix,
        rdepends=args.r_depends,
        rimports=args.r_imports,
        rsuggests=args.r_suggests,
        jlprefix=args.jl_prefix,
    )


# pylint: disable=undefined-variable
def byteify(input_object):
    if isinstance(input_object, dict):
        return OrderedDict(
            [(byteify(key), byteify(value)) for key, value in input_object.iteritems()]
        )
    if isinstance(input_object, list):
        return [byteify(element) for element in input_object]
    if isinstance(input_object, unicode):  # noqa:F821
        return input_object.encode("utf-8")
    return input_object


if __name__ == "__main__":
    cli()
