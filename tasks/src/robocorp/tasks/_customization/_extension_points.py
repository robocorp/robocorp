import inspect
from ast import FunctionDef
from typing import Any, Dict, Protocol, overload


class EPManagedParameters(Protocol):
    """
    The protocol for a class that describes the managed parameters when
    calling a task.
    """

    @overload
    def is_managed_param(self, param_name: str, *, node: FunctionDef) -> bool:
        """
        API to detect whether a given parameter is a managed parameter.

        Args:
            param_name: The name of the parameter.
            param: The FunctionDef to be checked (information in this case
                is gathered statically, when linting the action).

        Return: True if it's a managed parameter and False otherwise.
        """
        raise NotImplementedError()

    @overload
    def is_managed_param(self, param_name: str, *, param: inspect.Parameter) -> bool:
        """
        API to detect whether a given parameter is a managed parameter.

        Args:
            param_name: The name of the parameter.
            param: The inspect.Parameter to be checked (information in this case
                is gathered at runtime, when running the action).

        Return: True if it's a managed parameter and False otherwise.
        """
        raise NotImplementedError()

    def inject_managed_params(
        self,
        sig: inspect.Signature,
        new_kwargs: Dict[str, Any],
        original_kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        This enables the addition of managed parameters into a call to the task.

        Args:
            sig: The signature of the function being called.
            new_kwargs: The new kwargs (where the parameters should be injected).
            original_kwargs: The original kwargs passed to the function.
        """
        raise NotImplementedError()

    def get_managed_param_type(self, param: inspect.Parameter) -> type:
        """
        Provides the type of the given managed parameter.

        Args:
            param: The parameter for which the type is requested.

        Return: The type of the managed parameter.
        """
        raise NotImplementedError()
