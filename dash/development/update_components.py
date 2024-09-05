import sys
import subprocess
import shlex
import os
import argparse
import shutil
import logging
import coloredlogs


class _CombinedFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


logger = logging.getLogger(__name__)
coloredlogs.install(
    fmt="%(asctime)s,%(msecs)03d %(levelname)s - %(message)s", datefmt="%H:%M:%S"
)

dest_dir_map = {
    "dash-core-components": "dcc",
    "dash-html-components": "html",
    "dash-table": "dash_table",
}


def status_print(msg, **kwargs):
    try:
        print(msg, **kwargs)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "ignore"), **kwargs)


def bootstrap_components(components_source, concurrency, install_type):

    is_windows = sys.platform == "win32"

    source_glob = (
        components_source
        if components_source != "all"
        else "{dash-core-components,dash-html-components,dash-table}"
    )

    cmdstr = f"npx lerna exec --concurrency {concurrency} --scope='{source_glob}' -- npm {install_type}"
    cmd = shlex.split(cmdstr, posix=not is_windows)
    status_print(cmdstr)

    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_windows
    ) as proc:
        out, err = proc.communicate()
        status = proc.poll()

    if err:
        status_print(("🛑 " if status else "") + err.decode(), file=sys.stderr)

    if status or not out:
        status_print(
            f"🚨 Failed installing npm dependencies for component packages: {source_glob} (status={status}) 🚨",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        status_print(
            f"🟢 Finished installing npm dependencies for component packages: {source_glob} 🟢",
            file=sys.stderr,
        )


def build_components(components_source, concurrency):

    is_windows = sys.platform == "win32"

    source_glob = (
        components_source
        if components_source != "all"
        else "{dash-core-components,dash-html-components,dash-table}"
    )

    cmdstr = f"npx lerna exec --concurrency {concurrency} --scope='{source_glob}' -- npm run build"
    cmd = shlex.split(cmdstr, posix=not is_windows)
    status_print(cmdstr)

    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=is_windows
    ) as proc:
        out, err = proc.communicate()
        status = proc.poll()

    if err:
        status_print(("🛑 " if status else "") + err.decode(), file=sys.stderr)

    if status or not out:
        status_print(
            f"🚨 Finished updating component packages: {source_glob} (status={status}) 🚨",
            file=sys.stderr,
        )
        sys.exit(1)

    if "{" in source_glob:
        source_glob = source_glob.split("{")[1].split("}")[0]

    for package in source_glob.split(","):
        build_directory = os.path.join(
            "components", package, package.replace("-", "_").rstrip("/\\")
        )

        dest_dir = dest_dir_map.get(package) or package

        dest_path = os.path.join("dash", dest_dir)

        if not os.path.exists(dest_path):
            try:
                os.makedirs(dest_path)
            except OSError:
                logger.exception("🚨 Having issues manipulating %s", dest_path)
                sys.exit(1)

        if not os.path.exists(build_directory):
            status_print(
                "🚨 Could not locate build artifacts."
                + " Check that the npm build process completed"
                + f" successfully for package: {package} 🚨"
            )
            sys.exit(1)
        else:
            status_print(f"🚚 Moving build artifacts from {build_directory} to Dash 🚚")
            shutil.rmtree(dest_path)
            shutil.copytree(build_directory, dest_path)
            with open(os.path.join(dest_path, ".gitkeep"), "w", encoding="utf-8"):
                pass
            status_print(
                f"🟢 Finished moving build artifacts from {build_directory} to Dash 🟢"
            )


def cli():
    parser = argparse.ArgumentParser(
        prog="dash-update-components",
        formatter_class=_CombinedFormatter,
        description="Update the specified subcomponent libraries within Dash"
        " by copying over build artifacts, dependencies, and dependency metadata.",
    )
    parser.add_argument(
        "components_source",
        help="A glob string that matches the Dash component libraries to be updated"
        " (eg.'dash-table' // 'dash-core-components|dash-html-components' // 'all')."
        " The default argument is 'all'.",
        default="all",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Maximum concurrent steps, up to 3 (ie all components in parallel)",
    )
    parser.add_argument(
        "--ci",
        help="For clean-install use '--ci True'",
        default="False",
    )

    args = parser.parse_args()

    if sys.platform == "win32":
        args.components_source = args.components_source.replace('"', "").replace(
            "'", ""
        )

    bootstrap_components(
        args.components_source, args.concurrency, "ci" if args.ci == "True" else "i"
    )
    build_components(args.components_source, args.concurrency)


if __name__ == "__main__":
    cli()
