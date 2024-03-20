from typing import Union

from pydantic import BaseModel

from robocorp.tasks._customization._plugin_manager import PluginManager


def methoda(a: str) -> int:
    """
    This is methoda.

    Args:
        a: This is argument a.
    """
    return 1


def methodb(a: str = "a") -> int:
    """
    This is methodb.

    Args:
        a: This is argument a.

    Returns:
        The number 1.
    """
    return 1


def methodc(a: int = 1) -> int:
    """
    This is methodc.

    Args:
        a: This is argument a.

    Returns:
        The number 1.
    """
    return 1


def test_task_schema():
    from robocorp.tasks._task import Task

    task = Task(PluginManager(), __name__, __file__, methoda)
    input_schema = task.input_schema
    assert input_schema == {
        "properties": {
            "a": {"title": "A", "type": "string", "description": "This is argument a."}
        },
        "required": ["a"],
        "type": "object",
    }

    task = Task(PluginManager(), __name__, __file__, methodb)
    input_schema = task.input_schema
    assert input_schema == {
        "properties": {
            "a": {
                "default": "a",
                "title": "A",
                "type": "string",
                "description": "This is argument a.",
            }
        },
        "type": "object",
    }

    task = Task(PluginManager(), __name__, __file__, methodb)
    output_schema = task.output_schema
    assert output_schema == {"type": "integer", "description": "The number 1."}

    task = Task(
        PluginManager(),
        __name__,
        __file__,
        methoda,
        options=dict(is_consequential=True),
    )
    options = task.options
    assert options["is_consequential"] is True


def test_task_schema_default_value_type():
    from robocorp.tasks._task import Task

    task = Task(PluginManager(), __name__, __file__, methodc)
    input_schema = task.input_schema
    assert input_schema == {
        "properties": {
            "a": {
                "default": 1,
                "title": "A",
                "type": "integer",
                "description": "This is argument a.",
            }
        },
        "type": "object",
    }


def unicode_ação_Σ(ação: int = 1) -> int:
    """
    This is a method. In this method
    the description spans multiple lines
    and this must be properly supported
    in the spec.

    Args:
        ação: This is an argument

    Returns:
        The number 1.
    """
    return 1


def test_task_unicode():
    from robocorp.tasks._task import Task

    task = Task(PluginManager(), __name__, __file__, unicode_ação_Σ)
    input_schema = task.input_schema
    assert input_schema == {
        "properties": {
            "ação": {
                "type": "integer",
                "description": "This is an argument",
                "title": "Ação",
                "default": 1,
            }
        },
        "type": "object",
    }


class MyCustomData(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


def method_custom_type(a: MyCustomData) -> MyCustomData:
    return a


def test_task_schema_custom_type():
    from robocorp.tasks._task import Task

    task = Task(PluginManager(), __name__, __file__, method_custom_type)
    input_schema = task.input_schema
    assert input_schema == {
        "properties": {
            "a": {
                "properties": {
                    "name": {"title": "Name", "type": "string"},
                    "price": {"title": "Price", "type": "number"},
                    "is_offer": {
                        "anyOf": [{"type": "boolean"}, {"type": "null"}],
                        "default": None,
                        "title": "Is Offer",
                    },
                },
                "required": ["name", "price"],
                "title": "A",
                "type": "object",
            }
        },
        "type": "object",
        "required": ["a"],
    }

    output_schema = task.output_schema
    assert output_schema == {
        "properties": {
            "name": {"title": "Name", "type": "string"},
            "price": {"title": "Price", "type": "number"},
            "is_offer": {
                "anyOf": [{"type": "boolean"}, {"type": "null"}],
                "default": None,
                "title": "Is Offer",
            },
        },
        "required": ["name", "price"],
        "title": "MyCustomData",
        "type": "object",
    }


class Dependent(BaseModel):
    city: str


class MyDataWithDependent(BaseModel):
    name: str
    dependent: Dependent


def method_custom_dependent_type(a: MyDataWithDependent) -> MyDataWithDependent:
    return a


def test_task_schema_dependent_type():
    from robocorp.tasks._task import Task

    task = Task(PluginManager(), __name__, __file__, method_custom_dependent_type)
    input_schema = task.input_schema
    assert input_schema == {
        "properties": {
            "a": {
                "properties": {
                    "name": {"title": "Name", "type": "string"},
                    "dependent": {
                        "properties": {"city": {"title": "City", "type": "string"}},
                        "required": ["city"],
                        "title": "Dependent",
                        "type": "object",
                    },
                },
                "required": ["name", "dependent"],
                "title": "A",
                "type": "object",
            }
        },
        "type": "object",
        "required": ["a"],
    }

    output_schema = task.output_schema
    assert output_schema == {
        "properties": {
            "name": {"title": "Name", "type": "string"},
            "dependent": {
                "properties": {"city": {"title": "City", "type": "string"}},
                "required": ["city"],
                "title": "Dependent",
                "type": "object",
            },
        },
        "required": ["name", "dependent"],
        "title": "MyDataWithDependent",
        "type": "object",
    }
