def ask_user_input_to_proceed(msg: str) -> bool:
    """
    Args:
        msg: The message to query user (should end with something as: "(y/n)\n").

    Returns:
        True to proceed and False otherwise.
    """
    try:
        while (c := input(msg).lower().strip()) not in ("y", "n"):
            continue
        if c == "n":
            return False
        # otherwise 'y' keep on going...
    except KeyboardInterrupt:
        return False

    return True
