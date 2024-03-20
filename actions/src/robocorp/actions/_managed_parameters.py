import inspect
from typing import Any, Dict

from robocorp.tasks._customization._extension_points import EPManagedParameters


class ManagedParameters:
    """
    Default implementation of EPManagedParameters.

    The idea is that in the constructor it receives the parameter names and
    the actual instance mapped from the parameter name.
    """

    def __init__(self, param_name_to_instance: Dict[str, Any]):
        self._param_name_to_instance = param_name_to_instance

    def is_managed_param(self, param_name: str) -> bool:
        return param_name in self._param_name_to_instance

    def inject_managed_params(
        self, sig: inspect.Signature, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        for k, v in self._param_name_to_instance.items():
            if k in sig.parameters:
                if k not in kwargs:
                    kwargs[k] = v

        return kwargs

    def get_managed_param_type(
        self,
        param_name: str,
    ) -> type:
        return type(self._param_name_to_instance[param_name])

    def __typecheckself__(self) -> None:
        from robocorp.tasks._protocols import check_implements

        _: EPManagedParameters = check_implements(self)
