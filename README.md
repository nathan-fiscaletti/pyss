# PySS - Python Script Support

Adds a utility for running pyss.yaml files.

## Installation

```bash
pip install pyss
```

## Usage

```yaml
usage: pyss [options] [script_name]

A simple script runner for Python.

positional arguments:
  script_name   The name of the script to run.

options:
  -h, --help    show this help message and exit
  -l, --list    List all available scripts.
  -s, --silent  Run the script suppressing all output.
  -q, --quiet   Run the script suppressing header [pyss] messages.
```

Define a `pyss.yaml` or `pyss.yml` file in the root of your project. This file should contain a list of commands to run.

### Basic Example

```yaml
# Optionally provide a configuration
# for this PySS file. All fields are
# optional.
pyss:
 min_version: 1.0.2
 max_version: 1.0.5

# Define a list of scripts that can be run.
scripts:
  - name: say-my-name
    description: Says his name
    command: echo Heisenberg
```

Then, to run one of the scripts, use the `pyss` command from the root of your project.

```bash
$ pyss say-my-name
[pyss] [run script] 'say-my-name'
[pyss] [os.system] 'echo Heisenberg'
Heisenberg
```

### Advanced Example

- You can provide environment variables that will be evaluated at run time by formatting them as `${ENV_VAR}`.
- You can provide custom environment variables in the `env` section.
  - The `env` section is a dictionary of key-value pairs.
  - The key is the environment variable name and the value is the environment variable value.
  - If an environment variable is already set in the system, the value provided in the `env` section will override it during the execution of the script.
- You can provide 'before' and 'after' scripts to run before and after the main command.
  - The `before` and `after` scripts can be a single script or a list of scripts.
  - The `before` and `after` scripts can either be a shell command to execute, or the name of another script defined in the `pyss.yaml` file.
- You can mark scripts as "internal". 
  - Internal scripts will not show in `--list` output and cannot be executed directly.
  - For internal scripts, the `description` field is optional.

```yaml
scripts:
  - name: print-greeting
    internal: true
    command: echo Hello, ${NAME}!

  - name: print-farewell
    internal: true
    command: "echo Goodbye, ${NAME}!"

  - name: run
    description: Prints the name with a header.
    before:
     - print-greeting
    command: echo Your name is ${NAME} && echo You are ${AGE} years old.
    after:
      - print-farewell
    env:
      NAME: Heisenberg
```

### Execution Example

**Without any flags (Verbose)**

```sh
$ export AGE=28
$ pyss run
[pyss] [run script] 'run'
[pyss] [run script] 'print-greeting'
[pyss] [os.system] 'echo Hello, ${NAME}!'
Hello, Heisenberg!
[pyss] [os.system] 'echo Your name is ${NAME} && echo You are ${AGE} years old.'
Your name is Heisenberg
You are 28 years old.
[pyss] [run script] 'print-farewell'
[pyss] [os.system] 'echo Goodbye, ${NAME}!'
Goodbye, Heisenberg!
```

**With `--quiet`**

> Quiet mode suppresses the `[pyss]` messages. (Will still print error messages)

```sh
$ export AGE=28
$ pyss --quiet run
Hello, Heisenberg!
Your name is Heisenberg
You are 28 years old.
Goodbye, Heisenberg!
```

**With `--silent`**

> Silent mode suppresses all output.

## Utility

To list the commands available in the `pyss.yaml` file, you can run the following command:

```bash
$ pyss --list
Run script with: pyss <script_name>
Available Scripts found in pyss.yaml:
    - run : Prints the name with a header.
```

## Attribution

Thanks to Pyss Man: [@mavrw](https://github.com/mavrw)