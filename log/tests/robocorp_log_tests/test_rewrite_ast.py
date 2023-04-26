from robocorp_log_tests.test_rewrite_hook import ConfigForTest
from pathlib import Path

from io import StringIO
import pytest


def test_ast_utils():
    from robocorp.log import _ast_utils
    import ast

    node = ast.parse(
        """
in_project_roots = robolog._in_project_roots(sys._getframe(1).f_code.co_filename)

if in_project_roots:
    foo()

""",
        filename="<string>",
    )
    s = StringIO()
    _ast_utils.print_ast(node, stream=s)
    assert "Name" in s.getvalue()


def test_rewrite_ast_just_docstring(tmpdir):
    from robocorp.log._config import FilterKind
    from robocorp.log._rewrite_importhook import _rewrite

    config = ConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    '''
    just docstring
    '''

def _ignore_this():
    a = 10
    return a
    
def _ignore_this_too():
    a = 10
    yield a
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
    from robocorp.log._config import FilterKind
    from robocorp.log._rewrite_importhook import _rewrite

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
        assert "@caller_in_proj and @robo_lifecycle_hooks.before_method" in unparsed
        assert "@caller_in_proj and @robo_lifecycle_hooks.after_method" in unparsed
        assert "if @caller_in_proj:" in unparsed
        assert "@robo_lifecycle_hooks.method_except" in unparsed
        assert "after_assign" not in unparsed


@pytest.mark.parametrize("rewrite_assigns", [True, False])
def test_rewrite_simple_full(tmpdir, rewrite_assigns):
    from robocorp.log._config import FilterKind
    from robocorp.log._rewrite_importhook import _rewrite

    config = ConfigForTest(rewrite_assigns=rewrite_assigns)

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
        if not rewrite_assigns:
            assert "after_assign" not in unparsed
        else:
            assert unparsed.count("after_assign") == 1


def test_rewrite_iterators(tmpdir):
    from robocorp.log._config import FilterKind
    from robocorp.log._rewrite_importhook import _rewrite

    config = ConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    yield 2
    a = yield 3
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[-1]
    import ast

    if hasattr(ast, "unparse"):  # 3.9 onwards
        unparsed = ast.unparse(mod)
        assert unparsed.count("before_method('GENERATOR'") == 1
        assert unparsed.count("after_method('GENERATOR'") == 1
        assert unparsed.count("method_except('GENERATOR'") == 1
        assert unparsed.count("before_yield") == 2
        assert unparsed.count("after_yield") == 2
        assert unparsed.count("after_assign") == 1


def test_rewrite_yield_from(tmpdir):
    from robocorp.log._config import FilterKind
    from robocorp.log._rewrite_importhook import _rewrite

    config = ConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    x = yield from foo()
    yield from another()
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[-1]
    import ast

    if hasattr(ast, "unparse"):  # 3.9 onwards
        unparsed = ast.unparse(mod)
        assert unparsed.count("before_method('GENERATOR'") == 1
        assert unparsed.count("after_method('GENERATOR'") == 1
        assert unparsed.count("method_except('GENERATOR'") == 1
        assert unparsed.count("before_yield_from") == 2
        assert unparsed.count("after_yield_from") == 2
        assert unparsed.count("after_assign") == 1


def test_handle_iterators_on_log_project_call(tmpdir):
    # We have a problem here: if we're dealing with a generator function which
    # is from a library, we cannot do a before_method/after_method because
    # the stack will be unsynchronized, so, we have to do something as
    # library generator start/generator end (as we won't log things inside
    # it, this should be ok).
    from robocorp.log._config import FilterKind
    from robocorp.log._rewrite_importhook import _rewrite

    config = ConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    yield 2
    a = yield 3
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.log_on_project_call)[-1]
    import ast

    if hasattr(ast, "unparse"):  # 3.9 onwards
        unparsed = ast.unparse(mod)
        assert unparsed.count("before_method('UNTRACKED_GENERATOR'") == 1
        assert unparsed.count("method_except('UNTRACKED_GENERATOR'") == 1
        assert unparsed.count("after_method('UNTRACKED_GENERATOR'") == 1


def test_handle_yield_from_on_log_project_call(tmpdir):
    # We have a problem here: if we're dealing with a generator function which
    # is from a library, we cannot do a before_method/after_method because
    # the stack will be unsynchronized, so, we have to do something as
    # library generator start/generator end (as we won't log things inside
    # it, this should be ok).
    from robocorp.log._config import FilterKind
    from robocorp.log._rewrite_importhook import _rewrite

    config = ConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    yield from foo()
    a = yield from bar()
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.log_on_project_call)[-1]
    import ast

    if hasattr(ast, "unparse"):  # 3.9 onwards
        unparsed = ast.unparse(mod)
        assert unparsed.count("before_method('UNTRACKED_GENERATOR'") == 1
        assert unparsed.count("method_except('UNTRACKED_GENERATOR'") == 1
        assert unparsed.count("after_method('UNTRACKED_GENERATOR'") == 1
