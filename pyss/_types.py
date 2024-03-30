import os
import sys


class PlatformSpecificValue:
    _value: str | dict = None

    def __init__(self, shell: str | dict):
        self._value = shell

    def get(self) -> str:
        if isinstance(self._value, str) or self._value is None:
            return self._value

        if isinstance(self._value, dict):
            if sys.platform in self._value:
                return self._value[sys.platform]

        return None


class PyssFileHeader:
    min_version: str
    max_version: str
    shell: PlatformSpecificValue

    def __init__(self, data: dict):
        self.min_version = data.get("min_version")
        self.max_version = data.get("max_version")
        self.shell = PlatformSpecificValue(data.get("shell"))


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
    _value: str | dict

    def __init__(self, cmd: str | dict):
        self._value = cmd

    def get(self) -> str:
        if self._value is None or isinstance(self._value, str):
            return self._value

        if isinstance(self._value, dict):
            if "cmd" in self._value:
                return self._value.get("cmd")

            if sys.platform in self._value:
                return self._value[sys.platform]

    def get_shell(self) -> PlatformSpecificValue | None:
        if "shell" in self._value:
            return PlatformSpecificValue(self._value.get("shell"))
        return None
