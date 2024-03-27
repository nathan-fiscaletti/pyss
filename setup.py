from setuptools import setup

setup(
    name="pyss",
    version="1.0.4",
    description="Adds a utility for running pyss.yaml files.",
    author="Nathan Fiscaletti",
    author_email="nate.fiscaletti@gmail.com",
    packages=["pyss"],
    install_requires=["termcolor==2.2.0", "PyYAML==6.0"],
    entry_points={
        "console_scripts": [
            "pyss = pyss.main:main",
        ],
    },
)
