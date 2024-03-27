import os
import re


def prime_environment(env: dict[str, any]):
    """
    Prime the environment with the provided environment variables.
    """
    for key, value in env.items():
        os.environ[key] = value


def clear_environment(env: dict[str, any]):
    """
    Clear the environment of the provided environment variables.
    """
    for key in env.keys():
        os.environ.pop(key, None)


def evaluate_environment_variables(input: str) -> str:
    """
    Evaluates all environment variables in the input string and replaces
    them with their respective values.
    """
    env_var_pattern = re.compile(r"\${([a-zA-Z_][a-zA-Z0-9_]*)}")
    env_vars = env_var_pattern.findall(input)

    for env_var in env_vars:
        env_var_value = os.getenv(env_var)
        if env_var_value is None:
            raise ValueError(f"Environment variable '{env_var}' not set.")
        input = input.replace(f"${{{env_var}}}", env_var_value)

    return input
