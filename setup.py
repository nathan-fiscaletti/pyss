from setuptools import setup

setup(
    name="pyss",
    version="1.0.1",
    description="Adds a utility for running pyss.yaml files.",
    author="Nathan Fiscaletti",
    author_email="nate.fiscaletti@gmail.com",
    packages=["pyss"],
    install_requires=["termcolor"],
    entry_points={
        "console_scripts": [
            "pyss = pyss.main:main",
        ],
    },
)
