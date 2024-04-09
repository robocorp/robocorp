import typing

if typing.TYPE_CHECKING:
    from robocorp.actions._action_context import ActionContext


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

    Note: this class is abstract and is not meant to be instanced by clients.
        An instance can be created from one of the factory methods (`model_validate`
        or `from_action_context`).
    """

    @classmethod
    def model_validate(cls, value: str) -> "Secret":
        """
        Creates a secret given a string (expected when the user
        is passing the arguments using a json input).

        Args:
            value: The raw-text value to be used in the secret.

        Return: A Secret instance with the given value.

        Note: the model_validate method is used for compatibility with
            the pydantic API.
        """
        return _RawSecret(value)

    @classmethod
    def from_action_context(
        cls, action_context: "ActionContext", path: str
    ) -> "Secret":
        """
        Creates a secret given the action context (which may be encrypted
        in memory until the actual secret value is requested).

        Args:
            action_context: The action context which has the secret.

            path: The path inside of the action context for the secret data
            requested (Example: 'secrets/my_secret_name').

        Return: A Secret instance collected from the passed action context.
        """
        return _SecretInActionContext(action_context, path)

    @property
    def value(self) -> str:
        raise NotImplementedError(
            "The Secret class is abstract and should not be directly used."
        )


class _RawSecret(Secret):
    """
    Internal API to wrap a secret which is not passed encrypted.
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


class _SecretInActionContext(Secret):
    """
    Internal API to wrap a secret which is passed encrypted.
    """

    def __init__(self, action_context: "ActionContext", path: str):
        """
        Args:
            action_context: The action context.
            path: the path of the data required inside of the action context
                (a '/' splitted path, for instance: 'secrets/my_passwd')
        """
        if not path:
            raise RuntimeError("A valid path must be passed.")

        self._action_context = action_context
        self._paths = path.split("/")

    @property
    def value(self) -> str:
        """
        Provides the actual secret wrapped in this class.
        """
        from robocorp import log

        with log.suppress():
            dct = self._action_context.value

            v = None
            for path in self._paths:
                if not isinstance(dct, dict):
                    dct = None  # Remove from context
                    raise RuntimeError(
                        f"Unable to get path: {self._paths} in action context (expected dict to get {path!r} from)."
                    )
                try:
                    dct = v = dct[path]
                except KeyError:
                    dct = None  # Remove from context
                    raise RuntimeError(
                        f"Unable to get path: {self._paths} in action context (current path: {path!r})."
                    )

            dct = None  # Remove from context
            if v is None:
                raise RuntimeError(
                    f"Error. Path ({self._paths}) invalid for the action context."
                )

            if not isinstance(v, str):
                del v
                raise RuntimeError(
                    f"Error. Path ({self._paths}) did not map to a string in the action context."
                )

            return v
