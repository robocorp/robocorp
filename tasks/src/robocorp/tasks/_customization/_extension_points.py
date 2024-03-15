import inspect
from typing import Any, Dict


class EPManagedParameters:
    def is_managed_param(self, param: inspect.Parameter) -> bool:
        raise NotImplementedError()

    def inject_managed_params(
        self, sig: inspect.Signature, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        raise NotImplementedError()

    def get_managed_param_type(
        self,
        param: inspect.Parameter,
    ) -> type:
        raise NotImplementedError()
