# PySS - Python Script Support

Adds a utility for running pyss.yaml files.

## Installation

```bash
pip install pyss
```

## Usage

Define a `pyss.yaml` file in the root of your project. This file should contain a list of commands to run.

### Basic Example

```yaml
scripts:
  - name: say-my-name
    description: Says his name
    command: echo Heisenberg
```

Then, to run one of the commands, use the `pyss` command from the root of your project.

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
- You can mark scripts as "internal". When marked as internal, the script will not show in `--list` command and cannot be executed directly.
  - For internal scripts, the `description` field is optional.
- You can use the `--silent` flag to hide the header output.

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

```sh
$ export AGE=28
$ pyss --silent run
Hello, Heisenberg!
Your name is Heisenberg
You are 28 years old.
Goodbye, Heisenberg!
```

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