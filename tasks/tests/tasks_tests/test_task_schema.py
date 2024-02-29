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

    task = Task(__name__, __file__, methoda)
    input_schema = task.input_schema
    assert input_schema == {
        "additionalProperties": False,
        "properties": {
            "a": {"title": "A", "type": "string", "description": "This is argument a."}
        },
        "required": ["a"],
        "type": "object",
    }

    task = Task(__name__, __file__, methodb)
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

    task = Task(__name__, __file__, methodb)
    output_schema = task.output_schema
    assert output_schema == {"type": "integer", "description": "The number 1."}

    task = Task(__name__, __file__, methoda, options=dict(is_consequential=True))
    options = task.options
    assert options["is_consequential"] is True


def test_task_schema_default_value_type():
    from robocorp.tasks._task import Task

    task = Task(__name__, __file__, methodc)
    input_schema = task.input_schema
    assert input_schema == {
        "additionalProperties": False,
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


def methodd(a: int = 1) -> int:
    """
    This is a method. In this method
    the description spans multiple lines
    and this must be properly supported
    in the spec.

    Args:
        a: This is argument a.

    Returns:
        The number 1.
    """
    return 1


def test_task_schema_multiple_lines_in_description():
    from robocorp.tasks._task import Task

    task = Task(__name__, __file__, methodd)
    print(task.__doc__)
