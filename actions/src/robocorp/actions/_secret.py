class Secret:
    """
    This class should be used to receive secrets.

    The way to use it is by declaring a variable with the 'Secret' type
    in the @action.

    Example:

        ```
        from robocorp.actions import action, Secret

        @action
        def my_action(password: Secret):
            login(password.value)
        ```
    """

    def __init__(self, value: str):
        """
        Args:
            value: The secret value to be wrapped in this class (note that
                it's automatically hidden in the logs).
        """
        from robocorp import log

        log.hide_from_output(value)
        log.hide_from_output(repr(value))
        self.__value = value

    @property
    def value(self) -> str:
        """
        Provides the actual secret wrapped in this class.
        """
        return self.__value

    @classmethod
    def model_validate(cls, value: str) -> "Secret":
        """
        Creates a secret given a string (expected when the user
        is passing the arguments using a json input).

        Args:
            value: The raw-text value to be used in the secret.

        Return: A Secret instance with the given value.
        """
        return Secret(value)
