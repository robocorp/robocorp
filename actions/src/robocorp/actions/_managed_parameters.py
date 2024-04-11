import inspect
from ast import FunctionDef
from typing import Any, Dict, Optional, overload

from robocorp.tasks._customization._extension_points import EPManagedParameters


class ManagedParameters:
    """
    Default implementation of EPManagedParameters.

    The idea is that in the constructor it receives the parameter names and
    the actual instance mapped from the parameter name.
    """

    def __init__(self, param_name_to_instance: Dict[str, Any]):
        self._param_name_to_instance = param_name_to_instance

    @overload
    def is_managed_param(self, param_name: str, *, node: FunctionDef) -> bool:
        raise NotImplementedError()

    @overload
    def is_managed_param(self, param_name: str, *, param: inspect.Parameter) -> bool:
        raise NotImplementedError()

    def is_managed_param(
        self,
        param_name: str,
        *,
        node: Optional[FunctionDef] = None,
        param: Optional[inspect.Parameter] = None,
    ) -> bool:
        import ast

        from robocorp.actions._secret import Secret

        if param_name in self._param_name_to_instance:
            return True

        if node is not None:
            assert (
                param is None
            ), "Either node or param is expected, but not both at the same time."
            is_managed = False
            args: ast.arguments = node.args
            for arg in args.args:
                if arg.arg == param_name:
                    if arg.annotation:
                        unparsed = ast.unparse(arg.annotation)
                        if unparsed in (
                            "Secret",
                            "actions.Secret",
                            "robocorp.actions.Secret",
                        ):
                            is_managed = True

                    break

            return is_managed

        elif param is not None:
            if param.annotation and issubclass(param.annotation, Secret):
                return True

        else:
            raise AssertionError("Either node or param must be passed.")

        return False

    def inject_managed_params(
        self,
        sig: inspect.Signature,
        new_kwargs: Dict[str, Any],
        original_kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        from robocorp.actions._action_context import ActionContext
        from robocorp.actions._secret import Secret

        use_kwargs = new_kwargs.copy()

        request = new_kwargs.get("request")
        if request is None:
            request = self._param_name_to_instance.get("request")

        x_action_context = ActionContext.from_request(request)

        for param in sig.parameters.values():
            if (
                param.name not in use_kwargs
                and param.name in self._param_name_to_instance
            ):
                use_kwargs[param.name] = self._param_name_to_instance[param.name]

            elif param.annotation and issubclass(param.annotation, Secret):
                # Handle a secret
                secret_value = original_kwargs.get(param.name)

                if secret_value is not None:
                    # Gotten directly from the input.json (or command line)
                    # as a value in the root.
                    use_kwargs[param.name] = Secret.model_validate(secret_value)

                elif x_action_context is not None:
                    use_kwargs[param.name] = Secret.from_action_context(
                        x_action_context, f"secrets/{param.name}"
                    )

        return use_kwargs

    def get_managed_param_type(
        self,
        param: inspect.Parameter,
    ) -> type:
        from robocorp.actions._request import Request
        from robocorp.actions._secret import Secret

        if param.name == "request":
            return Request

        if param.annotation and issubclass(param.annotation, Secret):
            return Secret

        raise RuntimeError(
            f"Unable to get managed parameter type for parameter: {param}"
        )

    def __typecheckself__(self) -> None:
        from robocorp.tasks._protocols import check_implements

        _: EPManagedParameters = check_implements(self)


def _get_secret_header_name(secret_name: str) -> str:
    secret_name = secret_name.replace("_", "-")
    return f"x-secret-{secret_name}"
