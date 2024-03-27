import jsonschema
import re


@jsonschema.FormatChecker.cls_checks("version")
def __version_format(value):
    pattern = r"^\d+\.\d+\.\d+$"
    if not re.match(pattern, value):
        message = f"'{value}' is not a valid version format. Expected format: Major.Minor.Patch (e.g., 1.0.0)"
        raise jsonschema.ValidationError(
            message, instance=value, schema_path=["properties", "version", "format"]
        )
    return True


__dependency = {
    "anyOf": [
        {
            "type": "string",
        },
        {
            "type": "object",
            "properties": {
                "script": {"type": "string"},
                "command": {"type": "string"},
                "commands": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "env": {
                    "type": "object",
                },
                "silent": {
                    "type": "boolean",
                },
            },
            "oneOf": [
                {"required": ["script"]},
                {"required": ["command"]},
                {"required": ["commands"]},
            ],
        },
    ],
}

__dependencies = {
    "oneOf": [
        __dependency,
        {
            "type": "array",
            "items": __dependency,
        },
    ]
}

__schema = {
    "type": "object",
    "properties": {
        # PySS Configuration
        "pyss": {
            "type": "object",
            "properties": {
                # Optional properties to set version constraints
                "min_version": {"type": "string", "format": "version"},
                "max_version": {"type": "string", "format": "version"},
            },
        },
        # Script Configuration
        "scripts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "internal": {"type": "boolean"},
                    "before": __dependencies,
                    "after": __dependencies,
                    "command": {"type": "string"},
                    "commands": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name"],
                "oneOf": [{"required": ["command"]}, {"required": ["commands"]}],
                "allOf": [
                    {
                        "if": {
                            "not": {
                                "properties": {"internal": {"const": True}},
                                "required": ["internal"],
                            }
                        },
                        "then": {"required": ["description"]},
                    }
                ],
            },
        },
    },
    "required": ["scripts"],
}


def validate_pyss(data):
    jsonschema.validate(
        instance=data, schema=__schema, format_checker=jsonschema.FormatChecker()
    )
