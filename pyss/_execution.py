import sys
import re
import subprocess

from termcolor import colored

from pyss._logging import lerror, linfo

from pyss._environment import (
    prime_environment,
    clear_environment,
    evaluate_environment_variables,
)

from pyss._constants import ENV_VAR_COLOR, DETAIL_COLOR


def __execute_command(
    command: str, quiet: bool = False, disable_output: bool = False
) -> int:
    env_var_pattern = re.compile(r"\${([a-zA-Z_][a-zA-Z0-9_]*)}")
    command_colored = env_var_pattern.sub(
        lambda match: colored(match.group(), ENV_VAR_COLOR),
        command,
    )
    if not quiet:
        if disable_output:
            linfo("os.system (silent)", command_colored)
        else:
            linfo("os.system", command_colored)

    try:
        evaluated_script_command = evaluate_environment_variables(command)
    except ValueError as e:
        lerror(e)
        return 1

    proc = subprocess.Popen(
        evaluated_script_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE if not disable_output else subprocess.DEVNULL,
        stderr=subprocess.PIPE if not disable_output else subprocess.DEVNULL,
        shell=True,
    )

    try:
        outs, errs = proc.communicate(timeout=30)
        if outs:
            print(outs.decode(), file=sys.stdout, end="")
        if errs:
            print(errs.decode(), file=sys.stderr, end="")
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
        if outs:
            print(outs.decode(), file=sys.stdout, end="")
        if errs:
            print(errs.decode(), file=sys.stderr, end="")

    return proc.returncode


def __execute_dependency(
    scripts: list,
    dependency: dict | str,
    quiet: bool = False,
    disable_output: bool = False,
) -> int:
    if isinstance(dependency, str):
        exit_code = 0
        if dependency in [script["name"] for script in scripts]:
            exit_code = run_script(scripts, dependency, quiet, disable_output)
        else:
            exit_code = __execute_command(dependency, quiet, disable_output)
        return exit_code
    elif isinstance(dependency, dict):
        silent = False
        if "silent" in dependency:
            silent = dependency["silent"]

        if "env" in dependency:
            prime_environment(dependency["env"])

        exit_code = 0
        if "script" in dependency:
            script_name = dependency["script"]
            if script_name not in [script["name"] for script in scripts]:
                lerror(f"Script '{script_name}' not found.")
                return 1
            exit_code = run_script(scripts, script_name, quiet, silent)
        elif "command" in dependency:
            exit_code = __execute_command(dependency["command"], quiet, silent)
        elif "commands" in dependency:
            for command in dependency["commands"]:
                exit_code = __execute_command(command, quiet, silent)
                if exit_code != 0:
                    break

        if "env" in dependency:
            clear_environment(dependency["env"])

        return exit_code


def __execute_dependencies(
    scripts: list,
    dependencies: list | dict | str,
    quiet: bool = False,
    disable_output: bool = False,
) -> int:
    if isinstance(dependencies, list):
        exit_code = 0
        for dependency in dependencies:
            exit_code = __execute_dependency(scripts, dependency, quiet, disable_output)
            if exit_code != 0:
                break
        return exit_code

    return __execute_dependency(scripts, dependencies, quiet, disable_output)


def run_script(
    scripts: list, script_name: str, quiet: bool = False, disable_output: bool = False
) -> int:
    if not any(script["name"] == script_name for script in scripts):
        lerror(f"Script '{script_name}' not found.")
        return 1

    script = next(script for script in scripts if script["name"] == script_name)

    if not quiet:
        if disable_output:
            linfo("run script (silent)", script["name"], DETAIL_COLOR)
        else:
            linfo("run script", script["name"], DETAIL_COLOR)

    if "env" in script:
        prime_environment(script["env"])

    if "before" in script:
        exit_code = __execute_dependencies(
            scripts, script["before"], quiet, disable_output
        )
        if exit_code != 0:
            return exit_code

    commands = []
    if "command" in script:
        commands.append(script["command"])
    elif "commands" in script:
        commands.extend(script["commands"])

    for command in commands:
        exit_code = __execute_command(command, quiet, disable_output)
        if exit_code != 0:
            return exit_code

    if "after" in script:
        exit_code = __execute_dependencies(
            scripts, script["after"], quiet, disable_output
        )
        if exit_code != 0:
            return exit_code

    if "env" in script:
        clear_environment(script["env"])

    return exit_code
