from io import StringIO

import pytest

from robo_log._rewrite_config import BaseConfig, ConfigFilesFiltering
from contextlib import contextmanager


def test_ast_utils():
    from robo_log import _ast_utils
    import ast

    node = ast.parse(
        """
try:
    print({'a': c, 1: d})
except:
    on_except(sys.exc_info())
    raise
""",
        filename="<string>",
    )
    s = StringIO()
    _ast_utils.print_ast(node, stream=s)
    assert "Name" in s.getvalue()


class ConfigForTest(BaseConfig):
    def can_rewrite_module_name(self, module_name: str) -> bool:
        return "check" in module_name

    def can_rewrite_module(self, module_name: str, filename: str) -> bool:
        return "check" in module_name


class _SetupCallback:
    def __init__(self):
        self.check = None  # To be set by the test function
        self.found = []

    def before_method(self, package, mod_name, filename, name, lineno, args_dict):
        check = self.check
        assert package == check.__package__
        assert filename == check.__file__
        assert mod_name == check.__name__
        assert lineno > 0
        self.found.append(("before", name, args_dict))

    def after_method(self, package, mod_name, filename, name, lineno):
        assert package == self.check.__package__
        assert filename == self.check.__file__
        assert mod_name == self.check.__name__
        assert lineno > 0
        self.found.append(("after", name))

    def method_return(self, package, mod_name, filename, name, lineno, return_value):
        assert package == self.check.__package__
        assert filename == self.check.__file__
        assert mod_name == self.check.__name__
        assert lineno > 0
        self.found.append(("return", name, return_value))

    def method_except(self, package, mod_name, filename, name, lineno, exc_info):
        assert package == self.check.__package__
        assert filename == self.check.__file__
        assert mod_name == self.check.__name__
        tp, e, tb = exc_info
        assert "Fail here" in str(e)
        assert lineno > 0
        self.found.append(("except", name, lineno))


@contextmanager
def _setup_test_callbacks():
    from robo_log import _rewrite_callbacks

    setup_callback = _SetupCallback()

    with _rewrite_callbacks.before_method.register(
        setup_callback.before_method
    ), _rewrite_callbacks.after_method.register(
        setup_callback.after_method
    ), _rewrite_callbacks.method_return.register(
        setup_callback.method_return
    ), _rewrite_callbacks.method_except.register(
        setup_callback.method_except
    ):
        yield setup_callback


@pytest.mark.parametrize("config", [ConfigForTest(), ConfigFilesFiltering()])
def test_rewrite_hook_basic(config):
    from robo_log._rewrite_hook import RewriteHook
    import sys
    from imp import reload
    from robo_log_tests._resources import check

    hook = RewriteHook(config)
    sys.meta_path.insert(0, hook)

    try:
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
    finally:
        sys.meta_path.remove(hook)


@pytest.mark.parametrize("config", [ConfigForTest()])
def test_rewrite_hook_except(config):
    from robo_log._rewrite_hook import RewriteHook
    import sys
    from imp import reload
    from robo_log_tests._resources import check_traceback

    hook = RewriteHook(config)
    sys.meta_path.insert(0, hook)

    try:
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
                ("except", "sub_method", 2),
                ("after", "sub_method"),
                ("except", "another_method", 6),
                ("after", "another_method"),
                ("except", "main", 10),
                ("after", "main"),
            ]
    finally:
        sys.meta_path.remove(hook)
