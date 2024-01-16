from robocorp.actions import action


@action
def calculator_sum(v1: float, v2: float) -> float:
    """
    Sums 2 numbers and returns them.

    Args:
        v1: First number.
        v2: Second number.

    Returns:
        The sum of v1 + v2.
    """
    return v1 + v2


@action
def broken_action() -> int:
    """
    This always raises an error.
    """
    raise RuntimeError("This is broken")


@action
def neverending_action() -> str:
    import time

    time.sleep(500)
    raise RuntimeError("Should never get here...")


@action
def bad_return_none():
    """
    Return None when string is expected
    """
