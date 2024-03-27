import os
import sys
import re
import yaml

from packaging import version
from importlib.metadata import version as app_version
from termcolor import colored
from jsonschema import ValidationError

from pyss._validator import validate_pyss
from pyss._logging import lerror

from pyss._constants import (
    SCRIPTS_FILE_PATTERN,
    NOT_FOUND_COLOR,
    FOUND_COLOR,
    COMMAND_COLOR,
    SCRIPT_COLOR,
)


def get_scripts() -> tuple[list, str]:
    scripts_file_pattern = re.compile(SCRIPTS_FILE_PATTERN, re.IGNORECASE)
    scripts_file = None

    for file in os.listdir(os.getcwd()):
        if scripts_file_pattern.match(file):
            scripts_file = file
            break

    if scripts_file is None:
        file_colored = colored("pyss.yaml", NOT_FOUND_COLOR)
        lerror(f"No PySS YAML ({file_colored}) file found in the current directory.")
        sys.exit(1)

    scripts_config = yaml.load(open(scripts_file), Loader=yaml.FullLoader)

    try:
        validate_pyss(scripts_config)
    except ValidationError as e:
        lerror(e.message, title="Validation Error")
        sys.exit(1)

    min_version = None
    max_version = None

    if "pyss" in scripts_config:
        if "min_version" in scripts_config["pyss"]:
            min_version = scripts_config["pyss"]["min_version"]
        if "max_version" in scripts_config["pyss"]:
            max_version = scripts_config["pyss"]["max_version"]

    if min_version is not None:
        if version.parse(app_version("pyss")) < version.parse(min_version):
            lerror(
                f"This PySS project requires at least version {min_version} of PySS."
            )
            lerror(f"Current version: {app_version('pyss')}.")
            sys.exit(1)

    if max_version is not None:
        if version.parse(app_version("pyss")) > version.parse(max_version):
            lerror(
                f"PySS version {app_version('pyss')} is not supported by this PySS project."
            )
            sys.exit(1)

    scripts = scripts_config["scripts"]
    return scripts, scripts_file


def print_scripts(scripts: list, scripts_file: str):
    colored_example = colored("pyss <script_name>", COMMAND_COLOR)
    print(f"Run script with: {colored_example}")
    scripts_file_colored = colored(scripts_file, FOUND_COLOR)
    print(f"Available Scripts found in {scripts_file_colored}:")

    name_len = 0
    for script in scripts:
        if "internal" in script:
            if script["internal"]:
                continue
        name_len = max(name_len, len(script["name"]))

    for script in scripts:
        if "internal" in script:
            if script["internal"]:
                continue
        script_name = script["name"].ljust(name_len)
        script_name_colored = colored(script_name, SCRIPT_COLOR)
        print(f"    - {script_name_colored} : {script['description']}")
    sys.exit(0)
