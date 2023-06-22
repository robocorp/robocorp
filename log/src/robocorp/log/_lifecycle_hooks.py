import sys
from collections import deque
from logging import getLogger
from typing import Iterator, Tuple

from robocorp import log

logger = getLogger(__name__)


class _OnExitContextManager:
    def __init__(self, on_exit):
        self.on_exit = on_exit

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_exit()


class Callback(object):
    """
    Note that it's thread safe to register/unregister callbacks while callbacks
    are being notified, but it's not thread-safe to register/unregister at the
    same time in multiple threads.
    """

    def __init__(self):
        self.raise_exceptions = False
        self._callbacks = ()

    def register(self, callback):
        self._callbacks = self._callbacks + (callback,)

        # Enable using as a context manager to automatically call the unregister.
        return _OnExitContextManager(lambda: self.unregister(callback))

    def unregister(self, callback):
        self._callbacks = tuple(x for x in self._callbacks if x != callback)

    def __call__(self, *args, **kwargs):
        for c in self._callbacks:
            try:
                c(*args, **kwargs)
            except:
                logger.exception(f"Error calling: {c} with: {args} {kwargs}.")
                if self.raise_exceptions:
                    raise


# Called as: before_method(log_element_type, __name__, filename, name, lineno, args_dict)
before_method = Callback()

# Called as: after_method(log_element_type, __name__, filename, name, lineno)
after_method = Callback()

# Called as: method_return(__name__, filename, name, lineno, return_value)
method_return = Callback()

# Called as: method_except(__name__, filename, name, lineno, exc_info)
# tp, e, tb = exc_info
method_except = Callback()

# Called as: method_if(__name__, filename, name, lineno, variables)
# variables is a tuple(tuple(variable_name, variable_value))
method_if = Callback()

# Called as: method_else(__name__, filename, name, lineno, variables)
# variables is a tuple(tuple(variable_name, variable_value))
method_else = Callback()

# Called as: after_assign(__name__, filename, name, lineno, assign_name, assign_value)
after_assign = Callback()

# Called as: before_yield(__name__, filename, name, lineno, yielded_value)
before_yield = Callback()

# Called as: after_yield(__name__, filename, name, lineno)
after_yield = Callback()

# Called as: before_yield_from(__name__, filename, name, lineno)
before_yield_from = Callback()

# Called as: after_yield_from(__name__, filename, name, lineno)
after_yield_from = Callback()

# Called as: before_iterate(log_element_type, __name__, filename, name, lineno)
before_iterate = Callback()

# Called as: iterate_except(log_element_type, __name__, filename, name, lineno, exc_info)
# tp, e, tb = exc_info
iterate_except = Callback()

# Called as: before_iterate_step(log_element_type, __name__, filename, name, lineno, targets)
# targets is a tuple(tuple(target_name, target_value))
before_iterate_step = Callback()

# Called as: after_iterate_step(log_element_type, __name__, filename, name, lineno)
after_iterate_step = Callback()

# Called as: iterate_step_except(log_element_type, __name__, filename, name, lineno, exc_info)
# tp, e, tb = exc_info
iterate_step_except = Callback()

# Called as: after_iterate(log_element_type, __name__, filename, name, lineno)
after_iterate = Callback()


def iter_all_callbacks() -> Iterator[Callback]:
    for _key, val in tuple(globals().items()):
        if isinstance(val, Callback):
            yield val


def iter_all_name_and_callback() -> Iterator[Tuple[str, Callback]]:
    for key, val in tuple(globals().items()):
        if isinstance(val, Callback):
            yield (key, val)


_name_to_callback = {}
for k, v in iter_all_name_and_callback():
    _name_to_callback[k] = v
del k
del v


class MethodLifecycleContext:
    """
    See: robocorp_log_tests.test_rewrite_strategy tests to see how the
    code should be generated.
    """

    # Flag which subclasses can override.
    _accept = True

    def __init__(self, tup):
        if not self._accept:
            return

        self._stack = deque()

        # tup is log_element_type, mod_name, filename, name, lineno, args_dict
        before_method(*tup)

        # The after doesn't have the args_dict.
        self._stack.append((-1, "method", tup[:-1]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._accept:
            return

        while self._stack:
            _report_id, method_name, tup = self._stack.pop()

            if exc_type is not None and exc_val is not None:
                exc_info = (exc_type, exc_val, exc_tb)
                # Something as 'method_except' or 'iterate_except'
                method = _name_to_callback[f"{method_name}_except"]
                method(*tup, exc_info)

            # Something as 'after_method' or 'after_iterate'
            method = _name_to_callback[f"after_{method_name}"]
            method(*tup)

    def report_for_start(self, report_id, tup):
        if not self._accept:
            return

        # tup is (log_element_type, __name__, filename, name, lineno)
        before_iterate(*tup)
        self._stack.append((report_id, "iterate", tup))

    report_while_start = report_for_start

    def report_for_step_start(self, report_id, tup):
        if not self._accept:
            return

        # tup is (log_element_type, __name__, filename, name, lineno, targets)
        before_iterate_step(*tup)
        self._stack.append((report_id, "iterate_step", tup[:-1]))

    report_while_step_start = report_for_step_start

    def _report_end(self, report_id):
        if not self._accept:
            return

        while self._stack:
            stack_report_id, method_name, tup = self._stack.pop()

            method = _name_to_callback[f"after_{method_name}"]
            method(*tup)

            if stack_report_id == report_id:
                break

    report_for_end = _report_end
    report_for_step_end = _report_end
    report_while_end = _report_end
    report_while_step_end = _report_end

    def report_exception(self, report_ids):
        if not self._accept:
            return

        while self._stack:
            stack_report_id = self._stack[-1][0]
            if stack_report_id not in report_ids:
                break
            stack_report_id, method_name, tup = self._stack.pop()

            exc_info = sys.exc_info()
            # Something as 'method_except' or 'iterate_except'
            method = _name_to_callback[f"{method_name}_except"]
            method(*tup, exc_info)

            method = _name_to_callback[f"after_{method_name}"]
            method(*tup)


class MethodLifecycleContextCallerInProject(MethodLifecycleContext):
    def __init__(self, tup):
        self._caller_in_project_roots = log._caller_in_project_roots(level=3)
        self._accept = self._caller_in_project_roots

        MethodLifecycleContext.__init__(self, tup)
