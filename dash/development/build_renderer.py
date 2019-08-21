# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import json
import string
import shutil
import logging

import coloredlogs
import fire

from .._utils import run_command_with_process, compute_md5, job


logger = logging.getLogger(__name__)
coloredlogs.install(
    fmt="%(asctime)s,%(msecs)03d %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

renderer_bundles = (
    {
        "name": "react",
        "prod": ("umd", "react.production.min.js"),
        "dev": ("umd", "react.development.js"),
    },
    {
        "name": "react-dom",
        "prod": ("umd", "react-dom.production.min.js"),
        "dev": ("umd", "react-dom.development.js"),
    },
    {
        "name": "prop-types",
        "prod": ("prop-types.min.js",),
        "dev": ("prop-types.js",),
    },
)


def _concat(paths):
    return os.path.realpath(os.path.sep.join(paths))


root = _concat([os.path.abspath(__file__)] + [os.pardir for _ in range(3)])
renderer = _concat((root, "dash-renderer"))
assets = _concat((renderer, "dash_renderer"))
package_lock = _concat((renderer, "package-lock.json"))
npm_modules = _concat((renderer, "node_modules"))
versions = {}

with open(_concat((renderer, "package.json"))) as fpp:
    versions["version"] = json.load(fpp)["version"]


@job("run `npm i --ignore-scripts`")
def npm():
    """job to run `npm i`"""
    try:
        os.chdir(renderer)
        logger.info("removing old package-lock.json")
        os.remove(package_lock)
    except OSError:
        sys.exit(1)

    run_command_with_process("npm i --ignore-scripts")


@job("parse package-lock.json and produce the bundles")
def bundles():
    # make sure we start from fresh folder
    if os.path.exists(assets):
        logger.warning("🚨 %s already exists, remove it!", assets)
        shutil.rmtree(assets)

    try:
        os.makedirs(assets)
    except OSError:
        logger.exception("🚨 having issues manipulating %s", assets)
        sys.exit(1)

    with open(package_lock, "r") as fp:
        deps = json.load(fp)["dependencies"]

    for bundle in renderer_bundles:
        name = bundle["name"]
        version = deps[name]["version"]
        versions[name.replace("-", "")] = version

        logger.info("processing bundle => %s@%s", name, version)

        shutil.copyfile(
            _concat((npm_modules, name) + bundle["prod"]),
            _concat((assets, "{}@{}.min.js".format(name, version))),
        )
        shutil.copyfile(
            _concat((npm_modules, name) + bundle["dev"]),
            _concat((assets, "{}@{}.js".format(name, version))),
        )

    logger.info("run `npm run build:renderer`")
    os.chdir(renderer)
    run_command_with_process("npm run build:renderer")

    digest(versions["version"])

    logger.info("generate the `__init__.py` file from template and verisons")
    with open(
        _concat((os.path.dirname(__file__), "renderer_init.template"))
    ) as fp:
        t = string.Template(fp.read())

    with open(_concat((assets, "__init__.py")), "w") as fp:
        fp.write(t.safe_substitute(versions))


@job("compute the hash digest for assets")
def digest(version=None):
    copies = (
        _
        for _ in os.listdir(assets)
        if os.path.splitext(_)[-1] in {".js", ".map"}
    )
    logger.info("bundles in dash_renderer %s", copies)

    # compute the fingerprint for all the assets
    if version is not None:
        payload = {"dash_renderer": version}
    for copy in copies:
        payload["MD5 ({})".format(copy)] = compute_md5(_concat((assets, copy)))

    with open(_concat((renderer, "digest.json")), "w") as fp:
        json.dump(payload, fp, sort_keys=True, indent=4, separators=(",", ":"))
    logger.info(
        "bundle digest in digest.json:\n%s",
        json.dumps(payload, sort_keys=True, indent=4),
    )


@job("build the renderer in dev mode")
def watch():
    os.chdir(renderer)
    os.system("npm run build:dev")


def main():
    fire.Fire()
