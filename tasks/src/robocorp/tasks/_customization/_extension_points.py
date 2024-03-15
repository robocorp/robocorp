import inspect
from typing import Any, Dict, Protocol


class EPManagedParameters(Protocol):
    """
    The protocol for a class that describes the managed parameters when
    calling a task.
    """

    def is_managed_param(self, param_name: str) -> bool:
        raise NotImplementedError()

    def inject_managed_params(
        self, sig: inspect.Signature, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        raise NotImplementedError()

    def get_managed_param_type(
        self,
        param_name: str,
    ) -> type:
        raise NotImplementedError()
