from io import StringIO
from pathlib import Path

import pytest
from robocorp_log_tests.test_rewrite_hook import AutoLogConfigForTest

from robocorp.log._config import FilterKind
from robocorp.log._rewrite_importhook import _rewrite


def test_ast_utils() -> None:
    import ast

    from robocorp.log import _ast_utils

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
    # ast_module.dump(node, include_attributes=False, indent=True)


def test_rewrite_ast_just_docstring(tmpdir, str_regression):
    config = AutoLogConfigForTest()

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

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
    assert "before_method" not in unparsed
    assert "after_method" not in unparsed
    assert "method_except" not in unparsed


def test_rewrite_simple_on_project(tmpdir, str_regression):
    config = AutoLogConfigForTest()

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

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
    assert "MethodLifecycleContextCallerInProject" in unparsed


def test_rewrite_return_full(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    return 1
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[-1]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
    assert "MethodLifecycleContext(" in unparsed


def test_rewrite_return_log_on_project_call(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    return 1
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.log_on_project_call)[-1]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
    assert "MethodLifecycleContextCallerInProject" in unparsed


def test_no_rewrite_return_on_untracked_generator(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    yield 1
    return 2
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.log_on_project_call)[-1]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
    assert "MethodLifecycleContextCallerInProject" in unparsed


@pytest.mark.parametrize("rewrite_assigns", [True, False])
def test_rewrite_simple_full(tmpdir, rewrite_assigns, str_regression):
    config = AutoLogConfigForTest(rewrite_assigns=rewrite_assigns)

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

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
    assert "MethodLifecycleContext(('METHOD'" in unparsed
    if not rewrite_assigns:
        assert "after_assign" not in unparsed
    else:
        assert unparsed.count("after_assign") == 1


def test_rewrite_yield(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def method():
    a = call() and (yield 3)
    yield 2
    x = yield call()
"""
    )

    mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[-1]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)


def test_rewrite_yield_from(tmpdir, str_regression):
    config = AutoLogConfigForTest()

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

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
    assert unparsed.count("MethodLifecycleContext(('GENERATOR'") == 1
    assert unparsed.count("before_yield_from") == 2
    assert unparsed.count("after_yield_from") == 2
    assert unparsed.count("after_assign") == 1


def test_handle_iterators_on_log_project_call(tmpdir, str_regression):
    # We have a problem here: if we're dealing with a generator function which
    # is from a library, we cannot do a before_method/after_method because
    # the stack will be unsynchronized, so, we have to do something as
    # library generator start/generator end (as we won't log things inside
    # it, this should be ok).

    config = AutoLogConfigForTest()

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

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
    assert (
        unparsed.count("MethodLifecycleContextCallerInProject(('UNTRACKED_GENERATOR'")
        == 1
    )


def test_handle_yield_from_on_log_project_call(tmpdir, str_regression):
    # We have a problem here: if we're dealing with a generator function which
    # is from a library, we cannot do a before_method/after_method because
    # the stack will be unsynchronized, so, we have to do something as
    # library generator start/generator end (as we won't log things inside
    # it, this should be ok).

    config = AutoLogConfigForTest()

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

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
    assert (
        unparsed.count("MethodLifecycleContextCallerInProject(('UNTRACKED_GENERATOR'")
        == 1
    )


def test_rewrite_yield_multiple(tmpdir, str_regression):
    from robocorp.log._lifecycle_hooks import after_yield, before_yield

    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def foo():
    for a in [b := (yield call()), c := (yield 33)]:
        pass
    return [b, c]
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)

    def call():
        return 1

    found = []

    def before(*args):
        found.append("before")

    def after(*args):
        found.append("after")

    with before_yield.register(before), after_yield.register(after):
        namespace = {"call": call}
        namespace["__file__"] = "<string>"
        exec(co, namespace)
        foo = namespace["foo"]()
        assert next(foo) == 1
        assert foo.send("step_a") == 33
        with pytest.raises(StopIteration) as e:
            foo.send("step_b")

        assert e.value.value == ["step_a", "step_b"]

    # We cannot stack 2 before nor 2 after, it must be always interleaved.

    assert found == ["before", "after", "before", "after"]


def test_rewrite_for(tmpdir, str_regression):
    from robocorp.log._lifecycle_hooks import after_iterate, before_iterate

    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def foo():
    for a in [1, 2]:
        call(a)
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)

    def call(v):
        return v

    found = []

    def before(*args):
        found.append("before iterate")

    def after(*args):
        found.append("after iterate")

    with before_iterate.register(before), after_iterate.register(after):
        namespace = {"call": call}
        namespace["__file__"] = "<string>"
        exec(co, namespace)
        namespace["foo"]()

    assert found == ["before iterate", "after iterate"]


def test_rewrite_for_continue(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def foo():
    for a in [1, 2]:
        if a == 1:
            continue
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)


def test_rewrite_while(tmpdir, str_regression):
    from robocorp.log._lifecycle_hooks import after_iterate, before_iterate

    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def foo():
    a = 1
    while a < 3:
        a += 1
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)

    found = []

    def before(*args):
        found.append("before iterate")

    def after(*args):
        found.append("after iterate")

    with before_iterate.register(before), after_iterate.register(after):
        namespace = {}
        namespace["__file__"] = "<string>"
        exec(co, namespace)
        namespace["foo"]()

    assert found == ["before iterate", "after iterate"]


def test_rewrite_while_no_call_in_target(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def foo():
    a = 1
    while call() < 3:
        a += 1
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)


def test_rewrite_await(tmpdir, str_regression):
    # On await it should just skip the function.

    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def a():
    async def something():
        for a in range(10):
            try:
                x = a
            except Exception:
                pass
        return 1
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)


def test_rewrite_if_with_generator(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def foo():
    a = 20
    if a > 10:
        yield 1
    elif b == 10:
        yield 2
    else:
        yield 3
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)


def test_rewrite_if(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def foo():
    for a in range(2):
        a = 20
        if a > 10:
            if a > 2:
                pass
        elif b == 10:
            pass
        elif d == 10:
            if True:
                pass
            else:
                pass
        else:
            pass
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)


def test_rewrite_assert_simple(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def call():
    return 1
    
def foo():
    a = 10
    assert a > 10
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)


def test_rewrite_assert(tmpdir, str_regression):
    config = AutoLogConfigForTest()

    target = Path(tmpdir)
    target /= "check.py"
    target.write_text(
        """
def call():
    return 1
    
def foo():
    a = 10
    assert a > 10
    assert a != 'some string'
    assert call1(1, 2) == call2(call3()), 'The calls do not match'
    assert call1(22) + call1(22) * call3()
    assert a.call1(call2()) + a.b.call2(call4()) * a.b.c.call3()
    assert a.b.c and f.g
"""
    )

    co, mod = _rewrite(target, config, filter_kind=FilterKind.full_log)[1:3]
    import ast

    unparsed = ast.unparse(mod)
    str_regression.check(unparsed)
