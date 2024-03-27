# PySS: Python Script Support Tool

[![Sponsor Me!](https://img.shields.io/badge/%F0%9F%92%B8-Sponsor%20Me!-blue)](https://github.com/sponsors/nathan-fiscaletti)
[![PyPI version](https://badge.fury.io/py/pyss.svg)](https://badge.fury.io/py/pyss)
[![GitHub license](https://img.shields.io/github/license/nathan-fiscaletti/pyss.svg)](https://github.com/nathan-fiscaletti/pyss/blob/master/LICENSE)
[![Downloads](https://static.pepy.tech/badge/pyss)](https://pepy.tech/project/pyss)
[![Downloads](https://static.pepy.tech/badge/pyss/month)](https://pepy.tech/project/pyss)

PySS offers an efficient way to manage and execute `pyss.yaml` configurations, enhancing your Python scripting workflow.

## Getting Started

### Installing PySS

To integrate PySS into your environment, simply run:

```bash
pip install pyss
```

### How to Use

PySS streamlines script execution through a user-friendly command-line interface:

```yaml
usage: pyss [options] [script_name]

A simple script runner for Python.

positional arguments:
  script_name    The name of the script to run.

options:
  -h, --help     show this help message and exit
  -l, --list     List all available scripts.
  -s, --silent   Run the script suppressing all output.
  -q, --quiet    Run the script suppressing header [pyss] messages.
  -v, --version  Prints the program version to stdout.
```

To configure your project with PySS, create a `pyss.yaml` or `pyss.yml` file at the project root. This file should enumerate the commands you plan to execute.

#### Configuration Example

Below is a straightforward example to get you started:

```yaml
# Configure PySS settings here (all optional).
pyss:
 min_version: 1.0.2
 max_version: 1.1.0

# List your executable scripts.
scripts:
  - name: say-my-name
    description: Outputs a predetermined name
    command: echo Heisenberg
```

Execute a script by invoking the `pyss` command at your project's root:

```bash
$ pyss say-my-name
[pyss][run script] 'say-my-name'
[pyss][os.system] 'echo Heisenberg'
Heisenberg
```

#### Validating Your Configuration

To ensure your configuration is valid, run the following command:

```sh
$ pyss --test
[pyss][validate] Validating configuration file 'pyss.yaml'...
[pyss][validate] Configuration file 'pyss.yaml' is valid.
```

#### Advanced Configuration

For more complex setups, PySS supports environment variables, custom variables, pre/post execution scripts, and internal script designation:

- **Environment Variables**: Use `${VAR_NAME}` format to utilize environment variables within scripts. Define custom environment variables in the `env` section.
- **Internal Scripts**: Scripts marked as "internal" won't appear in the `--list` output and can't be invoked directly. The `description` for internal scripts is optional.
- **Pre/Post Execution Scripts**: Specify scripts to run before (`before`) and after (`after`) the main script. These can be direct commands or references to other scripts in your configuration.
    - By default, you can specify the value as a string and PySS will attempt to find another script in your configuration with the same name. If none is found, PySS will treat the value as a command.
    - Otherwise, you can provide an object as the value with the following properties:
        - `script`: The name of the script to run.
        - `command` or `commands`: The command(s) to run.
        - `silent`: Suppresses the output of the script.
        - `env`: Custom environment variables for the script.
        - **Note**: Only one of `command`, `commands` or `script` can be specified.

```yaml
scripts:
  - name: print-greeting
    internal: true
    command: echo Hello, ${NAME}!

  - name: print-farewell
    internal: true
    command: "echo Goodbye, ${NAME}!"

  - name: run
    description: Displays a customized greeting and farewell.
    before:
      - script: print-greeting
    commands: 
      - echo Your name is ${NAME}
      - echo You are ${AGE} years old.
    after: print-farewell
    env:
      NAME: Heisenberg
```

> See [./pyss/_validator.py](./pyss/_validator.py) for the full schema definition.

### Running Scripts

**Verbose Execution (Default)**

```sh
$ export AGE=28
$ pyss run
[pyss][run script] run
[pyss][run script] print-greeting
[pyss][os.system] echo Hello, ${NAME}!
Hello, Heisenberg!
[pyss][os.system] echo Your name is ${NAME}
Your name is Heisenberg
[pyss][os.system] echo You are ${AGE} years old.
You are 28 years old.
[pyss][run script] print-farewell
[pyss][os.system] echo Goodbye, ${NAME}!
Goodbye, Heisenberg!
```

**Quiet Mode (`--quiet`)**

```sh
$ export AGE=28
$ pyss --quiet run
Hello, Heisenberg!
Your name is Heisenberg
You are 28 years old.
Goodbye, Heisenberg!
```

**Silent Mode (`--silent`)**

```bash
# This mode executes the script without producing any output.
```

### Additional Features

To view a list of configured scripts, use:

```bash
$ pyss --list
```

## Credits

Special thanks to Pyss Man: [@mavrw](https://github.com/mavrw)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.