import sys


def cli():
    try:
        from plotly_cloud.cli import main  # pylint: disable=import-outside-toplevel

        main()
    except ImportError:
        print(
            "Plotly cloud is not installed,"
            " install it with `pip install dash[cloud]` to use the plotly command",
            file=sys.stderr,
        )
        sys.exit(-1)
