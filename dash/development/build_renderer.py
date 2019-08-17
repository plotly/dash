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


root = _concat((__file__, *(os.pardir for _ in range(3))))
renderer = _concat((root, "dash-renderer"))
assets = _concat((renderer, "dash_renderer"))
package_lock = _concat((renderer, "package-lock.json"))
npm_modules = _concat((renderer, "node_modules"))
versions = {}

with open(_concat((renderer, "VERSION.txt")), "r") as fpv:
    versions["version"] = fpv.read().strip()


@job("run `npm i --ignore-scripts`")
def npm():
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
        try:
            shutil.rmtree(assets)
            os.makedirs(assets)
        except OSError:
            logger.exception("🚨 having issues manipulate %s", assets)
            sys.exit(1)

    # parse the package-lock.json and copy bundles
    with open(package_lock, "r") as fp:
        deps = json.load(fp)["dependencies"]

    for bundle in renderer_bundles:
        name = bundle["name"]
        version = deps[name]["version"]
        versions[name.replace("-", "")] = version

        logger.info("processing bundle => %s@%s", name, version)

        shutil.copyfile(
            _concat((npm_modules, name, *bundle["prod"])),
            _concat((assets, "{}@{}.min.js".format(name, version))),
        )

        shutil.copyfile(
            _concat((npm_modules, name, *bundle["dev"])),
            _concat((assets, "{}@{}.js".format(name, version))),
        )

    # run build
    os.chdir(renderer)
    run_command_with_process("npm run build:renderer")

    copies = os.listdir(assets)
    logger.info("bundles in dash_renderer %s", copies)

    # compute the fingerprint for all the assets
    digest = {"dash_renderer": versions["version"]}
    for copy in copies:
        digest["MD5 ({})".format(copy)] = compute_md5(_concat((assets, copy)))

    with open(_concat((renderer, "digest.json")), "w") as fp:
        json.dump(digest, fp, sort_keys=True, indent=4, separators=(",", ":"))
    logger.info(
        "bundle digest in digest.json:\n%s", json.dumps(digest, indent=4)
    )

    # generate the __init__.py from template
    with open(
        _concat((os.path.dirname(__file__), "renderer_init.template"))
    ) as fp:
        t = string.Template(fp.read())

    with open(_concat((assets, "__init__.py")), "w") as fp:
        fp.write(t.safe_substitute(versions))


def main():
    fire.Fire()
