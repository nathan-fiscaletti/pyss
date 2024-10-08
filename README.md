# PySS: Python Script Support Tool

[![Sponsor Me!](https://img.shields.io/badge/%F0%9F%92%B8-Sponsor%20Me!-blue)](https://github.com/sponsors/nathan-fiscaletti)
[![PyPI version](https://badge.fury.io/py/pyss.svg)](https://badge.fury.io/py/pyss)
[![GitHub license](https://img.shields.io/github/license/nathan-fiscaletti/pyss.svg)](https://github.com/nathan-fiscaletti/pyss/blob/master/LICENSE)
[![Downloads](https://static.pepy.tech/badge/pyss)](https://pepy.tech/project/pyss)
[![Downloads](https://static.pepy.tech/badge/pyss/month)](https://pepy.tech/project/pyss)

PySS is a tool designed to facilitate the management and execution of `pyss.yaml` configurations, aimed at enhancing Python scripting workflows. It offers a straightforward command-line interface for executing scripts defined in a `pyss.yaml` or `pyss.yml` file, with capabilities for testing configurations, silent and quiet execution modes, and advanced configuration options including environment variables, custom variables, and pre/post execution scripts. The project is open-source, licensed under the MIT License, and is geared towards simplifying script execution tasks for Python developers

## Installing PySS

To integrate PySS into your environment, simply run:

```bash
pip install pyss
```

## How to Use

PySS streamlines script execution through a user-friendly command-line interface:

```yaml
usage: pyss [options] [script_name]

A simple script runner for Python.

positional arguments:
  script_name    the name of the script to execute

options:
  -h, --help     show this help message and exit
  -l, --list     show a list of all scripts configured for use
  -t, --test     validate the pyss configuration file
  -s, --silent   execute the script without any output
  -q, --quiet    execute the script while omitting the [pyss] header messages
  -v, --version  prints the program version to stdout
```

To configure your project with PySS, create a `pyss.yaml` or `pyss.yml` file at the project root. This file should enumerate the commands you plan to execute.

### Configuration Example

Below is a straightforward example to get you started:

```yaml
# Configure PySS settings here (all optional).
pyss:
 min_version: 1.0.2
 max_version: 1.1.7

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

### Advanced Configuration

For more complex setups, PySS supports environment variables, custom variables, pre/post execution scripts, per-platform customization, shell customization and internal script designation. View the [Advanced Configuration](advanced.md) documentation for more information.

### Validating Your Configuration

To ensure your configuration is valid, run the following command:

```sh
$ pyss --test
[pyss][validate] Validating configuration file 'pyss.yaml'...
[pyss][validate] Configuration file 'pyss.yaml' is valid.
```

## Running Scripts

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

## Additional Features

To view a list of configured scripts, use:

```bash
$ pyss --list
```

## Credits

Special thanks to Pyss Man: [@mavrw](https://github.com/mavrw)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
