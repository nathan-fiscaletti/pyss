import argparse

from importlib.metadata import version as app_version


def parse_arguments() -> tuple[argparse.Namespace, lambda: None]:
    parser = argparse.ArgumentParser(
        prog="pyss",
        usage="%(prog)s [options] [script_name]",
        description="A simple script runner for Python.",
        epilog="For more information, visit: https://github.com/nathan-fiscaletti/pyss",
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="show a list of all scripts configured for use.",
    )

    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="validate the PySS configuration file.",
    )

    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="execute the script without any output.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="execute the script while omitting the [pyss] header messages.",
    )

    parser.add_argument(
        "-v",
        "--version",
        help="prints the program version to stdout.",
        action="version",
        version=f"%(prog)s v{app_version('pyss')}",
    )

    parser.add_argument(
        "script_name", nargs="?", help="the name of the script to execute."
    )

    return parser.parse_args(), lambda: parser.print_help()
