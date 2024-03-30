from jsonschema import ValidationError
from pyss._validator import validate_pyss_data


def test_header_version_formatting():
    happy_cases = [
        {"min_version": "0.1.0"},
        {"max_version": "0.1.0"},
        {"min_version": "0.1.0", "max_version": "0.1.0"},
        {},
    ]

    for case in happy_cases:
        data = {
            "pyss": case,
            "scripts": [],
        }

        exception: Exception = None
        try:
            validate_pyss_data(data)
        except Exception as e:
            exception = e
        assert exception is None

    failure_cases = [
        {"min_version": "asdf"},
        {"max_version": "asdf"},
        {"min_version": "0.1.0", "max_version": "asdf"},
        {"min_version": "asdf", "max_version": "0.1.0"},
    ]

    for case in failure_cases:
        data = {
            "pyss": case,
            "scripts": [],
        }

        exception: ValidationError = None
        try:
            validate_pyss_data(data)
        except ValidationError as e:
            exception = e
        assert exception is not None
        assert (
            exception.message
            == "'asdf' is not a valid version format. Expected format: Major.Minor.Patch (e.g., 1.0.0)"
        )


def test_header_shell():
    happy_cases = [
        {"shell": "bash"},
        {"shell": {"linux": "bash"}},
        {"shell": {"win32": "cmd"}},
        {"shell": {"darwin": "bash"}},
        {},
    ]

    for case in happy_cases:
        data = {
            "pyss": case,
            "scripts": [],
        }

        exception: Exception = None
        try:
            validate_pyss_data(data)
        except Exception as e:
            exception = e
        assert exception is None

    failure_cases = [
        {"shell": {}},
        {"shell": {"something_wrong": 1}},
    ]

    for case in failure_cases:
        data = {
            "pyss": case,
            "scripts": [],
        }

        exception: ValidationError = None
        try:
            validate_pyss_data(data)
        except ValidationError as e:
            exception = e
        assert exception is not None
        assert exception.message in [
            "{} is not valid under any of the given schemas",
            "{'something_wrong': 1} is not valid under any of the given schemas",
        ]


def test_scripts_required():
    data = {
        "pyss": {},
    }

    exception: ValidationError = None
    try:
        validate_pyss_data(data)
    except ValidationError as e:
        exception = e
    assert exception is not None
    assert exception.message == "'scripts' is a required property"


def test_scripts_type():
    data = {
        "pyss": {},
        "scripts": "not a list",
    }

    exception: ValidationError = None
    try:
        validate_pyss_data(data)
    except ValidationError as e:
        exception = e
    assert exception is not None
    assert exception.message == "'not a list' is not of type 'array'"


def test_scripts_commands_required():
    happy_cases = [
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "commands": ["echo 'hello world'"],
                },
            ],
        },
    ]

    for case in happy_cases:
        exception: Exception = None
        try:
            validate_pyss_data(case)
        except Exception as e:
            exception = e
        assert exception is None

    failure_case = {
        "pyss": {},
        "scripts": [
            {"name": "test", "description": "test"},
        ],
    }

    exception: ValidationError = None
    try:
        validate_pyss_data(failure_case)
    except ValidationError as e:
        exception = e
    assert exception is not None
    assert (
        exception.message
        == "{'name': 'test', 'description': 'test'} is not valid under any of the given schemas"
    )


def test_scripts_description_required():
    happy_cases = [
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                },
            ],
        },
        # Internal scripts do not require a description
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "internal": True,
                    "command": "echo 'hello world'",
                },
            ],
        },
    ]

    for case in happy_cases:
        exception: Exception = None
        try:
            validate_pyss_data(case)
        except Exception as e:
            exception = e
        assert exception is None

    failure_case = {
        "pyss": {},
        "scripts": [
            {
                "name": "test",
                "command": "echo 'hello world'",
            },
        ],
    }

    exception: ValidationError = None
    try:
        validate_pyss_data(failure_case)
    except ValidationError as e:
        exception = e
    assert exception is not None
    assert exception.message == "'description' is a required property"


def test_scripts_command_as_object():
    happy_cases = [
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": {"cmd": "echo 'hello world'"},
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "commands": [
                        {"darwin": "echo 'hello world'", "win32": "echo 'hello world'"}
                    ],
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": {
                        "darwin": "echo 'hello world'",
                        "win32": "echo 'hello world'",
                    },
                },
            ],
        },
    ]

    for case in happy_cases:
        exception: Exception = None
        try:
            validate_pyss_data(case)
        except Exception as e:
            exception = e
        assert exception is None

    failure_cases = [
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": {"not_command": "echo 'hello world'"},
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": {},
                },
            ],
        },
    ]

    for case in failure_cases:
        exception: ValidationError = None
        try:
            validate_pyss_data(case)
        except ValidationError as e:
            exception = e
        assert exception is not None
        assert exception.message.endswith("is not valid under any of the given schemas")


def test_scripts_dependency_requirements():
    happy_cases = [
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": ["test2"],
                    "after": ["test2"],
                },
                {
                    "name": "test2",
                    "description": "test2",
                    "command": "echo 'hello world'",
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": "test2",
                    "after": "test2",
                },
                {
                    "name": "test2",
                    "description": "test2",
                    "command": "echo 'hello world'",
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": [{"script": "test2"}],
                    "after": {"script": "test2"},
                },
                {
                    "name": "test2",
                    "internal": True,
                    "command": "echo 'hello world'",
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": [{"command": "echo 'hello'"}],
                    "after": {"command": "echo 'hello'"},
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": [{"commands": ["echo 'hello'"]}],
                    "after": {"commands": ["echo 'hello'"]},
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": [{"commands": [{"cmd": "echo 'hello world'"}]}],
                    "after": {"commands": [{"cmd": "echo 'hello world'"}]},
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": [{"command": {"cmd": "echo 'hello world'"}}],
                    "after": {"command": {"cmd": "echo 'hello world'"}},
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": [
                        {
                            "commands": [
                                {
                                    "darwin": "echo 'hello world'",
                                    "win32": "echo 'hello world'",
                                }
                            ]
                        }
                    ],
                    "after": {
                        "commands": [
                            {
                                "darwin": "echo 'hello world'",
                                "win32": "echo 'hello world'",
                            }
                        ]
                    },
                },
            ],
        },
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": [
                        {
                            "command": {
                                "darwin": "echo 'hello world'",
                                "win32": "echo 'hello world'",
                            }
                        }
                    ],
                    "after": {
                        "command": {
                            "darwin": "echo 'hello world'",
                            "win32": "echo 'hello world'",
                        }
                    },
                },
            ],
        },
    ]

    for case in happy_cases:
        exception: Exception = None
        try:
            validate_pyss_data(case)
        except Exception as e:
            exception = e
        assert exception is None

    failure_cases = [
        {
            "pyss": {},
            "scripts": [
                {
                    "name": "test",
                    "description": "test",
                    "command": "echo 'hello world'",
                    "before": {},
                    "after": {},
                },
            ],
        },
    ]

    for case in failure_cases:
        exception: ValidationError = None
        try:
            validate_pyss_data(case)
        except ValidationError as e:
            exception = e
        assert exception is not None
        assert exception.message == "{} is not valid under any of the given schemas"
