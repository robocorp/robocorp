import sys


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


def test_task_schema():
    from robocorp.tasks._task import Task

    task = Task(sys.modules[__name__], methoda)
    input_schema = task.input_schema
    assert input_schema == {
        "additionalProperties": False,
        "properties": {
            "a": {"title": "A", "type": "string", "description": "This is argument a."}
        },
        "required": ["a"],
        "type": "object",
    }

    task = Task(sys.modules[__name__], methodb)
    input_schema = task.input_schema
    assert input_schema == {
        "additionalProperties": False,
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

    task = Task(sys.modules[__name__], methodb)
    output_schema = task.output_schema
    assert output_schema == {"type": "integer", "description": "The number 1."}

    task = Task(sys.modules[__name__], methoda, options=dict(is_consequential=True))
    options = task.options
    assert options["is_consequential"] is True
