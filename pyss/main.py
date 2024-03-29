import sys
import os

from jsonschema import ValidationError
from termcolor import colored

from pyss._logging import log_error, log_info
from pyss._arguments import parse_arguments
from pyss._scripts import get_scripts, print_scripts, validate_pyss_data, get_pyss_file
from pyss._execution import run_pyss, PyssCfg
from pyss._environment import prime_environment
from pyss._constants import (
    NOT_FOUND_COLOR,
    FOUND_COLOR,
)


def main():
    args, print_help = parse_arguments()

    pyss_file = get_pyss_file()

    file_location = pyss_file.file_location

    if args.test:
        try:
            log_info("validate", f"Validating configuration file '{file_location}'...")
            validate_pyss_data(dict(pyss_file))
            log_info("validate", f"Configuration file '{file_location}' is valid.")
            sys.exit(0)
        except ValidationError as e:
            log_error(e.message, title="Validation Error")
            sys.exit(1)

    scripts = get_scripts(pyss_file)
    if args.list:
        print_scripts(scripts, file_location)

    if not args.script_name:
        log_error("No script name provided.")
        print_help()
        sys.exit(1)

    desired_script = args.script_name

    if not any(script["name"] == desired_script for script in scripts):
        script_name_colored = colored(desired_script, NOT_FOUND_COLOR)
        file_location_colored = colored(file_location, FOUND_COLOR)
        log_error(
            f"Script '{script_name_colored}' not found in {file_location_colored}."
        )
        sys.exit(1)

    script = next(script for script in scripts if script["name"] == desired_script)
    if script is not None:
        if "internal" in script:
            if script["internal"]:
                script_name_colored = colored(desired_script, NOT_FOUND_COLOR)
                log_error(f"Script '{script_name_colored}' is internal.")
                sys.exit(1)

    if pyss_file.env is not None:
        prime_environment(pyss_file.env)

    if args.silent:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

    sys.exit(
        run_pyss(
            PyssCfg(
                scripts=scripts,
                script_name=desired_script,
                quiet=args.quiet,
                disable_output=args.silent,
            )
        )
    )


if __name__ == "__main__":
    main()
