from io import StringIO

import pytest

from robocorp_logging._rewrite_config import BaseConfig, ConfigFilesFiltering


def test_ast_utils():
    from robocorp_logging import _ast_utils
    import ast

    node = ast.parse(
        """
print({'a': c, 1: d})
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


@pytest.mark.parametrize("config", [ConfigForTest(), ConfigFilesFiltering()])
def test_rewrite_hook_basic(config):
    from robocorp_logging._rewrite_hook import RewriteHook
    import sys
    from robocorp_logging import _rewrite_callbacks
    from imp import reload
    from robocorp_logging_tests._resources import check

    hook = RewriteHook(config)
    sys.meta_path.insert(0, hook)

    try:
        check = reload(check)

        found = []

        def before_method(package, filename, name, lineno, args_dict):
            assert package == check.__package__
            assert filename == check.__file__
            assert lineno > 0
            found.append(("before", name, args_dict))

        def after_method(package, filename, name, lineno):
            assert package == check.__package__
            assert filename == check.__file__
            assert lineno > 0
            found.append(("after", name))

        def method_return(package, filename, name, lineno, return_value):
            assert package == check.__package__
            assert filename == check.__file__
            assert lineno > 0
            found.append(("return", name, return_value))

        _rewrite_callbacks.before_method.register(before_method)
        _rewrite_callbacks.after_method.register(after_method)
        _rewrite_callbacks.method_return.register(method_return)

        check.some_method()
        check.SomeClass(1, 2)
        assert found == [
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
