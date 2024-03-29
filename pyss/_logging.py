from termcolor import colored

from pyss._constants import INFO_COLOR


def log_error(message, title="Error"):
    print(f"{colored(title, 'red')}: {message}")


def log_info(header, message, color=INFO_COLOR):
    print(f"{colored(f'[pyss][{header}]', color)} {message}")
