# PySS: Python Script Support Tool

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

This utility facilitates running Python scripts with ease.

positional arguments:
  script_name   Specifies the script you wish to execute.

options:
  -h, --help    Displays this guide.
  -l, --list    Shows a list of all scripts configured for use.
  -s, --silent  Executes the script without any output.
  -q, --quiet   Executes the script while omitting the [pyss] header messages.
```

To configure your project with PySS, create a `pyss.yaml` or `pyss.yml` file at the project root. This file should enumerate the commands you plan to execute.

#### Configuration Example

Below is a straightforward example to get you started:

```yaml
# Configure PySS settings here (all optional).
pyss:
 min_version: 1.0.2
 max_version: 1.0.6

# List your executable scripts.
scripts:
  - name: say-my-name
    description: Outputs a predetermined name
    command: echo Heisenberg
```

Execute a script by invoking the `pyss` command at your project's root:

```bash
$ pyss say-my-name
[pyss] [run script] 'say-my-name'
[pyss] [os.system] 'echo Heisenberg'
Heisenberg
```

#### Advanced Configuration

For more complex setups, PySS supports environment variables, custom variables, pre/post execution scripts, and internal script designation:

- **Environment Variables**: Use `${VAR_NAME}` format to utilize environment variables within scripts. Define custom environment variables in the `env` section.
- **Pre/Post Execution Scripts**: Specify scripts to run before (`before`) and after (`after`) the main script. These can be direct commands or references to other scripts in your configuration.
- **Internal Scripts**: Scripts marked as "internal" won't appear in the `--list` output and can't be invoked directly. The `description` for internal scripts is optional.

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
     - print-greeting
    command: echo Your name is ${NAME} && echo You are ${AGE} years old.
    after:
      - print-farewell
    env:
      NAME: Heisenberg
```

### Running Scripts

**Verbose Execution (Default)**

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