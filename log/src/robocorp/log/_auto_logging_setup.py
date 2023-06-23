import sys
import threading
from typing import Any, List, Optional, Sequence, Tuple

from robocorp.log import critical, is_sensitive_variable_name

from ._config import BaseConfig
from ._logger_instances import _get_logger_instances
from ._obj_info_repr import get_obj_type_and_repr
from ._on_exit_context_manager import OnExitContextManager
from .protocols import LogElementType, OptExcInfo, Status


def _get_obj_type_and_repr_and_hide_if_needed(key, val):
    obj_type, obj_repr = get_obj_type_and_repr(val)

    if is_sensitive_variable_name(key):
        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.hide_from_output(obj_repr)
                if isinstance(val, str):
                    robo_logger.hide_from_output(val)
    return obj_type, obj_repr


class _StackEntry:
    __slots__ = "mod_name name status".split()

    def __init__(self, mod_name, name, status):
        self.mod_name = mod_name
        self.name = name
        self.status = status


class _AutoLogging:
    """
    Class responsible for listening for callbacks and then dispatching those
    to the logger.
    """

    def __init__(self, rewrite_hook_config: BaseConfig) -> None:
        from ._rewrite_importhook import RewriteHook

        self.tid = threading.get_ident()
        self.status_stack: List[_StackEntry] = []
        self._rewrite_hook_config = rewrite_hook_config
        self._hook: Optional[RewriteHook] = None

    def register(self, add_rewrite_hook: bool = True) -> None:
        from robocorp.log import _lifecycle_hooks

        for name, callback in _lifecycle_hooks.iter_all_name_and_callback():
            callback.register(getattr(self, f"call_{name}"))

        if add_rewrite_hook:
            from ._rewrite_importhook import RewriteHook

            self._hook = hook = RewriteHook(self._rewrite_hook_config)
            sys.meta_path.insert(0, hook)

    def unregister(self, add_rewrite_hook: bool = True) -> None:
        from robocorp.log import _lifecycle_hooks

        for name, callback in _lifecycle_hooks.iter_all_name_and_callback():
            callback.unregister(getattr(self, f"call_{name}"))

        if add_rewrite_hook:
            assert self._hook
            sys.meta_path.remove(self._hook)
            self._hook = None

    def _call_before_element(
        self,
        method_type: LogElementType,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        args: List[Tuple[str, str, str]],
    ) -> None:
        if self.tid != threading.get_ident():
            return

        if method_type != "UNTRACKED_GENERATOR":
            # We don't change the stack for untracked generators
            # because we don't know when they may yield.
            self.status_stack.append(_StackEntry(mod_name, name, "PASS"))

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.start_element(
                    name,
                    mod_name,
                    filename,
                    lineno,
                    method_type,
                    "",
                    args,
                )

    def call_before_method(
        self,
        method_type: LogElementType,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        args_dict: dict,
    ) -> None:
        if self.tid != threading.get_ident():
            return
        args: List[Tuple[str, str, str]] = []
        for key, val in args_dict.items():
            obj_type, obj_repr = _get_obj_type_and_repr_and_hide_if_needed(key, val)
            args.append((f"{key}", obj_type, obj_repr))
        self._call_before_element(method_type, mod_name, filename, name, lineno, args)

    def call_before_iterate_step(
        self,
        method_type: LogElementType,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        targets: Sequence[Tuple[str, Any]],
    ) -> None:
        if self.tid != threading.get_ident():
            return
        args: List[Tuple[str, str, str]] = []
        if targets is not None:
            for key, val in targets:
                obj_type, obj_repr = _get_obj_type_and_repr_and_hide_if_needed(key, val)
                args.append((f"{key}", obj_type, obj_repr))
        self._call_before_element(method_type, mod_name, filename, name, lineno, args)

    def call_before_iterate(
        self,
        method_type: LogElementType,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
    ) -> None:
        self._call_before_element(method_type, mod_name, filename, name, lineno, [])

    def _call_after_element(
        self,
        method_type: LogElementType,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        status = "PASS"
        if method_type != "UNTRACKED_GENERATOR":
            try:
                pop_stack_entry = self.status_stack.pop(-1)
            except IndexError:
                # oops, something bad happened, the stack is unsynchronized
                critical("On method return the status_stack was empty.")
                return
            else:
                if pop_stack_entry.mod_name != mod_name or pop_stack_entry.name != name:
                    critical(
                        f"On method return status stack package/name was: {pop_stack_entry.mod_name}.{pop_stack_entry.name}. Received: {mod_name}.{name}."
                    )
                    return
            status = pop_stack_entry.status

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.end_method(method_type, name, mod_name, status)

    call_after_method = _call_after_element
    call_after_iterate = _call_after_element
    call_after_iterate_step = _call_after_element

    def call_before_yield(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        yielded_value: Any,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        try:
            pop_stack_entry = self.status_stack.pop(-1)
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On before yield the status_stack was empty.")
            return
        else:
            if pop_stack_entry.mod_name != mod_name or pop_stack_entry.name != name:
                critical(
                    f"On before yield status stack package/name was: {pop_stack_entry.mod_name}.{pop_stack_entry.name}. Received: {mod_name}.{name}."
                )
                return

        yielded_value_type, yielded_value_repr = get_obj_type_and_repr(yielded_value)

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.yield_suspend(
                    name,
                    mod_name,
                    filename,
                    lineno,
                    yielded_value_type,
                    yielded_value_repr,
                )

    def call_after_yield(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        self.status_stack.append(_StackEntry(mod_name, name, "PASS"))

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.yield_resume(name, mod_name, filename, lineno)

    def call_method_if(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        variables: Sequence[Tuple[str, Any]],
    ) -> None:
        if self.tid != threading.get_ident():
            return

        variables_name_type_repr = []
        if variables is not None:
            for key, val in variables:
                obj_type, obj_repr = _get_obj_type_and_repr_and_hide_if_needed(key, val)
                variables_name_type_repr.append((f"{key}", obj_type, obj_repr))

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.start_element(
                    name,
                    mod_name,
                    filename,
                    lineno,
                    "IF",
                    "",
                    variables_name_type_repr,
                )

    def call_method_else(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        variables: Sequence[Tuple[str, Any]],
    ) -> None:
        if self.tid != threading.get_ident():
            return

        variables_name_type_repr = []
        if variables is not None:
            for key, val in variables:
                obj_type, obj_repr = _get_obj_type_and_repr_and_hide_if_needed(key, val)
                variables_name_type_repr.append((f"{key}", obj_type, obj_repr))

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.start_element(
                    name,
                    mod_name,
                    filename,
                    lineno,
                    "ELSE",
                    "",
                    variables_name_type_repr,
                )

    def call_before_yield_from(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        try:
            pop_stack_entry = self.status_stack.pop(-1)
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On before yield from the status_stack was empty.")
            return
        else:
            if pop_stack_entry.mod_name != mod_name or pop_stack_entry.name != name:
                critical(
                    f"On before yield from status stack package/name was: {pop_stack_entry.mod_name}.{pop_stack_entry.name}. Received: {mod_name}.{name}."
                )
                return

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.yield_from_suspend(name, mod_name, filename, lineno)

    def call_after_yield_from(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        self.status_stack.append(_StackEntry(mod_name, name, "PASS"))

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.yield_from_resume(name, mod_name, filename, lineno)

    def call_after_assign(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        assign_name: str,
        assign_value: Any,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        assign_type, assign_repr = _get_obj_type_and_repr_and_hide_if_needed(
            assign_name, assign_value
        )

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.after_assign(
                    name,
                    mod_name,
                    filename,
                    lineno,
                    assign_name,
                    assign_type,
                    assign_repr,
                )

    def call_method_return(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        return_value: Any,
    ):
        if self.tid != threading.get_ident():
            return

        return_type, return_repr = _get_obj_type_and_repr_and_hide_if_needed(
            "", return_value
        )

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.method_return(
                    name,
                    mod_name,
                    filename,
                    lineno,
                    return_type,
                    return_repr,
                )

    def call_method_except(
        self,
        method_type: LogElementType,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        exc_info: OptExcInfo,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        if method_type == "UNTRACKED_GENERATOR":
            # TODO: Investigate: in this case maybe we should create a dummy
            # stack entry? -- Must verify how it'd look in the UI.
            pass

        try:
            _stack_entry = self.status_stack[-1]
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On method except the status_stack was empty.")
            return

        self.status_stack[-1].status = Status.ERROR

        # We just want to report it once. On other cases it should just be
        # marked as failed.
        # We should probably have a concept of a "reference" to note that another
        # context exited to an exception already reported.
        tp, e, tb = exc_info
        if e is None or tb is None or tp is None:
            return

        try:
            if e.__robocorp_log_reported__:  # type: ignore
                return
        except Exception:
            try:
                e.__robocorp_log_reported__ = True  # type: ignore
            except Exception:
                pass

        with _get_logger_instances() as logger_instances:
            for robo_logger in logger_instances:
                robo_logger.log_method_except(exc_info, unhandled=False)

    call_iterate_except = call_method_except
    call_iterate_step_except = call_method_except


def register_auto_logging_callbacks(
    rewrite_hook_config: BaseConfig, add_rewrite_hook: bool = True
):
    # Make sure that this method should be called only once.
    registered = getattr(register_auto_logging_callbacks, "registered", False)
    if registered:
        import warnings

        warnings.warn("Auto logging is already setup. 2nd call has no effect.")
        return OnExitContextManager(lambda: None)
    register_auto_logging_callbacks.registered = True  # type: ignore

    auto_logging = _AutoLogging(rewrite_hook_config)
    auto_logging.register(add_rewrite_hook=add_rewrite_hook)

    def _exit():
        # If the user actually used the with ... statement we'll remove things now.
        # Note: this is meant only for testing as it has caveats (mainly, modules
        # already loaded won't be rewritten and will have the hooks based on
        # the config which was set when it was loaded).
        auto_logging.unregister(add_rewrite_hook=add_rewrite_hook)
        register_auto_logging_callbacks.registered = False

    return OnExitContextManager(_exit)
