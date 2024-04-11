from robocorp.actions import Secret, action


@action
def get_private(private_info: Secret) -> str:
    """
    Returns the value passed to the private key.

    Returns:
        The value of the private key.
    """
    return private_info.value
