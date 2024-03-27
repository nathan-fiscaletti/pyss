import re
import sys
import os

import argparse
import yaml

import subprocess

from importlib.metadata import version as app_version
from packaging import version

from termcolor import colored

__SCRIPTS_FILE_PATTERN = r"pyss\.(yml|yaml)$"

__NOT_FOUND_COLOR = "red"
__FOUND_COLOR = "green"
__COMMAND_COLOR = "yellow"
__SCRIPT_COLOR = "blue"
__ENV_VAR_COLOR = "magenta"

__INFO_COLOR = "blue"
__DETAIL_COLOR = "cyan"


def __error(message):
    print(f"{colored('Error', 'red')}: {message}")


def __info(header, message, color=__INFO_COLOR):
    print(f"{colored(f'[pyss] [{header}]', color)} '{message}'")


def __prime_environment(env: dict[str, any]):
    """
    Prime the environment with the provided environment variables.
    """
    for key, value in env.items():
        os.environ[key] = value


def __clear_environment(env: dict[str, any]):
    """
    Clear the environment of the provided environment variables.
    """
    for key in env.keys():
        os.environ.pop(key, None)


def __evaluate_environment_variables(input: str) -> str:
    """
    Evaluates all environment variables in the input string and replaces
    them with their respective values.
    """
    env_var_pattern = re.compile(r"\${([a-zA-Z_][a-zA-Z0-9_]*)}")
    env_vars = env_var_pattern.findall(input)

    for env_var in env_vars:
        env_var_value = os.getenv(env_var)
        if env_var_value is None:
            raise ValueError(f"Environment variable '{env_var}' not found.")
        input = input.replace(f"${{{env_var}}}", env_var_value)

    return input


def __execute_command(
    command: str, quiet: bool = False, disable_output: bool = False
) -> int:
    env_var_pattern = re.compile(r"\${([a-zA-Z_][a-zA-Z0-9_]*)}")
    command_colored = env_var_pattern.sub(
        lambda match: colored(match.group(), __ENV_VAR_COLOR),
        command,
    )
    if not quiet:
        __info("os.system", command_colored)

    try:
        evaluated_script_command = __evaluate_environment_variables(command)
    except ValueError as e:
        __error(e)
        return 1

    proc = subprocess.Popen(
        evaluated_script_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE if not disable_output else None,
        stderr=subprocess.PIPE if not disable_output else None,
        shell=True,
    )

    try:
        outs, errs = proc.communicate(timeout=15)
        if outs:
            print(outs.decode(), file=sys.stdout, end="")
        if errs:
            print(errs.decode(), file=sys.stderr, end="")
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()

    return proc.returncode


def __execute_dependencies(
    scripts: list, dependencies: list | str, quiet: bool = False
) -> int:
    if not isinstance(dependencies, list):
        if dependencies in [script["name"] for script in scripts]:
            exit_code = __run_script(scripts, dependencies, quiet)
        else:
            exit_code = __execute_command(dependencies, quiet)
        if exit_code != 0:
            return exit_code
    else:
        for dependency_script in dependencies:
            if dependency_script in [script["name"] for script in scripts]:
                exit_code = __run_script(scripts, dependency_script, quiet)
            else:
                exit_code = __execute_command(dependency_script, quiet)
            if exit_code != 0:
                return exit_code
    return 0


def __run_script(
    scripts: list, script_name: str, quiet: bool = False, disable_output: bool = False
) -> int:
    if not any(script["name"] == script_name for script in scripts):
        __error(f"Script '{script_name}' not found.")
        return 1

    script = next(script for script in scripts if script["name"] == script_name)

    if not quiet:
        __info("run script", script["name"], __DETAIL_COLOR)

    if "env" in script:
        if not isinstance(script["env"], dict):
            __error("The 'env' key must be a dictionary.")
            return 1
        __prime_environment(script["env"])

    if "before" in script:
        exit_code = __execute_dependencies(scripts, script["before"], quiet)
        if exit_code != 0:
            return exit_code

    script_command = script["command"]
    exit_code = __execute_command(script_command, quiet)
    if exit_code != 0:
        return exit_code

    if "after" in script:
        exit_code = __execute_dependencies(scripts, script["after"], quiet)
        if exit_code != 0:
            return exit_code

    if "env" in script:
        __clear_environment(script["env"])

    return exit_code


def __get_scripts() -> tuple[list, str]:
    scripts_file_pattern = re.compile(__SCRIPTS_FILE_PATTERN, re.IGNORECASE)
    scripts_file = None

    for file in os.listdir(os.getcwd()):
        if scripts_file_pattern.match(file):
            scripts_file = file
            break

    if scripts_file is None:
        file_colored = colored("pyss.yaml", __NOT_FOUND_COLOR)
        __error(f"No PySS YAML ({file_colored}) file found in the current directory.")
        sys.exit(1)

    scripts_config = yaml.load(open(scripts_file), Loader=yaml.FullLoader)
    if "scripts" not in scripts_config:
        __error("No 'scripts' key found in the PySS YAML file.")
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
            __error(
                f"This PySS project requires at least version {min_version} of PySS."
            )
            __error(f"Current version: {app_version('pyss')}.")
            sys.exit(1)

    if max_version is not None:
        if version.parse(app_version("pyss")) > version.parse(max_version):
            __error(
                f"PySS version {app_version('pyss')} is not supported by this PySS project."
            )
            sys.exit(1)

    scripts = scripts_config["scripts"]
    if not isinstance(scripts, list):
        __error("The 'scripts' key must be a list.")
        sys.exit(1)

    return scripts, scripts_file


def __print_scripts(scripts: list, scripts_file: str):
    colored_example = colored("pyss <script_name>", __COMMAND_COLOR)
    print(f"Run script with: {colored_example}")
    scripts_file_colored = colored(scripts_file, __FOUND_COLOR)
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
        script_name_colored = colored(script_name, __SCRIPT_COLOR)
        print(f"    - {script_name_colored} : {script['description']}")
    sys.exit(0)


def __parse_arguments() -> tuple[argparse.Namespace, lambda: None]:
    parser = argparse.ArgumentParser(
        prog="pyss",
        usage="%(prog)s [options] [script_name]",
        description="A simple script runner for Python.",
        epilog="For more information, visit: https://github.com/nathan-fiscaletti/pyss",
    )

    parser.add_argument(
        "-l", "--list", action="store_true", help="List all available scripts."
    )

    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Run the script suppressing all output.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Run the script suppressing header [pyss] messages.",
    )

    parser.add_argument(
        "-v",
        "--version",
        help="Prints the program version to stdout.",
        action="version",
        version=f"%(prog)s v{app_version('pyss')}",
    )

    parser.add_argument("script_name", nargs="?", help="The name of the script to run.")

    return parser.parse_args(), lambda: parser.print_help()


def main():
    args, print_help = __parse_arguments()
    scripts, scripts_file = __get_scripts()

    if args.list:
        __print_scripts(scripts, scripts_file)

    if not args.script_name:
        __error("No script name provided.")
        print_help()
        sys.exit(1)

    desired_script = args.script_name

    if not any(script["name"] == desired_script for script in scripts):
        script_name_colored = colored(desired_script, __NOT_FOUND_COLOR)
        scripts_file_colored = colored(scripts_file, __FOUND_COLOR)
        __error(f"Script '{script_name_colored}' not found in {scripts_file_colored}.")
        sys.exit(1)

    for script in scripts:
        if script["name"] == desired_script:
            if "internal" in script:
                if script["internal"]:
                    script_name_colored = colored(desired_script, __NOT_FOUND_COLOR)
                    __error(f"Script '{script_name_colored}' is internal.")
                    sys.exit(1)
            break

    if args.silent:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

    exit_code = __run_script(scripts, desired_script, args.quiet)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
