# PySS: Advanced Configuration

> See [./pyss/_validator.py](./pyss/_validator.py) for the full schema definition.

For more complex setups, PySS supports environment variables, custom variables, pre/post execution scripts, shell customization and internal script designation:

## Environment Variables

In PySS, environment variables allow for dynamic script configurations. Utilize them within scripts using the `${VAR_NAME}` syntax. Define these variables in the `env` section to make them accessible to your scripts.

### Defining Environment Variables

Environment variables are set in the `env` section of a script or at the header level for global access. These variables can be referenced in any script command or in pre/post execution scripts.

#### Example

```yaml
env:
  PROJECT_DIR: "/path/to/project"

scripts:
  - name: backup-database
    command: "mysqldump -u root -p${DB_PASSWORD} my_database > ${PROJECT_DIR}/backup.sql"
    env:
      DB_PASSWORD: "password"
```

In this example, `PROJECT_DIR` and `DB_PASSWORD` are custom environment variables used within the `backup-database` script. The variables are replaced with their respective values when the script executes.


## Internal Scripts

Scripts marked as "internal" won't appear in the `--list` output and can't be invoked directly. The `description` for internal scripts is optional. These scripts are typically used as pre/post execution scripts for other scripts.

```yaml
env:
  NAME: "Heisenberg"

scripts:
  - name: print-greeting
    internal: true
    command: echo Hello, ${NAME}!

  - name: run
    description: Displays a customized greeting followed by your name.
    before: print-greeting
    command: echo Your name is ${NAME}
```

In this example, `print-greeting` is an internal script that won't appear in the list of available scripts. It is used as a pre-execution script for the `run` script.

## Shell Customization

Customize the shell used to execute scripts by specifying the `shell` property in the `pyss` header of the configuration file or in the distinct command objects.

- The shell property in the header will be used as the default shell for all scripts if specified. Otherwise, PySS will use the system's default shell.
- If a shell is specified in a command object, it will take precedence for that command.

> By default, PySS uses `subprocess.Popen` to execute scripts with `shell=True`

#### Shell Objects

Shell objects can either be a **string representing a shell to use**, or **an object specifying a different shell to use for different systems.**

#### Shell Property in Header

```yaml
pyss:
  shell: /bin/sh
```

The shell object supports distinct shells for `sys.platform` values (`darwin`, `win32`, `linux` etc.). See [sys.platform values](https://docs.python.org/3/library/sys.html#sys.platform) in the Python documentation for more information.

```yaml
pyss:
  shell:
    win32: "C:\\Windows\\System32\\cmd.exe"
    linux: "/bin/sh"
```

#### Shell Property in Command Object

If a shell is specified in a command object, PySS will use `subprocess.Popen` with `executable` set to the specified shell **while executing that command.**

```yaml
scripts:
  - name: print-pwd
    description: Displays the current working directory.
    command: 
      win32: "echo $PWD.path"
      linux: "echo ${PWD}"
      shell:
        win32: "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
```


## Command Objects

Command objects offer flexibility in script configuration, allowing for system-specific commands and shell customization. They can be specified as strings or as objects for detailed system-specific configurations.
  
### System-Specific Commands

For scripts that need to run different commands based on the operating system, use an object with keys for each system type. The supported system types include `sys.platform` values (`win32`, `linux`, `darwin`, etc.) See [sys.platform values](https://docs.python.org/3/library/sys.html#sys.platform) in the Python documentation for more information.

```yaml
scripts:
  - name: check-disk-space
    description: Displays the available disk space on the system.
    command:
      win32: "fsutil volume diskfree C:"
      linux: "df -h /"
```

This script, `check-disk-space`, runs different commands based on the operating system. It uses `fsutil` on Windows and `df` on Unix-like systems to check disk space.

### Specifying a Shell

In some cases, you may want to execute a command using a specific shell. This can be done by specifying the `shell` property within the command object.

```yaml
scripts:
  - name: list-files
    description: Lists all files in the current directory.
    command: "ls -la"
    shell: "/bin/bash"
```

Here, the `list-files` script explicitly specifies `/bin/bash` as the shell for executing the `ls -la` command. See the [Shell Customization](#shell-customization) section for more details on shell customization.

## Pre/Post Execution Scripts

PySS allows for the specification of scripts to be executed before (`before`) and after (`after`) the main script commands. These can either be direct commands or references to other scripts defined in your configuration.

### Specifying Pre/Post Execution Scripts

Pre/post execution scripts can enhance the script's functionality or perform necessary setup/cleanup tasks.

```yaml
scripts:
  - name: initialize
    internal: true
    command: "echo Initializing..."
  
  - name: cleanup
    internal: true
    command: "echo Cleaning up..."

  - name: main-task
    description: "Performs the main task with initialization and cleanup."
    before: initialize
    command: "echo Performing main task..."
    after: cleanup
```

In this configuration, `initialize` is run before `main-task`, and `cleanup` is run afterward. These pre/post execution scripts can be specified as a list, allowing for multiple scripts to run before or after the main script.

## Full Example

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