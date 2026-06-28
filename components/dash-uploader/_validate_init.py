"""
DO NOT MODIFY
This file is used to validate your publish settings.
"""
from __future__ import print_function

import os
import sys
import importlib


components_package = "dash_uploader"

components_lib = importlib.import_module(components_package)

missing_dist_msg = "Warning {} was not found in `{}.__init__.{}`!!!"
missing_manifest_msg = """
Warning {} was not found in `MANIFEST.in`!
It will not be included in the build!
"""

with open("MANIFEST.in", "r") as f:
    manifest = f.read()


def check_dist(dist, filename):
    # Support the dev bundle.
    if filename.endswith("dev.js"):
        return True

    return any(
        filename in x
        for d in dist
        for x in (
            [d.get("relative_package_path")]
            if not isinstance(d.get("relative_package_path"), list)
            else d.get("relative_package_path")
        )
    )


def check_manifest(filename):
    return filename in manifest


def check_file(dist, filename):
    if not check_dist(dist, filename):
        print(
            missing_dist_msg.format(filename, components_package, "_js_dist"),
            file=sys.stderr,
        )
    if not check_manifest(filename):
        print(missing_manifest_msg.format(filename), file=sys.stderr)


for cur, _, files in os.walk(components_package):
    for f in files:

        if f.endswith("js"):
            # noinspection PyProtectedMember
            check_file(components_lib._js_dist, f)
        elif f.endswith("css"):
            # noinspection PyProtectedMember
            check_file(components_lib._css_dist, f)
        elif not f.endswith("py"):
            check_manifest(f)
