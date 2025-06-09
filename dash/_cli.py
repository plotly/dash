import argparse
import importlib
import sys
from typing import Any, Dict

from dash import Dash


def load_app(app_path: str) -> Dash:
    """
    Load a Dash app instance from a string like "module:variable".

    :param app_path: The import path to the Dash app instance.
    :return: The loaded Dash app instance.
    """
    app_split = app_path.split(":")
    module_str = app_split[0]

    if not module_str:
        raise ValueError(f"Invalid app path: '{app_path}'. ")

    try:
        module = importlib.import_module(module_str)
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_str}'.") from e

    if len(app_split) == 2:
        app_str = app_split[1]
        try:
            app_instance = getattr(module, app_str)
        except AttributeError as e:
            raise AttributeError(
                f"Could not find variable '{app_str}' in module '{module_str}'."
            ) from e
    else:
        for module_var in vars(module).values():
            if isinstance(module_var, Dash):
                app_instance = module_var
                break

    if not isinstance(app_instance, Dash):
        raise TypeError(f"'{app_path}' did not resolve to a Dash app instance.")

    return app_instance


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the Plotly CLI."""
    parser = argparse.ArgumentParser(
        description="A command line interface for Plotly Dash."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- `run` command ---
    run_parser = subparsers.add_parser(
        "run",
        help="Run a Dash app.",
        description="Run a local development server for a Dash app.",
    )

    run_parser.add_argument(
        "app",
        help='The Dash app to run, in the format "module:variable" '
        'or just "module" to find the app instance automatically. (eg: plotly run app)',
    )

    # Server options
    run_parser.add_argument(
        "--host",
        type=str,
        help='Host IP used to serve the application (Default: "127.0.0.1").',
    )
    run_parser.add_argument(
        "--port",
        "-p",
        type=int,
        help='Port used to serve the application (Default: "8050").',
    )
    run_parser.add_argument(
        "--proxy",
        type=str,
        help='Proxy configuration string, e.g., "http://0.0.0.0:8050::https://my.domain.com".',
    )

    # Debug flag (supports --debug and --no-debug)
    # Note: Requires Python 3.9+
    run_parser.add_argument(
        "--debug",
        "-d",
        action=argparse.BooleanOptionalAction,
        help="Enable/disable Flask debug mode and dev tools.",
    )

    # Dev Tools options
    dev_tools_group = run_parser.add_argument_group("dev tools options")
    dev_tools_group.add_argument(
        "--dev-tools-ui",
        action=argparse.BooleanOptionalAction,
        help="Enable/disable the dev tools UI.",
    )
    dev_tools_group.add_argument(
        "--dev-tools-props-check",
        action=argparse.BooleanOptionalAction,
        help="Enable/disable component prop validation.",
    )
    dev_tools_group.add_argument(
        "--dev-tools-serve-dev-bundles",
        action=argparse.BooleanOptionalAction,
        help="Enable/disable serving of dev bundles.",
    )
    dev_tools_group.add_argument(
        "--dev-tools-hot-reload",
        action=argparse.BooleanOptionalAction,
        help="Enable/disable hot reloading.",
    )
    dev_tools_group.add_argument(
        "--dev-tools-hot-reload-interval",
        type=float,
        help="Interval in seconds for hot reload polling (Default: 3).",
    )
    dev_tools_group.add_argument(
        "--dev-tools-hot-reload-watch-interval",
        type=float,
        help="Interval in seconds for server-side file watch polling (Default: 0.5).",
    )
    dev_tools_group.add_argument(
        "--dev-tools-hot-reload-max-retry",
        type=int,
        help="Max number of failed hot reload requests before failing (Default: 8).",
    )
    dev_tools_group.add_argument(
        "--dev-tools-silence-routes-logging",
        action=argparse.BooleanOptionalAction,
        help="Enable/disable silencing of Werkzeug's route logging.",
    )
    dev_tools_group.add_argument(
        "--dev-tools-disable-version-check",
        action=argparse.BooleanOptionalAction,
        help="Enable/disable the Dash version upgrade check.",
    )
    dev_tools_group.add_argument(
        "--dev-tools-prune-errors",
        action=argparse.BooleanOptionalAction,
        help="Enable/disable pruning of tracebacks to user code only.",
    )

    return parser


def cli():
    """The main entry point for the Plotly CLI."""
    sys.path.insert(0, ".")
    parser = create_parser()
    args = parser.parse_args()

    try:
        if args.command == "run":
            app = load_app(args.app)

            # Collect arguments to pass to the app.run() method.
            # Only include arguments that were actually provided on the CLI
            # or have a default value in the parser.
            run_options: Dict[str, Any] = {
                key: value
                for key, value in vars(args).items()
                if value is not None and key not in ["command", "app"]
            }

            app.run(**run_options)

    except (ValueError, ImportError, AttributeError, TypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
