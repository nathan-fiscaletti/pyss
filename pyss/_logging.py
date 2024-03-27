from termcolor import colored

from pyss._constants import INFO_COLOR


def lerror(message, title="Error"):
    print(f"{colored(title, 'red')}: {message}")


def linfo(header, message, color=INFO_COLOR):
    print(f"{colored(f'[pyss] [{header}]', color)} '{message}'")
