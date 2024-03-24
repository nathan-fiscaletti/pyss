import re
import sys
import os
import yaml

from termcolor import colored

__SCRIPTS_FILE_PATTERN = r"pyss\.(yml|yaml)$"

__NOT_FOUND_COLOR = "red"
__FOUND_COLOR = "green"
__COMMAND_COLOR = "yellow"
__SCRIPT_COLOR = "blue"


def main():
    scripts_file_pattern = re.compile(__SCRIPTS_FILE_PATTERN, re.IGNORECASE)
    scripts_file = None

    for file in os.listdir(os.getcwd()):
        if scripts_file_pattern.match(file):
            scripts_file = file
            break

    if scripts_file is None:
        file_colored = colored("pyss.yaml", __NOT_FOUND_COLOR)
        print(f"No PYSS YAML ({file_colored}) file found in the current directory.")
        sys.exit(1)

    scripts_config = yaml.load(open(scripts_file), Loader=yaml.FullLoader)

    scripts = scripts_config["scripts"]

    action_idx = 1

    silent = False
    if sys.argv[1] == "--silent":
        silent = True
        action_idx = 2

    action = sys.argv[action_idx]

    if action == "--list":
        print()
        colored_example = colored("pyss <script_name>", __COMMAND_COLOR)
        print(f"Run script with: {colored_example}")
        print()
        scripts_file_colored = colored(scripts_file, __FOUND_COLOR)
        print(f"Available Scripts found in {scripts_file_colored}:")
        print()

        name_len = 0
        for script in scripts:
            name_len = max(name_len, len(script["name"]))

        for script in scripts:
            script_name = script["name"].ljust(name_len)
            script_name_colored = colored(script_name, __SCRIPT_COLOR)
            print(f"    - {script_name_colored} : {script['description']}")
        print()
        sys.exit(0)

    desired_script = action

    if not any(script["name"] == desired_script for script in scripts):
        script_name_colored = colored(desired_script, __NOT_FOUND_COLOR)
        scripts_file_colored = colored(scripts_file, __FOUND_COLOR)
        print(f"Script '{script_name_colored}' not found in {scripts_file_colored}.")
        sys.exit(1)

    for script in scripts:
        if script["name"] == desired_script:
            script_command = script["command"]
            if not silent:
                name_colored = colored(script["name"], __SCRIPT_COLOR)
                command_colored = colored(script_command, __COMMAND_COLOR)
                print()
                print(f"Running script:  {name_colored}")
                print(f"Execute:         {command_colored}")
                print()
            exit_code = os.system(script_command)
            sys.exit(exit_code)
