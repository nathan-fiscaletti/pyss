import os
import sys
import re
import subprocess

from termcolor import colored

from pyss._logging import log_error, log_info

from pyss._environment import (
    prime_environment,
    clear_environment,
    evaluate_environment_variables,
)

from pyss._constants import ENV_VAR_COLOR, DETAIL_COLOR
from pyss._types import PyssCfg, Command


def run_pyss(cfg: PyssCfg) -> int:
    if not any(script["name"] == cfg.script_name for script in cfg.scripts):
        log_error(f"Script '{cfg.script_name}' not found.")
        return 1

    script = next(script for script in cfg.scripts if script["name"] == cfg.script_name)

    if not cfg.quiet and not cfg.disable_output:
        log_info("run script", script["name"], DETAIL_COLOR)

    if "env" in script:
        prime_environment(script["env"])

    if "before" in script:
        exit_code = __execute_dependencies(cfg, script["before"])
        if exit_code != 0:
            return exit_code

    commands: list[Command] = []
    if "command" in script:
        command = script["command"]
        commands.append(Command(command))
    elif "commands" in script:
        for command in script["commands"]:
            commands.append(Command(command))

    for command in commands:
        exit_code = __execute_command(cfg, command)
        if exit_code != 0:
            return exit_code

    if "after" in script:
        exit_code = __execute_dependencies(cfg, script["after"])
        if exit_code != 0:
            return exit_code

    if "env" in script:
        clear_environment(script["env"])

    return exit_code


def __execute_command(
    cfg: PyssCfg,
    input: Command,
) -> int:
    command = input.get()

    try:
        evaluated_script_command = evaluate_environment_variables(command)
    except ValueError as e:
        log_error(e)
        return 1

    pyss_directory = os.path.dirname(cfg.scripts.pyss_file.file_location)

    shell = None
    if cfg.scripts.pyss_file.header.shell is not None:
        shell = cfg.scripts.pyss_file.header.shell.get()

    _cmd_shell = input.get_shell()
    if _cmd_shell is not None:
        shell = _cmd_shell.get()

    env_var_pattern = re.compile(r"\${([a-zA-Z_][a-zA-Z0-9_]*)}")
    command_colored = env_var_pattern.sub(
        lambda match: colored(match.group(), ENV_VAR_COLOR),
        command,
    )

    if not cfg.quiet and not cfg.disable_output:
        if shell is None:
            log_info("subprocess.Popen(shell=True)", command_colored)
        else:
            log_info(shell, command_colored)

    proc = subprocess.Popen(
        evaluated_script_command,
        cwd=pyss_directory,
        stdout=subprocess.DEVNULL if cfg.disable_output else None,
        stderr=subprocess.DEVNULL if cfg.disable_output else None,
        shell=True,
        executable=shell,
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
    cfg: PyssCfg,
    dependency: dict | str,
) -> int:
    if isinstance(dependency, str):
        exit_code = 0
        if dependency in [script["name"] for script in cfg.scripts]:
            exit_code = run_pyss(
                PyssCfg(
                    scripts=cfg.scripts,
                    script_name=dependency,
                    quiet=cfg.quiet,
                    disable_output=cfg.disable_output,
                )
            )
        else:
            exit_code = __execute_command(cfg, Command(dependency))
        return exit_code
    elif isinstance(dependency, dict):
        silent = cfg.disable_output
        if "silent" in dependency:
            silent = dependency["silent"]

        if "env" in dependency:
            prime_environment(dependency["env"])

        exit_code = 0
        if "script" in dependency:
            script_name = dependency["script"]
            if script_name not in [script["name"] for script in cfg.scripts]:
                log_error(f"Script '{script_name}' not found.")
                return 1
            exit_code = run_pyss(
                PyssCfg(
                    scripts=cfg.scripts,
                    script_name=script_name,
                    quiet=cfg.quiet,
                    disable_output=silent,
                )
            )
        elif "command" in dependency:
            exit_code = __execute_command(cfg, Command(dependency["command"]))
        elif "commands" in dependency:
            for command in dependency["commands"]:
                exit_code = __execute_command(cfg, Command(command))
                if exit_code != 0:
                    break

        if "env" in dependency:
            clear_environment(dependency["env"])

        return exit_code


def __execute_dependencies(
    cfg: PyssCfg,
    dependencies: list | dict | str,
) -> int:
    if isinstance(dependencies, list):
        exit_code = 0
        for dependency in dependencies:
            exit_code = __execute_dependency(cfg, dependency)
            if exit_code != 0:
                break
        return exit_code

    return __execute_dependency(cfg, dependencies)
