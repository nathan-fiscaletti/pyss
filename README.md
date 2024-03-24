# PYSS - Python Script Support

Adds a utility for running pyss.yaml files.

## Installation

```bash
pip install -g pyss
```

## Usage

Define a `pyss.yaml` file in the root of your project. This file should contain a list of commands to run.

```yaml
scripts:
  - name: say-my-name
    description: Says his name
    command: echo Heisenberg
  - name: ww
    description: What could it stand for?
    command: echo Willy Wonka?
```

Then, to run one of the commands, use the `pyss` command from the root of your project.

```bash
$ pyss say-my-name

Running script:  say-my-name
Execute:         echo Heisenberg

Heisenberg
```

## Utility

To list the commands available in the `pyss.yaml` file, you can run the following command:

```bash
$ pyss --list

Run script with: pyss <script_name>

Available Scripts found in pyss.yaml:

    - say-my-name : Says his name
    - ww          : What could it stand for?

```

## Attribution

Thanks to Pyss Man: [@mavrw](https://github.com/mavrw)