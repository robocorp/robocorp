from robocorp.actions import Secret, action


@action
def hello(name: str, private_info: Secret) -> str:
    """
    Provides a greeting for a person.

    Args:
        name: The name of the person to greet.
        private_info: Some private information gotten from the

    Returns:
        The greeting for the person.
    """
    return f"Hello {name}. Private info: {private_info.value}"
