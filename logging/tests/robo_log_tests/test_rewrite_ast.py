from robo_log_tests.test_rewrite_hook import ConfigForTest
from pathlib import Path

from io import StringIO


def test_ast_utils():
    from robo_log import _ast_utils
    import ast

    node = ast.parse(
        """
in_project_roots = robo_log._in_project_roots(sys._getframe(1).f_code.co_filename)

if in_project_roots:
    foo()

""",
        filename="<string>",
    )
    s = StringIO()
    _ast_utils.print_ast(node, stream=s)
    assert "Name" in s.getvalue()


def test_rewrite_ast_just_docstring(tmpdir):
    from robo_log._config import FilterKind
    from robo_log._rewrite_importhook import _rewrite

    config = ConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    '''
    just docstring
    '''
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[-1]
    import ast

    if hasattr(ast, "unparse"):  # 3.9 onwards
        unparsed = ast.unparse(mod)
        assert "before_method" not in unparsed
        assert "after_method" not in unparsed
        assert "method_except" not in unparsed


def test_rewrite_simple_on_project(tmpdir):
    from robo_log._config import FilterKind
    from robo_log._rewrite_importhook import _rewrite

    config = ConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    '''
    just docstring
    '''
    a = 1
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.log_on_project_call)[-1]
    import ast

    if hasattr(ast, "unparse"):  # 3.9 onwards
        unparsed = ast.unparse(mod)
        assert (
            "@caller_in_proj and @robocorp_rewrite_callbacks.before_method" in unparsed
        )
        assert (
            "@caller_in_proj and @robocorp_rewrite_callbacks.after_method" in unparsed
        )
        assert "if @caller_in_proj:" in unparsed
        assert "@robocorp_rewrite_callbacks.method_except" in unparsed
        assert "after_assign" not in unparsed


def test_rewrite_simple_full(tmpdir):
    from robo_log._config import FilterKind
    from robo_log._rewrite_importhook import _rewrite

    config = ConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    '''
    just docstring
    '''
    a = 1
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[-1]
    import ast

    if hasattr(ast, "unparse"):  # 3.9 onwards
        unparsed = ast.unparse(mod)
        assert "@caller_in_proj" not in unparsed
        assert "before_method" in unparsed
        assert "after_assign" in unparsed
