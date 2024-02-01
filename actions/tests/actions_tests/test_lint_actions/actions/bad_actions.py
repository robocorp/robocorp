from robocorp.actions import action


@action
def bad_action_no_return():
    """
    Empty...
    """


@action
def bad_action_no_docstring() -> str:
    return ""
