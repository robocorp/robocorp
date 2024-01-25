from contextlib import contextmanager

import pytest
from robocorp_log_tests.fixtures import AutoLogConfigForTest

from robocorp.log._config import DefaultAutoLogConfig
from robocorp.log.protocols import LogElementType


class _SetupCallback:
    def __init__(self):
        self.check = None  # To be set by the test function
        self.found = []

    def before_method(
        self, method_type: LogElementType, mod_name, filename, name, lineno, args_dict
    ):
        check = self.check
        if check:
            assert filename == check.__file__
            assert mod_name == check.__name__
            assert lineno > 0
        self.found.append(("before", name, args_dict))

    def after_method(
        self, method_type: LogElementType, mod_name, filename, name, lineno
    ):
        check = self.check
        if check:
            assert filename == check.__file__
            assert mod_name == check.__name__
            assert lineno > 0
        self.found.append(("after", name))

    def method_return(self, mod_name, filename, name, lineno, return_value):
        check = self.check
        if check:
            assert filename == check.__file__
            assert mod_name == check.__name__
            assert lineno > 0
        self.found.append(("return", name, return_value))

    def method_except(
        self, method_type: LogElementType, mod_name, filename, name, lineno, exc_info
    ):
        check = self.check
        if check:
            assert filename == check.__file__
            assert mod_name == check.__name__
        tp, e, tb = exc_info
        assert "Fail here" in str(e)
        assert lineno > 0
        self.found.append(("except", name, lineno))


@contextmanager
def _setup_test_callbacks():
    from robocorp.log import _lifecycle_hooks

    setup_callback = _SetupCallback()

    with _lifecycle_hooks.before_method.register(
        setup_callback.before_method
    ), _lifecycle_hooks.after_method.register(
        setup_callback.after_method
    ), _lifecycle_hooks.method_return.register(
        setup_callback.method_return
    ), _lifecycle_hooks.method_except.register(setup_callback.method_except):
        yield setup_callback


@pytest.mark.parametrize("config", [AutoLogConfigForTest(), DefaultAutoLogConfig()])
def test_rewrite_hook_basic(config):
    from importlib import reload

    from robocorp_log_tests._resources import check

    from robocorp.log._auto_logging_setup import add_import_hook
    from robocorp.log._rewrite_importhook import RewriteHook

    hook = RewriteHook(config)
    with add_import_hook(hook):
        check = reload(check)
        assert "call_another_method" in check.call_another_method.__doc__
        with _setup_test_callbacks() as setup_callback:
            setup_callback.check = check
            check.some_method()
            check.SomeClass(1, 2)
            assert setup_callback.found == [
                ("before", "some_method", {}),
                (
                    "before",
                    "call_another_method",
                    {
                        "param0": 1,
                        "param1": "arg",
                        "args": (["a", "b"],),
                        "kwargs": {"c": 3},
                    },
                ),
                ("after", "call_another_method"),
                ("return", "some_method", 22),
                ("after", "some_method"),
                ("before", "SomeClass.__init__", {"arg1": 1, "arg2": 2}),
                ("after", "SomeClass.__init__"),
            ]


def test_rewrite_hook_except():
    from importlib import reload

    from robocorp_log_tests._resources import check_traceback

    from robocorp.log._auto_logging_setup import add_import_hook
    from robocorp.log._rewrite_importhook import RewriteHook

    config = AutoLogConfigForTest()

    hook = RewriteHook(config)
    with add_import_hook(hook):
        check = reload(check_traceback)
        with _setup_test_callbacks() as setup_callback:
            setup_callback.check = check
            try:
                check.main()
            except RuntimeError:
                pass
            else:
                raise AssertionError("Expected exception.")
            assert setup_callback.found == [
                ("before", "main", {}),
                ("before", "another_method", {}),
                ("before", "sub_method", {"arg_name": ("arg", "name", 1)}),
                ("except", "sub_method", 1),
                ("after", "sub_method"),
                ("except", "another_method", 5),
                ("after", "another_method"),
                ("except", "main", 9),
                ("after", "main"),
            ]


def test_rewrite_hook_log_on_project_call():
    from importlib import reload
    from unittest import mock

    from robocorp_log_tests._resources import check_lib_lib, check_lib_main

    from robocorp import log as robolog
    from robocorp.log._auto_logging_setup import add_import_hook
    from robocorp.log._rewrite_importhook import RewriteHook

    config = AutoLogConfigForTest()

    hook = RewriteHook(config)
    with add_import_hook(hook):
        check_lib_lib = reload(check_lib_lib)
        check_lib_main = reload(check_lib_main)

        def dummy_in_project_roots(filename):
            if "check_lib_lib.py" in filename:
                return False
            return True

        with mock.patch.object(robolog, "_in_project_roots", dummy_in_project_roots):
            with _setup_test_callbacks() as setup_callback:
                check_lib_main.main()

                assert setup_callback.found == [
                    ("before", "main", {}),
                    ("before", "in_lib", {}),
                    ("after", "in_lib"),
                    ("after", "main"),
                ]
