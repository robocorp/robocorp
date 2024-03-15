import inspect
from typing import Any, Dict

from robocorp.tasks._customization._extension_points import EPManagedParameters


class ManagedParameters(EPManagedParameters):
    def __init__(self, kwargs: Dict[str, Any]):
        self.kwargs = kwargs

    def is_managed_param(self, param: inspect.Parameter) -> bool:
        return param.name in self.kwargs

    def inject_managed_params(
        self, sig: inspect.Signature, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        for k, v in self.kwargs.items():
            if k in sig.parameters:
                if k not in kwargs:
                    kwargs[k] = v

        return kwargs
