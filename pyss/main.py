import sys
import os

from jsonschema import ValidationError
from termcolor import colored

from pyss._logging import lerror, linfo
from pyss._arguments import parse_arguments
from pyss._scripts import get_scripts, print_scripts, validate_config, get_raw_config
from pyss._execution import run_script
from pyss._constants import (
    NOT_FOUND_COLOR,
    FOUND_COLOR,
)


def main():
    args, print_help = parse_arguments()

    cfg, cfg_file = get_raw_config()

    if args.test:
        try:
            linfo("validate", f"Validating configuration file '{cfg_file}'...")
            validate_config(cfg)
            linfo("validate", f"Configuration file '{cfg_file}' is valid.")
            sys.exit(0)
        except ValidationError as e:
            lerror(e.message, title="Validation Error")
            sys.exit(1)

    scripts = get_scripts(cfg)
    if args.list:
        print_scripts(scripts, cfg_file)

    if not args.script_name:
        lerror("No script name provided.")
        print_help()
        sys.exit(1)

    desired_script = args.script_name

    if not any(script["name"] == desired_script for script in scripts):
        script_name_colored = colored(desired_script, NOT_FOUND_COLOR)
        scripts_file_colored = colored(cfg_file, FOUND_COLOR)
        lerror(f"Script '{script_name_colored}' not found in {scripts_file_colored}.")
        sys.exit(1)

    script = next(script for script in scripts if script["name"] == desired_script)
    if script is not None:
        if "internal" in script:
            if script["internal"]:
                script_name_colored = colored(desired_script, NOT_FOUND_COLOR)
                lerror(f"Script '{script_name_colored}' is internal.")
                sys.exit(1)

    if args.silent:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

    exit_code = run_script(scripts, desired_script, args.quiet, args.silent)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
