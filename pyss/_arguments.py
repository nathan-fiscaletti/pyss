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
        help="Shows a list of all scripts configured for use.",
    )

    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Executes the script without any output.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Executes the script while omitting the [pyss] header messages.",
    )

    parser.add_argument(
        "-v",
        "--version",
        help="Prints the program version to stdout.",
        action="version",
        version=f"%(prog)s v{app_version('pyss')}",
    )

    parser.add_argument(
        "script_name", nargs="?", help="Specifies the script you wish to execute."
    )

    return parser.parse_args(), lambda: parser.print_help()
