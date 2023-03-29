from typing import NotRequired, TypedDict

import pytest

from robo_cli.config import validator

SIMPLE = TypedDict(
    "Simple",
    {
        "string": str,
        "number": int,
    },
)

COMPLEX = TypedDict(
    "Complex",
    {
        "dict": dict[str, int],
        "list": list[int],
    },
)

OPTIONALS = TypedDict(
    "Optionals",
    {
        "required": str,
        "not-required-simple": NotRequired[str],
        "not-required-complex": NotRequired[dict[str, int]],
    },
)


def test_simple_valid():
    value = {
        "string": "zero",
        "number": 0,
    }
    validator.validate_schema(value, SIMPLE)


def test_simple_invalid():
    value = {
        "string": "zero",
        "number": "not-a-number",
    }
    with pytest.raises(ValueError):
        validator.validate_schema(value, SIMPLE)


def test_simple_missing():
    value = {
        "string": "zero",
    }
    with pytest.raises(KeyError):
        validator.validate_schema(value, SIMPLE)


def test_complex_valid():
    value = {
        "dict": {"key": 100},
        "list": [1, 2, 3],
    }
    validator.validate_schema(value, COMPLEX)


def test_complex_invalid_dict_key():
    value = {
        "dict": {100: 100},
        "list": [1, 2, 3],
    }
    with pytest.raises(ValueError):
        validator.validate_schema(value, COMPLEX)


def test_complex_invalid_dict_value():
    value = {
        "dict": {"key": "value"},
        "list": [1, 2, 3],
    }
    with pytest.raises(ValueError):
        validator.validate_schema(value, COMPLEX)


def test_complex_invalid_list():
    value = {
        "dict": {"key": 100},
        "list": [1, "a-string", 3],
    }
    with pytest.raises(ValueError):
        validator.validate_schema(value, COMPLEX)


def test_optionals_valid_missing():
    value = {
        "required": "a-string",
    }
    validator.validate_schema(value, OPTIONALS)


def test_optionals_valid_simple():
    value = {
        "required": "a-string",
        "not-required-simple": "another-string",
    }
    validator.validate_schema(value, OPTIONALS)


def test_optionals_valid_complex():
    value = {
        "required": "a-string",
        "not-required-complex": {"key": 123},
    }
    validator.validate_schema(value, OPTIONALS)


def test_optionals_invalid():
    value = {
        "required": "a-string",
        "not-required-simple": 123,
    }
    with pytest.raises(ValueError):
        validator.validate_schema(value, OPTIONALS)


def test_optionals_invalid_complex():
    value = {
        "required": "a-string",
        "not-required-complex": {"key": "invalid-value"},
    }
    with pytest.raises(ValueError):
        validator.validate_schema(value, OPTIONALS)
