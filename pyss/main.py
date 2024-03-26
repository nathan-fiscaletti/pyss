import re
import sys
import os
import yaml

from termcolor import colored

from importlib.metadata import version

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


def __execute_command(command: str, silent: bool = False) -> int:
    env_var_pattern = re.compile(r"\${([a-zA-Z_][a-zA-Z0-9_]*)}")
    command_colored = env_var_pattern.sub(
        lambda match: colored(match.group(), __ENV_VAR_COLOR),
        command,
    )
    if not silent:
        __info("os.system", command_colored)

    try:
        evaluated_script_command = __evaluate_environment_variables(command)
    except ValueError as e:
        __error(e)
        return 1

    return os.system(evaluated_script_command)


def __execute_dependencies(
    scripts: list, dependencies: list | str, silent: bool = False
) -> int:
    if not isinstance(dependencies, list):
        if dependencies in [script["name"] for script in scripts]:
            exit_code = __run_script(scripts, dependencies, silent)
        else:
            exit_code = __execute_command(dependencies, silent)
        if exit_code != 0:
            return exit_code
    else:
        for dependency_script in dependencies:
            if dependency_script in [script["name"] for script in scripts]:
                exit_code = __run_script(scripts, dependency_script, silent)
            else:
                exit_code = __execute_command(dependency_script, silent)
            if exit_code != 0:
                return exit_code
    return 0


def __run_script(scripts: list, script_name: str, silent: bool = False) -> int:
    if not any(script["name"] == script_name for script in scripts):
        __error(f"Script '{script_name}' not found.")
        return 1

    script = next(script for script in scripts if script["name"] == script_name)

    if not silent:
        __info("run script", script["name"], __DETAIL_COLOR)

    if "env" in script:
        if not isinstance(script["env"], dict):
            __error("The 'env' key must be a dictionary.")
            return 1
        __prime_environment(script["env"])

    if "before" in script:
        exit_code = __execute_dependencies(scripts, script["before"], silent)
        if exit_code != 0:
            return exit_code

    script_command = script["command"]
    exit_code = __execute_command(script_command, silent)
    if exit_code != 0:
        return exit_code

    if "after" in script:
        exit_code = __execute_dependencies(scripts, script["after"], silent)
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


def __print_help():
    print(colored(f"Python Script Support (PySS) - v{version('pyss')}", "white"))
    print()
    print("  Author:   Nathan Fiscaletti")
    print("  Website:  github.com/nathan-fiscaletti/pyss")
    print()
    print("A simple script runner for Python.")
    print()
    print("Usage: pyss [options] <script_name>")
    print()
    print("Options:")
    print("    --list : List all available scripts.")
    print("    --help : Show this help message.")
    sys.exit(0)


def __evaluate(action: str, silent: bool = False):
    scripts, scripts_file = __get_scripts()

    if action == "--list":
        __print_scripts(scripts, scripts_file)

    if action == "--help":
        __print_help()

    desired_script = action

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

    exit_code = __run_script(scripts, desired_script, silent)
    sys.exit(exit_code)


def main():
    action_idx = 1
    silent = False
    if sys.argv[1] == "--silent":
        silent = True
        action_idx = 2
    action = sys.argv[action_idx]

    __evaluate(action, silent)


if __name__ == "__main__":
    main()
