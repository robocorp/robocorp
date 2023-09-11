import ast
import typing
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from ._ast_utils import ASTRewriter
from ._config import AutoLogConfigBase, FilterKind
from .protocols import LogElementType

DEBUG = False


def is_rewrite_disabled(docstring: str) -> bool:
    return "NO_LOG" in docstring


FilterKindLiteral = Literal[1, 2, 3]
FILTER_KIND_FULL: FilterKindLiteral = 1
FILTER_KIND_PROJECT_CALL: FilterKindLiteral = 2
FILTER_KIND_EXCLUDE: FilterKindLiteral = 3


def _make_import_aliases_ast(lineno: int, filter_kind: FilterKindLiteral):
    aliases = [
        ast.alias(
            "robocorp.log._lifecycle_hooks",
            "@robo_lifecycle_hooks",
            lineno=lineno,
            col_offset=0,
        ),
    ]

    if filter_kind == FILTER_KIND_PROJECT_CALL:
        aliases.append(
            ast.alias("robocorp.log", "@robolog", lineno=lineno, col_offset=0)
        )

    imports = [ast.Import([alias], lineno=lineno, col_offset=0) for alias in aliases]
    return imports


def _make_lifecycle_func_with_args(factory, func_name: str, *args):
    call = factory.Call(factory.NameLoadRewriteCallback(func_name))
    call.args.extend(args)
    return call


def _make_ctx_func_with_args(factory, func_name: str, *args):
    call = factory.Call(factory.NameLoadCtx(func_name))
    call.args.extend(args)
    return call


def _make_after_yield_expr(
    factory, function, class_name: str, node_lineno: int
) -> ast.Expr:
    return factory.Expr(
        _make_ctx_func_with_args(
            factory,
            "after_yield",
            factory.NameLoad("__name__"),
            factory.NameLoad("__file__"),
            factory.Str(f"{class_name}{function.name}"),
            factory.LineConstantAt(node_lineno),
        )
    )


def _make_before_yield_from_exprs(
    factory, function, class_name, node_lineno
) -> ast.Expr:
    return factory.Expr(
        _make_ctx_func_with_args(
            factory,
            "before_yield_from",
            factory.NameLoad("__name__"),
            factory.NameLoad("__file__"),
            factory.Str(f"{class_name}{function.name}"),
            factory.LineConstantAt(node_lineno),
        )
    )


def _make_after_yield_from_expr(
    factory, function, class_name: str, node_lineno: int
) -> ast.Expr:
    return factory.Expr(
        _make_ctx_func_with_args(
            factory,
            "after_yield_from",
            factory.NameLoad("__name__"),
            factory.NameLoad("__file__"),
            factory.Str(f"{class_name}{function.name}"),
            factory.LineConstantAt(node_lineno),
        )
    )


_EMPTY_LIST: list = []


def _create_method_with_stmt(
    factory,
    class_name: str,
    function,
    filter_kind: FilterKindLiteral,
    log_method_type: LogElementType,
    function_body: List[ast.stmt],
) -> ast.With:
    # Target code:
    # def method(a, b):
    #     with MethodLifecycleContextCallerInProject(
    #         __name, __file__, "method_name", 11, {'a': a, 'b': b}) as ctx:
    #         ...
    if filter_kind == FILTER_KIND_PROJECT_CALL:
        name = "MethodLifecycleContextCallerInProject"
    else:
        name = "MethodLifecycleContext"

    call = factory.Call(factory.NameLoadRewriteCallback(name))

    tup_elts = [
        factory.Str(log_method_type),
        factory.NameLoad("__name__"),
        factory.NameLoad("__file__"),
        factory.Str(f"{class_name}{function.name}"),
        factory.LineConstantAt(function.lineno),
    ]

    dct = factory.Dict()
    keys: list[Union[ast.expr, None]] = []
    values: list[ast.expr] = []
    for arg in function.args.args:
        if class_name and arg.arg == "self":
            continue
        keys.append(factory.Str(arg.arg))
        values.append(factory.NameLoad(arg.arg))

    if function.args.vararg:
        keys.append(factory.Str(function.args.vararg.arg))
        values.append(factory.NameLoad(function.args.vararg.arg))

    if function.args.kwarg:
        keys.append(factory.Str(function.args.kwarg.arg))
        values.append(factory.NameLoad(function.args.kwarg.arg))
    dct.keys = keys
    dct.values = values
    tup_elts.append(dct)
    call.args.append(factory.Tuple(*tup_elts))

    with_stmt = factory.WithStmt(
        items=[
            factory.withitem(
                context_expr=call,
                optional_vars=factory.NameStore("@ctx"),
            )
        ],
        body=function_body,
    )
    return with_stmt


AcceptedCases = Literal[
    # Only when full logging is available for a function.
    "full_log",
    # Can be used on external libraries when the function is called from the user code.
    "log_on_project_call",
    # Can be used for generators being tracked (used for things which don't add
    # to the stack internally)
    # i.e.: for loop can't use it but an assign can.
    "generator",
    # Can be used even for generators which aren't internally tracked (usually just
    # the function itself).
    "untracked_generator",
]


def _accept_function_rewrite(
    function: ast.FunctionDef,
    rewrite_ctx,
    filter_kind: FilterKindLiteral,
    cases: Tuple[AcceptedCases, ...],
) -> bool:
    if function.name.startswith("_") and function.name != "__init__":
        return False

    if not function.body:
        return False

    if filter_kind == FILTER_KIND_FULL:
        if "full_log" not in cases:
            return False

    elif filter_kind == FILTER_KIND_PROJECT_CALL:
        if "log_on_project_call" not in cases:
            return False

    generator_in_cases: bool = "generator" in cases

    # rewrite_ctx.is_generator is slow, so, in the cases where we'd track
    # it anyways we can skip the check.
    if generator_in_cases:
        return True

    is_generator = rewrite_ctx.is_generator(function)

    if is_generator:
        if not generator_in_cases:
            return False

    return True


def _rewrite_funcdef(
    rewrite_ctx: ASTRewriter,
    function: ast.FunctionDef,
    filter_kind: FilterKindLiteral,
) -> None:
    parent: Any
    # Only rewrite functions which actually have some content.

    class_name = ""
    stack = rewrite_ctx.stack
    if stack:
        parent = stack[-1]
        if parent.__class__.__name__ == "ClassDef":
            class_name = parent.name + "."

    first_non_constant_stmt_index = 0
    stmt: ast.stmt
    for stmt in function.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            first_non_constant_stmt_index += 1
            continue
        break

    # Note: we need to compute this before we change the body!
    # Also, it's important that this is cached as new calls will use the
    # cached value (for is_generator) directly.
    log_method_type: LogElementType
    if rewrite_ctx.is_generator(function):
        if filter_kind == FILTER_KIND_PROJECT_CALL:
            log_method_type = "UNTRACKED_GENERATOR"
        else:
            log_method_type = "GENERATOR"
    else:
        log_method_type = "METHOD"

    function_body = function.body
    function.body = []  # Proper value will be set later.

    # Separate the docstring.
    if first_non_constant_stmt_index > 0:
        function_body_prefix = function_body[0:first_non_constant_stmt_index]
        function_body = function_body[first_non_constant_stmt_index:]
    else:
        function_body_prefix = _EMPTY_LIST

    if not function_body:
        # We had just the docstring, no real contents here
        # (so, just restore the docstring).
        function.body = function_body_prefix
        return

    factory = rewrite_ctx.NodeFactory(
        function_body[0].lineno, function_body[0].col_offset
    )

    with_stmt = _create_method_with_stmt(
        factory,
        class_name,
        function,
        filter_kind,
        log_method_type,
        function_body,
    )

    function.body = function_body_prefix + [with_stmt]


def rewrite_ast_add_callbacks(
    mod: ast.Module,
    original_filter_kind: FilterKind,
    source: bytes,
    module_path: str,
    config: AutoLogConfigBase,
) -> None:
    """Rewrite the module as needed so that the logging is done automatically."""

    if not mod.body:
        # Nothing to do.
        return

    # Convert to int for performance.
    kind: FilterKindLiteral
    if original_filter_kind == FilterKind.full_log:
        kind = FILTER_KIND_FULL
    elif original_filter_kind == FilterKind.log_on_project_call:
        kind = FILTER_KIND_PROJECT_CALL
    elif original_filter_kind == FilterKind.exclude:
        kind = FILTER_KIND_EXCLUDE
    else:
        raise ValueError(f"Unexpected filter kind: {original_filter_kind}.")

    # We'll insert some special imports at the top of the module, but after any
    # docstrings and __future__ imports, so first figure out where that is.
    doc = getattr(mod, "docstring", None)
    expect_docstring = doc is None
    if doc is not None and is_rewrite_disabled(doc):
        return
    pos = 0
    lineno = 1
    for item in mod.body:
        if (
            expect_docstring
            and isinstance(item, ast.Expr)
            and isinstance(item.value, ast.Str)
        ):
            doc = item.value.s
            if is_rewrite_disabled(doc):
                return
            expect_docstring = False
        elif (
            isinstance(item, ast.ImportFrom)
            and item.level == 0
            and item.module == "__future__"
        ):
            pass
        else:
            break
        pos += 1
    # Special case: for a decorated function, set the lineno to that of the
    # first decorator, not the `def`. Issue #4984.
    if isinstance(item, ast.FunctionDef) and item.decorator_list:
        lineno = item.decorator_list[0].lineno
    else:
        lineno = item.lineno
    # Now actually insert the special imports.
    imports = _make_import_aliases_ast(lineno, kind)
    mod.body[pos:pos] = imports

    dispatch_table = _DispatchTable()

    rewrite_ctx = ASTRewriter(mod, dispatch_table, config, module_path, kind)

    rewrite_ctx.iter_and_replace_nodes(mod)

    if DEBUG:
        print("\n============ New AST (with hooks in place) ==============\n")
        # Note: only python 3.9 onwards.
        print(ast.unparse(mod))  # type: ignore


def _handle_async_funcdef(
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node,
):
    yield rewrite_ctx.DONT_GO_INTO_NODE


def _handle_funcdef(
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node,
):
    try:
        function: ast.FunctionDef = node
        if not _accept_function_rewrite(
            function,
            rewrite_ctx,
            filter_kind,
            cases=(
                "full_log",
                "log_on_project_call",
                "generator",
            ),
        ):
            yield rewrite_ctx.DONT_GO_INTO_NODE
            return

        if filter_kind == FILTER_KIND_PROJECT_CALL and rewrite_ctx.is_generator(
            function
        ):
            # This is the case for 'untracked_generator'. In this situation,
            # we should not go inside the function (so, we just do the
            # function-level rewriting).
            _rewrite_funcdef(rewrite_ctx, node, filter_kind)
            yield rewrite_ctx.DONT_GO_INTO_NODE
            return

        yield
        _rewrite_funcdef(rewrite_ctx, node, filter_kind)

    except Exception:
        raise RuntimeError(
            f"Error when rewriting function: {node.name} line: {node.lineno} "
            f"at: {module_path}"
        )


def _handle_return(
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node,
):
    func_and_class_name = rewrite_ctx.get_function_and_class_name()
    if not func_and_class_name:
        return None

    function, class_name = func_and_class_name
    if not _accept_function_rewrite(
        function,
        rewrite_ctx,
        filter_kind,
        cases=("full_log", "log_on_project_call", "generator"),
    ):
        return

    try:
        factory = rewrite_ctx.NodeFactory(node.lineno, node.col_offset)

        result: List[ast.stmt] = []

        call = factory.Call(factory.NameLoadRewriteCallback("method_return"))
        call.args.append(factory.NameLoad("__name__"))
        call.args.append(factory.NameLoad("__file__"))
        call.args.append(factory.Str(f"{class_name}{function.name}"))
        call.args.append(factory.LineConstantAt(node.lineno))

        if node.value:
            assign = factory.Assign()
            store_name = factory.NameTempStore()
            assign.targets = [store_name]
            assign.value = node.value

            node.value = factory.NameLoad(store_name.id)

            result.append(assign)
            call.args.append(factory.NameLoad(store_name.id))
        else:
            call.args.append(factory.NoneConstant())

        if filter_kind == FILTER_KIND_PROJECT_CALL:
            result.append(
                factory.AndExpr(
                    factory.Attribute(factory.NameLoad("@ctx"), "_accept"), call
                )
            )
        else:
            result.append(factory.Expr(call))
        result.append(node)
        return result
    except Exception:
        raise RuntimeError(
            f"Error when rewriting function return: {function.name} line: {node.lineno}"
            f" at: {module_path}"
        )


def _handle_continue_break(
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node: Union[ast.Continue, ast.Break],
):
    func_and_class_name = rewrite_ctx.get_function_and_class_name()
    if not func_and_class_name:
        return None

    function, class_name = func_and_class_name
    if not _accept_function_rewrite(
        function,
        rewrite_ctx,
        filter_kind,
        cases=("full_log", "generator"),
    ):
        return

    try:
        kind = "continue" if isinstance(node, ast.Continue) else "break"
        factory = rewrite_ctx.NodeFactory(node.lineno, node.col_offset)
        call = factory.Call(factory.NameLoadCtx(f"report_{kind}"))
        call.args = [
            factory.Tuple(
                factory.NameLoad("__name__"),
                factory.NameLoad("__file__"),
                factory.Str(f"{class_name}{function.name}"),
                factory.LineConstantAt(node.lineno),
            )
        ]

        rewrite_ctx.stmts_cursor.before_append(factory.Expr(call))
    except Exception:
        raise RuntimeError(
            f"Error when rewriting node: {node.__class__.__name__} line: {node.lineno} "
            f"at: {module_path}"
        )


def _handle_if(
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node: ast.If,
):
    """
    When handling an if we have 2 options: writing it unscoped (so, we just
    notify that an if branch was taken, but we don't notify when it exits, which
    is meant for generators) or scoped (regular case without generators).
    """
    func_and_class_name = rewrite_ctx.get_function_and_class_name()
    if not func_and_class_name:
        yield
        return None

    function, _class_name = func_and_class_name
    if _accept_function_rewrite(
        function,
        rewrite_ctx,
        filter_kind,
        cases=("full_log",),
    ):
        yield from _handle_full_log_if(
            function, rewrite_ctx, config, module_path, filter_kind, node
        )

    elif _accept_function_rewrite(
        function,
        rewrite_ctx,
        filter_kind,
        cases=(
            "full_log",
            "generator",
        ),
    ):
        yield from _handle_generator_if(
            function, rewrite_ctx, config, module_path, filter_kind, node
        )

    else:
        yield
        return None


def _handle_full_log_if(
    function,
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node: ast.If,
):
    if_id = rewrite_ctx.next_context_id()
    has_else = node.orelse and not (
        len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If)
    )
    if has_else:
        else_id = rewrite_ctx.next_context_id()
    yield
    try:
        stmt_name = "if"
        parent_node = rewrite_ctx.stack[-1]
        iselif = False
        if isinstance(parent_node, ast.If):
            iselif = bool(
                parent_node.orelse
                and len(parent_node.orelse) == 1
                and parent_node.orelse[0] is node
            )
            if iselif:
                stmt_name = "elif"

        if node.body:
            factory = rewrite_ctx.NodeFactory(
                node.body[0].lineno, node.body[0].col_offset
            )
            # With an IF we want to generate something as:
            #
            # if x:
            #     @ctx.report_if_start(1,
            #        ("IF_SCOPE", __name__, "filename", "for a in range(2)", 2))
            #     @ctx.report_if_end(1)
            targets = _collect_names_used_as_node_or_none(factory, node.test)

            call = factory.Call(factory.NameLoadCtx(f"report_if_start"))
            call.args.append(factory.IntConstant(if_id))
            call.args.append(
                factory.Tuple(
                    factory.Str(f"IF_SCOPE"),
                    factory.NameLoad("__name__"),
                    factory.NameLoad("__file__"),
                    factory.Str(f"{stmt_name} {ast.unparse(node.test)}"),
                    factory.LineConstantAt(node.lineno),
                    targets,
                )
            )
            node.body.insert(0, factory.Expr(call))

            last_stmt = node.body[-1]
            factory_last = rewrite_ctx.NodeFactory(
                last_stmt.lineno, last_stmt.col_offset
            )
            call = factory_last.Call(factory_last.NameLoadCtx(f"report_if_end"))
            call.args.append(factory_last.IntConstant(if_id))
            node.body.append(factory_last.Expr(call))

        if has_else:
            factory = rewrite_ctx.NodeFactory(
                node.orelse[0].lineno, node.orelse[0].col_offset
            )

            targets = _collect_names_used_as_node_or_none(factory, node.test)

            call = factory.Call(factory.NameLoadCtx(f"report_else_start"))
            call.args.append(factory.IntConstant(else_id))
            call.args.append(
                factory.Tuple(
                    factory.Str(f"ELSE_SCOPE"),
                    factory.NameLoad("__name__"),
                    factory.NameLoad("__file__"),
                    factory.Str(f"else (to if {ast.unparse(node.test)})"),
                    factory.LineConstantAt(node.lineno),
                    targets,
                )
            )
            node.orelse.insert(0, factory.Expr(call))

            last_stmt = node.orelse[-1]
            factory_last = rewrite_ctx.NodeFactory(
                last_stmt.lineno, last_stmt.col_offset
            )
            call = factory_last.Call(factory_last.NameLoadCtx(f"report_else_end"))
            call.args.append(factory_last.IntConstant(else_id))
            node.orelse.append(factory_last.Expr(call))

    except Exception:
        raise RuntimeError(
            f"Error when rewriting function (full) if statement in: {function.name} line: {node.lineno}"
            f" at: {module_path}"
        )


def _handle_generator_if(
    function,
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node: ast.If,
):
    yield
    try:
        stmt_name = "if"
        parent_node = rewrite_ctx.stack[-1]
        iselif = False
        if isinstance(parent_node, ast.If):
            iselif = bool(
                parent_node.orelse
                and len(parent_node.orelse) == 1
                and parent_node.orelse[0] is node
            )
            if iselif:
                stmt_name = "elif"

        if node.body:
            factory = rewrite_ctx.NodeFactory(
                node.body[0].lineno, node.body[0].col_offset
            )
            call = factory.Call(factory.NameLoadRewriteCallback("method_if"))
            call.args.append(factory.NameLoad("__name__"))
            call.args.append(factory.NameLoad("__file__"))
            call.args.append(factory.Str(f"{stmt_name} {ast.unparse(node.test)}"))
            call.args.append(factory.LineConstantAt(node.lineno))

            targets = _collect_names_used_as_node_or_none(factory, node.test)
            call.args.append(targets)
            node.body.insert(0, factory.Expr(call))

        if node.orelse and not (
            len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If)
        ):
            factory = rewrite_ctx.NodeFactory(
                node.orelse[0].lineno, node.orelse[0].col_offset
            )
            call = factory.Call(factory.NameLoadRewriteCallback("method_else"))
            call.args.append(factory.NameLoad("__name__"))
            call.args.append(factory.NameLoad("__file__"))
            call.args.append(factory.Str(f"else (to if {ast.unparse(node.test)})"))
            call.args.append(factory.LineConstantAt(node.orelse[0].lineno))
            targets = _collect_names_used_as_node_or_none(factory, node.test)
            call.args.append(targets)
            node.orelse.insert(0, factory.Expr(call))

    except Exception:
        raise RuntimeError(
            f"Error when rewriting function if statement in: {function.name} line: {node.lineno}"
            f" at: {module_path}"
        )


def _handle_before_assert(
    rewrite_ctx: ASTRewriter,
    config: AutoLogConfigBase,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node: ast.Assert,
):
    if filter_kind != FILTER_KIND_FULL:
        yield
        return None

    func_and_class_name = rewrite_ctx.get_function_and_class_name()
    if not func_and_class_name:
        yield
        return None

    function, _class_name = func_and_class_name

    dispatch_table: _DispatchTable = typing.cast(
        _DispatchTable, rewrite_ctx.dispatch_data
    )
    with dispatch_table.record_name_context():
        unparsed = ast.unparse(node.test)
        with dispatch_table.assert_context():
            yield

        try:
            factory = rewrite_ctx.NodeFactory(node.lineno, node.col_offset)

            # If(
            # test=UnaryOp(
            #  op=Not(),
            #  operand=Constant(value=1)),
            #    body=[
            #     Raise(
            #      exc=Call(
            #       func=Name(id='AssertionError', ctx=Load()),
            #       args=[
            #        Name(id='message', ctx=Load())],
            #       keywords=[]))],
            #    orelse=[])],

            func = factory.NameLoad("AssertionError")
            exc = factory.Call(func)
            raise_stmt = factory.Raise()
            raise_stmt.exc = exc

            call = factory.Call(factory.NameLoadRewriteCallback("assert_failed"))
            call.args.append(factory.NameLoad("__name__"))
            call.args.append(factory.NameLoad("__file__"))
            call.args.append(factory.Str(unparsed))
            call.args.append(factory.LineConstantAt(node.lineno))

            new_if_node: ast.If = factory.If(factory.NotUnaryOp(node.test))
            targets = _collect_names_used_as_node_or_none(
                factory, node.test, dispatch_table.recorded_name_to_new_name
            )
            call.args.append(targets)

            if node.msg:
                factory_msg = rewrite_ctx.NodeFactory(
                    node.msg.lineno, node.msg.col_offset
                )
                joined_str = factory_msg.JoinedStr()
                joined_str.values = [node.msg, factory_msg.Constant("\n")]
                exc.args.append(joined_str)
            else:
                factory_msg = rewrite_ctx.NodeFactory(node.lineno, node.col_offset)
                joined_str = factory_msg.JoinedStr()
                joined_str.values = []
                exc.args.append(joined_str)

            joined_str.values.append(factory.Constant(f"Failed: assert {unparsed}\n"))
            if isinstance(targets, ast.Tuple) and targets.elts:
                joined_str.values.append(factory.Constant(f"Variables:"))
                for tup in targets.elts:
                    if isinstance(tup, ast.Tuple):
                        name = typing.cast(ast.Constant, tup.elts[0]).value
                        name_load = typing.cast(ast.Name, tup.elts[1]).id
                        joined_str.values.append(factory_msg.Constant(f"\n  {name} = "))
                        v = factory_msg.FormattedValue(factory_msg.NameLoad(name_load))
                        v.conversion = 114
                        joined_str.values.append(v)

            new_if_node.body = [factory.Expr(call), raise_stmt]
            new_if_node.orelse = []
            rewrite_ctx.cursor.current = new_if_node

        except Exception:
            raise RuntimeError(
                f"Error when rewriting assert: {function.name} line: {node.lineno} "
                f"at: {module_path}"
            )


def _handle_assign(
    rewrite_ctx: ASTRewriter,
    config: AutoLogConfigBase,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node,
):
    if filter_kind != FILTER_KIND_FULL or not config.get_rewrite_assigns():
        return None

    func_and_class_name = rewrite_ctx.get_function_and_class_name()
    if not func_and_class_name:
        return None

    function, class_name = func_and_class_name
    if not _accept_function_rewrite(
        function,
        rewrite_ctx,
        filter_kind,
        cases=("full_log", "generator"),
    ):
        return

    try:
        factory = rewrite_ctx.NodeFactory(node.lineno, node.col_offset)
        for target in node.targets:
            if isinstance(target, ast.Name):
                call = _make_lifecycle_func_with_args(
                    factory,
                    "after_assign",
                    factory.NameLoad("__name__"),
                    factory.NameLoad("__file__"),
                    factory.Str(f"{class_name}{function.name}"),
                    factory.LineConstantAt(node.lineno),
                    factory.Str(target.id),
                    factory.NameLoad(target.id),
                )

                rewrite_ctx.stmts_cursor.after_append(factory.Expr(call))
    except Exception:
        raise RuntimeError(
            f"Error when rewriting assign: {function.name} line: {node.lineno} "
            f"at: {module_path}"
        )


def _filter_calls(node):
    # We can't go into calls or list comprehensions as we could end up loading
    # names which are just being created.
    return isinstance(
        node,
        (
            ast.Name,
            ast.Tuple,
            ast.List,
            ast.Dict,
            ast.BinOp,
            ast.BoolOp,
            ast.Compare,
            ast.Set,
            ast.operator,
            ast.boolop,
            ast.cmpop,
        ),
    )


def _collect_names(target: ast.AST):
    from robocorp.log import _ast_utils

    if isinstance(target, ast.Name):
        yield target

    for node in _ast_utils.iter_nodes_to_collect_names(target):
        if isinstance(node, ast.Name):
            yield node


def _accept_generator_full_log(
    rewrite_ctx: ASTRewriter, filter_kind: FilterKindLiteral
) -> Optional[Tuple[ast.FunctionDef, str]]:
    """
    If it's accepted returns the function and class name, otherwise
    returns None.
    """
    func_and_class_name = rewrite_ctx.get_function_and_class_name()
    if not func_and_class_name:
        return None

    function, class_name = func_and_class_name
    if not _accept_function_rewrite(
        function,
        rewrite_ctx,
        filter_kind,
        cases=("full_log", "generator"),
    ):
        return None

    return function, class_name


def _handle_before_try(
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node: ast.Try,
):
    func_and_class_name = _accept_generator_full_log(rewrite_ctx, filter_kind)
    if not func_and_class_name:
        yield
        return

    function, _class_name = func_and_class_name

    try:
        with rewrite_ctx.record_context_ids() as ids:
            yield

        if ids:
            if node.handlers:
                handler: ast.ExceptHandler
                for handler in node.handlers:
                    factory = rewrite_ctx.NodeFactory(
                        handler.body[0].lineno, handler.body[0].col_offset
                    )

                    call = factory.Call(factory.NameLoadCtx("report_exception"))
                    node_ids = [factory.IntConstant(ctx_id) for ctx_id in ids]
                    call.args.append(factory.Tuple(*node_ids))
                    handler.body.insert(0, factory.Expr(call))
    except Exception:
        raise RuntimeError(
            f"Error when rewriting try: {function.name} line: {node.lineno} at:"
            f" {module_path}"
        )


def _handle_for_or_while(
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node: Union[ast.For, ast.While],
):
    func_and_class_name = rewrite_ctx.get_function_and_class_name()
    if not func_and_class_name:
        yield
        return None

    function, _class_name = func_and_class_name
    if not _accept_function_rewrite(
        function,
        rewrite_ctx,
        filter_kind,
        cases=("full_log",),
    ):
        yield
        return None

    if rewrite_ctx.is_generator(function):
        # On generators we can't really track things inside the function because
        # pausing and unpausing of generators would need to recreate the whole context
        # up to the inner statement (i.e.: it'd need to pop/push the for which we
        # can't really do right now).
        yield
        return None

    for_id = rewrite_ctx.next_context_id()
    for_step_id = rewrite_ctx.next_context_id()

    yield

    try:
        # Wrapping of before/after for 'for' statements and each step of its body.
        factory = rewrite_ctx.NodeFactory(node.lineno, node.col_offset)
        stmts_cursor = rewrite_ctx.stmts_cursor

        stmt_name: str
        if isinstance(node, ast.For):
            iter_desc = ast.unparse(node.iter)
            collect_names_from_node = node.target
            target_desc = ast.unparse(node.target)
            name_str = factory.Str(f"for {target_desc} in {iter_desc}")
            step_name_str = factory.Str(f"Step: for {target_desc} in {iter_desc}")
            stmt_name = "for"

        elif isinstance(node, ast.While):
            while_desc = ast.unparse(node.test)
            collect_names_from_node = node.test
            name_str = factory.Str(f"while {while_desc}")
            step_name_str = factory.Str(f"Step: while {while_desc}")
            stmt_name = "while"
        else:
            raise RuntimeError(f"Unexpected node: {node}.")

        stmt_name_upper = stmt_name.upper()

        # With a FOR we want to generate something as:
        #
        # @ctx.report_for_start(1,
        #    ("FOR", __name__, "filename", "for a in range(2)", 2))
        # for a in b:
        #     @ctx.report_for_step_start(2, ("FOR_STEP", __name__, "filename",
        #         "for a in range(2)", 2), [('a', a)])
        #     print(a)
        #     @ctx.report_for_step_end(2)
        #
        # @ctx.report_for_end(1)

        # With a WHILE we want to generate something as:
        #
        # @ctx.report_while_start(1, ("WHILE", __name__, "filename", "while a < 1", 2))
        # while a < 1:
        #     @ctx.report_while_step_start(2, ("WHILE_STEP", __name__, "filename",
        #         "while a < 1", 2), [('a', a)])
        #     print(a)
        #     @ctx.report_while_step_end(2)
        #
        # @ctx.report_while_end(1)

        call = factory.Call(factory.NameLoadCtx(f"report_{stmt_name}_start"))
        call.args.append(factory.IntConstant(for_id))
        call.args.append(
            factory.Tuple(
                factory.Str(stmt_name_upper),  # FOR/WHILE
                factory.NameLoad("__name__"),
                factory.NameLoad("__file__"),
                name_str,
                factory.LineConstantAt(node.lineno),
            )
        )
        stmts_cursor.before_append(factory.Expr(call))

        call = factory.Call(factory.NameLoadCtx(f"report_{stmt_name}_end"))
        call.args.append(factory.IntConstant(for_id))
        stmts_cursor.after_append(factory.Expr(call))

        body = node.body
        if body:
            targets = _collect_names_used_as_node_or_none(
                factory, collect_names_from_node
            )

            call = factory.Call(factory.NameLoadCtx(f"report_{stmt_name}_step_start"))
            call.args.append(factory.IntConstant(for_step_id))
            call.args.append(
                factory.Tuple(
                    factory.Str(f"{stmt_name_upper}_STEP"),  # FOR_STEP / WHILE_STEP
                    factory.NameLoad("__name__"),
                    factory.NameLoad("__file__"),
                    step_name_str,
                    factory.LineConstantAt(node.lineno),
                    targets,
                )
            )
            body.insert(0, factory.Expr(call))

            last_stmt = body[-1]
            factory_last = rewrite_ctx.NodeFactory(
                last_stmt.lineno, last_stmt.col_offset
            )
            call = factory_last.Call(
                factory_last.NameLoadCtx(f"report_{stmt_name}_step_end")
            )
            call.args.append(factory_last.IntConstant(for_step_id))
            body.append(factory_last.Expr(call))

    except Exception:
        raise RuntimeError(
            f"Error when rewriting for: {function.name} line: {node.lineno} "
            f"at: {module_path}"
        )


def _collect_names_used_as_node_or_none(
    factory, collect_names_from_node, replacement_dict=None
) -> Union[ast.Constant, ast.Tuple]:
    """
    i.e.:
    In something as:

    for a,b in iter_in():
        ...

    We should collect a node as (('a', a), ('b', b),)

    In something as:

    if a > 10:
        ...

    We should collect a node as (('a', a),)

    If no names are available it should return a `None` node.
    """
    replacement_dict = replacement_dict or {}

    target_load: Union[ast.Name, ast.Constant]
    targets: Union[ast.Constant, ast.Tuple]
    temp_targets = []
    found = set()
    for name_target in _collect_names(collect_names_from_node):
        target_name = name_target.id
        if target_name in found:
            continue
        found.add(target_name)
        target_load = factory.NameLoad(name_target.id)
        temp_targets.append(
            factory.Tuple(
                factory.Str(replacement_dict.get(target_name, target_name)),
                target_load,
            )
        )

    if not temp_targets:
        targets = factory.NoneConstant()
    else:
        targets = factory.Tuple(*temp_targets)

    return targets


def _handle_yield(
    rewrite_ctx: ASTRewriter,
    config,
    module_path: str,
    filter_kind: FilterKindLiteral,
    node: Union[ast.Yield, ast.YieldFrom],
):
    func_and_class_name = rewrite_ctx.get_function_and_class_name()
    if not func_and_class_name:
        return None

    function, class_name = func_and_class_name
    if not _accept_function_rewrite(
        function, rewrite_ctx, filter_kind, cases=("full_log", "generator")
    ):
        return None

    try:
        # Wrapping of before/after for yield statements.
        factory = rewrite_ctx.NodeFactory(node.lineno, node.col_offset)
        stmts_cursor = rewrite_ctx.stmts_cursor
        yield_cursor = rewrite_ctx.cursor

        if isinstance(node, ast.Yield):
            value_yielded: ast.AST
            if isinstance(yield_cursor.parent, ast.stmt):
                # We can only rewrite in the simple case where we have something
                # as:
                # yield 2
                #
                # or
                #
                # a = yield call()
                #
                # Because we can't risk rewriting something as:
                #
                # a = call1() and (yield call2())
                #
                # as it'd change the order of the calls
                #
                # If the assumption above is correct then we can do something as:
                #
                # @tmp = call()
                # before_yield(..., @tmp)
                # yield @tmp
                #
                # and properly report the yield value, otherwise we need to do
                # further analysis to know whether it's ok to rewrite it.

                if node.value is not None:
                    assign = factory.Assign()
                    store_name = factory.NameTempStore()
                    assign.targets = [store_name]
                    assign.value = node.value

                    node.value = factory.NameLoad(store_name.id)

                    value_yielded = factory.NameLoad(store_name.id)
                    stmts_cursor.before_append(assign)
                else:
                    value_yielded = factory.NoneConstant()

                stmts_cursor.before_append(
                    factory.Expr(
                        _make_ctx_func_with_args(
                            factory,
                            "before_yield",
                            factory.NameLoad("__name__"),
                            factory.NameLoad("__file__"),
                            factory.Str(f"{class_name}{function.name}"),
                            factory.LineConstantAt(node.lineno),
                            value_yielded,
                        )
                    )
                )

                stmts_cursor.after_prepend(
                    _make_after_yield_expr(factory, function, class_name, node.lineno)
                )
            else:
                # This is a case which is more complex. We do it in a way
                # where we create a function and then yield from that function.
                #
                # Something as:
                #
                # yield f()
                #
                # becomes:
                #
                # def @tmp_0():
                #     @tmp_1 = f()
                #     before(...)
                #     @tmp_2 = yield from @tmp_1
                #     after(...)
                #     return @tmp_2
                #
                # yield from @tmp_0()
                #
                temp_funcdef = factory.FunctionDefTemp()

                if node.value is not None:
                    store_name = factory.NameTempStore()
                    assign = factory.Assign(targets=[store_name], value=node.value)

                    value_yielded = factory.NameLoad(store_name.id)
                    temp_funcdef.body.append(assign)
                else:
                    value_yielded = factory.NoneConstant()

                temp_funcdef.body.append(
                    factory.Expr(
                        _make_ctx_func_with_args(
                            factory,
                            "before_yield",
                            factory.NameLoad("__name__"),
                            factory.NameLoad("__file__"),
                            factory.Str(f"{class_name}{function.name}"),
                            factory.LineConstantAt(node.lineno),
                            value_yielded,
                        )
                    )
                )

                store_name = factory.NameTempStore()
                assign = factory.Assign(
                    targets=[store_name], value=factory.Yield(value_yielded)
                )

                temp_funcdef.body.append(assign)
                temp_funcdef.body.append(
                    _make_after_yield_expr(factory, function, class_name, node.lineno)
                )
                temp_funcdef.body.append(
                    factory.Return(factory.NameLoad(store_name.id))
                )

                stmts_cursor.before_append(temp_funcdef)

                yield_cursor.current = factory.YieldFrom(
                    factory.Call(factory.NameLoad(temp_funcdef.name))
                )

        else:
            stmts_cursor.before_append(
                _make_before_yield_from_exprs(
                    factory, function, class_name, node.lineno
                )
            )
            stmts_cursor.after_prepend(
                _make_after_yield_from_expr(factory, function, class_name, node.lineno)
            )
    except Exception:
        raise RuntimeError(
            f"Error when rewriting yield: {function.name} line: {node.lineno} "
            f"at: {module_path}"
        )


class _DispatchTable:
    def __init__(self) -> None:
        _dispatch_before: Dict[
            type,
            Callable[
                [ASTRewriter, AutoLogConfigBase, str, FilterKindLiteral, Any],
                Optional[list],
            ],
        ] = {}

        _dispatch_after: Dict[
            type,
            Callable[
                [ASTRewriter, AutoLogConfigBase, str, FilterKindLiteral, Any],
                Optional[list],
            ],
        ] = {}

        ### STATEMENTS
        _dispatch_after[ast.Return] = _handle_return
        _dispatch_after[ast.Assign] = _handle_assign
        _dispatch_after[ast.Continue] = _handle_continue_break
        _dispatch_after[ast.Break] = _handle_continue_break

        # We have to gather the ids for the contexts in order (so, do it
        # in before / after generator).
        _dispatch_before[ast.FunctionDef] = _handle_funcdef
        _dispatch_before[ast.AsyncFunctionDef] = _handle_async_funcdef
        _dispatch_before[ast.For] = _handle_for_or_while
        _dispatch_before[ast.While] = _handle_for_or_while
        _dispatch_before[ast.If] = _handle_if

        # Note: returns generator which is called when it finishes (right before
        # _dispatch_after)
        _dispatch_before[ast.Assert] = _handle_before_assert

        # Note: returns generator which is called when it finishes (right before
        # _dispatch_after)
        _dispatch_before[ast.Try] = _handle_before_try

        ### EXPRESSIONS
        _dispatch_after[ast.Yield] = _handle_yield
        _dispatch_after[ast.YieldFrom] = _handle_yield

        self.dispatch_before = _dispatch_before
        self.dispatch_after = _dispatch_after

        self.recorded_name_to_new_name: Dict[str, str] = {}

    def _handle_assert_compare(
        self,
        rewrite_ctx: ASTRewriter,
        config,
        module_path: str,
        filter_kind: FilterKindLiteral,
        node: ast.Compare,
    ):
        c = node.left
        if not isinstance(c, (ast.Constant, ast.Name)):
            # No point in making assigns to constants (as those appear directly)
            # nor names (as the name can be gotten directly from the scope and
            # shouldn't change).
            # Attributes may change on each access (i.e.: properties), so
            # for attributes the temporary alias would be needed.
            factory = rewrite_ctx.NodeFactory(c.lineno, c.col_offset)
            assign = factory.Assign()
            store_name = factory.NameTempStore()
            assign.targets = [store_name]
            assign.value = c
            rewrite_ctx.stmts_cursor.before_append(assign)
            node.left = factory.NameLoad(store_name.id)
            self.recorded_name_to_new_name[store_name.id] = ast.unparse(c)

        for i, c in enumerate(node.comparators):
            if not isinstance(c, (ast.Constant, ast.Name)):
                factory = rewrite_ctx.NodeFactory(c.lineno, c.col_offset)
                assign = factory.Assign()
                store_name = factory.NameTempStore()
                assign.targets = [store_name]
                assign.value = c
                rewrite_ctx.stmts_cursor.before_append(assign)
                node.comparators[i] = factory.NameLoad(store_name.id)
                self.recorded_name_to_new_name[store_name.id] = ast.unparse(c)
        yield rewrite_ctx.DONT_GO_INTO_NODE

    def _handle_assert_call(
        self,
        rewrite_ctx: ASTRewriter,
        config,
        module_path: str,
        filter_kind: FilterKindLiteral,
        node: ast.Call,
    ):
        factory = rewrite_ctx.NodeFactory(node.func.lineno, node.func.col_offset)
        assign = factory.Assign()
        store_name = factory.NameTempStore()
        assign.targets = [store_name]
        assign.value = node
        rewrite_ctx.stmts_cursor.before_append(assign)
        if node.args:
            call_rep = "(...)"
        else:
            call_rep = "()"
        self.recorded_name_to_new_name[
            store_name.id
        ] = f"{ast.unparse(node.func)}{call_rep}"
        rewrite_ctx.cursor.current = factory.NameLoad(store_name.id)
        yield rewrite_ctx.DONT_GO_INTO_NODE

    def _handle_assert_attribute(
        self,
        rewrite_ctx: ASTRewriter,
        config,
        module_path: str,
        filter_kind: FilterKindLiteral,
        node: ast.Attribute,
    ):
        factory = rewrite_ctx.NodeFactory(node.lineno, node.col_offset)
        assign = factory.Assign()
        store_name = factory.NameTempStore()
        assign.targets = [store_name]
        assign.value = node
        rewrite_ctx.stmts_cursor.before_append(assign)
        self.recorded_name_to_new_name[store_name.id] = ast.unparse(node)
        rewrite_ctx.cursor.current = factory.NameLoad(store_name.id)
        yield rewrite_ctx.DONT_GO_INTO_NODE

    @contextmanager
    def replace_before(self, tp, callback):
        assert tp not in self.dispatch_before
        self.dispatch_before[tp] = callback
        try:
            yield
        finally:
            del self.dispatch_before[tp]

    @contextmanager
    def record_name_context(self):
        self.recorded_name_to_new_name = {}
        try:
            yield
        finally:
            self.recorded_name_to_new_name = {}

    @contextmanager
    def assert_context(self):
        """
        In the assert context we change some of the expressions inside the assert
        so that we can report on them to the user.

        i.e.:

        Something as:

        assert my.path == 'foo'

        should become something as:

        @temp_name = my.path
        if not @temp_name == 'foo':
            report_assert_failed(..., [('my.path', @temp_name)])
        """
        with self.replace_before(
            ast.Compare, self._handle_assert_compare
        ), self.replace_before(ast.Call, self._handle_assert_call), self.replace_before(
            ast.Attribute, self._handle_assert_attribute
        ):
            yield
