import os


class Shell:
    _nt: str = None
    _posix: str = None

    def __init__(self, shell: str | dict):
        if isinstance(shell, str):
            self._nt = shell
            self._posix = shell
        elif isinstance(shell, dict):
            self._nt = shell.get("nt")
            self._posix = shell.get("posix")

    def get(self) -> str:
        if os.name == "nt" and self._nt is not None:
            return self._nt
        elif os.name == "posix" and self._posix is not None:
            return self._posix
        return None


class PyssFileHeader:
    min_version: str
    max_version: str
    shell: Shell

    def __init__(self, data: dict):
        self.min_version = data.get("min_version")
        self.max_version = data.get("max_version")
        self.shell = Shell(data.get("shell"))


class PySSFile(dict):
    file_location: str
    header: PyssFileHeader
    env: dict[str, any] = None

    def __init__(self, data: dict, file_location: str):
        super(PySSFile, self).__init__(data)
        self.header = PyssFileHeader(data["pyss"] if "pyss" in data else {})
        self.file_location = file_location
        self.env = data.get("env")


class Scripts(list):
    pyss_file: PySSFile

    def __init__(self, pyss_file: PySSFile, scripts: list):
        super(Scripts, self).__init__(scripts)
        self.pyss_file = pyss_file


class PyssCfg:
    scripts: Scripts
    script_name: str
    quiet: bool
    disable_output: bool

    def __init__(
        self,
        scripts: Scripts,
        script_name: str,
        quiet: bool,
        disable_output: bool,
    ):
        self.scripts = scripts
        self.script_name = script_name
        self.quiet = quiet
        self.disable_output = disable_output


class Command:
    _nt: str = None
    _posix: str = None
    _cmd: str = None
    _shell: Shell = None

    def __init__(self, cmd: str | dict):
        if isinstance(cmd, str):
            self._cmd = cmd
        elif isinstance(cmd, dict):
            self._nt = cmd.get("nt")
            self._posix = cmd.get("posix")
            self._cmd = cmd.get("cmd")
            if "shell" in cmd:
                self._shell = Shell(cmd.get("shell"))

    def get(self) -> str:
        if os.name == "nt" and self._nt is not None:
            return self._nt
        elif os.name == "posix" and self.__posix is not None:
            return self._posix
        return self._cmd

    def get_shell(self) -> Shell | None:
        return self._shell
