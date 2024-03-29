import os
import sys
import re
import yaml

from packaging import version
from importlib.metadata import version as app_version
from termcolor import colored
from jsonschema import ValidationError

from pyss._validator import validate_pyss_data
from pyss._logging import log_error

from pyss._constants import (
    FILE_LOCATION_PATTERN,
    NOT_FOUND_COLOR,
    FOUND_COLOR,
    COMMAND_COLOR,
    SCRIPT_COLOR,
)

from pyss._types import PySSFile, Scripts


def get_pyss_file() -> PySSFile:
    file_location_pattern = re.compile(FILE_LOCATION_PATTERN, re.IGNORECASE)
    file_location = None

    current_dir = os.getcwd()
    path_parts = current_dir.split(os.sep)

    for i in range(len(path_parts) - 1, -1, -1):
        path_part = path_parts[: i + 1]
        current_dir = os.sep.join(path_part)
        for file in os.listdir(current_dir):
            if file_location_pattern.match(file):
                file_location = os.path.join(current_dir, file)
                break

        if file_location is not None:
            break

    if file_location is None:
        file_colored = colored("pyss.yaml", NOT_FOUND_COLOR)
        log_error(f"No PySS YAML ({file_colored}) file found in the current directory.")
        sys.exit(1)

    scripts_config = yaml.load(open(file_location), Loader=yaml.FullLoader)

    return PySSFile(scripts_config, file_location)


def get_scripts(pyss_file: PySSFile) -> Scripts:
    try:
        validate_pyss_data(pyss_file)
    except ValidationError as e:
        log_error(e.message, title="Validation Error")
        sys.exit(1)

    script_header = pyss_file.header

    if script_header.min_version is not None:
        if version.parse(app_version("pyss")) < version.parse(
            script_header.min_version
        ):
            log_error(
                f"This PySS project requires at least version {script_header.min_version} of PySS."
            )
            log_error(f"Current version: {app_version('pyss')}.")
            sys.exit(1)

    if script_header.max_version is not None:
        if version.parse(app_version("pyss")) > version.parse(
            script_header.max_version
        ):
            log_error(
                f"PySS version {app_version('pyss')} is not supported by this PySS project."
            )
            sys.exit(1)

    return Scripts(pyss_file, pyss_file["scripts"])


def print_scripts(scripts: Scripts):
    colored_example = colored("pyss <script_name>", COMMAND_COLOR)
    print(f"Run script with: {colored_example}")
    file_location_colored = colored(scripts.pyss_file.file_location, FOUND_COLOR)
    print(f"Available Scripts found in {file_location_colored}:")

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
