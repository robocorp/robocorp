import ast
from typing import Any, Union, List, Optional, Tuple, Dict, Callable, Sequence, Iterator
import typing
from . import _ast_utils
from ._config import BaseConfig, FilterKind
from .protocols import LogElementType

DEBUG = False


def is_rewrite_disabled(docstring: str) -> bool:
    return "NO_LOG" in docstring


class _RewriteCtx:
    def __init__(self):
        self._memo = {}

    def save_func_to_before_method_call(
        self, function: ast.FunctionDef, call: ast.Call
    ):
        self._memo.setdefault(function, []).append(call)

    def save_func_to_except_method_call(self, function, call):
        self._memo.setdefault(function, []).append(call)

    def save_func_to_after_method_call(self, function, call):
        self._memo.setdefault(function, []).append(call)

    def iter_func_calls_from_func(self, func: ast.FunctionDef) -> Iterator[ast.Call]:
        yield from iter(self._memo[func])


def _make_import_aliases_ast(lineno, filter_kind: FilterKind):
    aliases = [
        ast.alias(
            "robocorp.log._lifecycle_hooks",
            "@robo_lifecycle_hooks",
            lineno=lineno,
            col_offset=0,
        ),
    ]

    if filter_kind == FilterKind.log_on_project_call:
        aliases.append(
            ast.alias("robocorp.log", "@robolog", lineno=lineno, col_offset=0)
        )

    imports = [ast.Import([alias], lineno=lineno, col_offset=0) for alias in aliases]
    return imports


def _get_function_and_class_name(stack) -> Optional[Tuple[Any, str]]:
    if not stack:
        return None
    stack_it = reversed(stack)
    for function in stack_it:
        if function.__class__.__name__ != "FunctionDef":
            continue
        break
    else:
        return None

    class_name = ""
    try:
        parent = next(stack_it)
        if parent.__class__.__name__ == "ClassDef":
            class_name = parent.name + "."
    except StopIteration:
        pass

    return function, class_name


def _rewrite_return(function, class_name, node: ast.Return) -> Optional[list]:
    if function.name.startswith("_"):
        return None

    factory = _ast_utils.NodeFactory(node.lineno, node.col_offset)

    result: List[ast.stmt] = []

    call = factory.Call()
    call.func = factory.NameLoadRewriteCallback("method_return")
    call.args.append(factory.NameLoad("__name__"))
    call.args.append(factory.NameLoad("__file__"))
    call.args.append(factory.Str(f"{class_name}{function.name}"))
    call.args.append(factory.LineConstant())

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

    result.append(factory.Expr(call))
    result.append(node)
    return result


def _rewrite_assign(function, class_name, node: ast.Assign) -> Optional[list]:
    factory = _ast_utils.NodeFactory(node.lineno, node.col_offset)

    result: List[ast.stmt] = []

    if isinstance(node.value, ast.Yield):
        result.extend(_make_before_yield_exprs(factory, function, class_name, node))

    result.append(node)

    if isinstance(node.value, ast.Yield):
        result.append(_make_after_yield_expr(factory, function, class_name))

    for target in node.targets:
        if isinstance(target, ast.Name):
            call = _make_func_with_args(
                factory,
                "after_assign",
                factory.NameLoad("__name__"),
                factory.NameLoad("__file__"),
                factory.Str(f"{class_name}{function.name}"),
                factory.LineConstant(),
                factory.Str(target.id),
                factory.NameLoad(target.id),
            )

            result.append(factory.Expr(call))

    return result


def _make_func_with_args(factory, func_name, *args):
    call = factory.Call()
    call.func = factory.NameLoadRewriteCallback(func_name)
    call.args.extend(args)
    return call


class INodeWithValueExpr(typing.Protocol):
    value: ast.expr


def _make_before_yield_exprs(
    factory, function, class_name, node_with_yield_val: INodeWithValueExpr
) -> Sequence[ast.Expr]:
    assert isinstance(node_with_yield_val.value, ast.Yield)
    yield_expr: ast.Yield = node_with_yield_val.value

    result = []
    if yield_expr.value is not None:
        assign = factory.Assign()
        store_name = factory.NameTempStore()
        assign.targets = [store_name]
        assign.value = yield_expr.value

        yield_expr.value = factory.NameLoad(store_name.id)

        value_yielded = factory.NameLoad(store_name.id)
        result.append(assign)
    else:
        value_yielded = factory.NoneConstant()

    result.append(
        factory.Expr(
            _make_func_with_args(
                factory,
                "before_yield",
                factory.NameLoad("__name__"),
                factory.NameLoad("__file__"),
                factory.Str(f"{class_name}{function.name}"),
                factory.LineConstant(),
                value_yielded,
            )
        )
    )
    return result


def _make_after_yield_expr(factory, function, class_name):
    return factory.Expr(
        _make_func_with_args(
            factory,
            "after_yield",
            factory.NameLoad("__name__"),
            factory.NameLoad("__file__"),
            factory.Str(f"{class_name}{function.name}"),
            factory.LineConstant(),
        )
    )


def _rewrite_yield(function, class_name, node: ast.Expr) -> Optional[list]:
    factory = _ast_utils.NodeFactory(node.lineno, node.col_offset)

    result: List[ast.stmt] = []
    result.extend(_make_before_yield_exprs(factory, function, class_name, node))
    result.append(node)
    result.append(_make_after_yield_expr(factory, function, class_name))
    return result


_EMPTY_LIST: list = []


def _create_before_method_ast(
    rewrite_ctx: _RewriteCtx, factory, class_name, function, filter_kind
) -> list:
    # Target code:
    # def method(a, b):
    #     before_method(__name, __file__, "method_name", 11, {'a': a, 'b': b})
    stmts: list = []

    if filter_kind == FilterKind.log_on_project_call:
        # In this case we need to create a local variable signaling whether
        # the caller is in the project (as if it's not we won't log the calls).
        call = factory.Call()
        call.func = factory.NameLoadRobo("_caller_in_project_roots")

        assign = factory.Assign()
        caller_in_proj_name = factory.NameStore("@caller_in_proj")
        assign.targets = [caller_in_proj_name]
        assign.value = call
        stmts.append(assign)

    call = factory.Call()
    call.func = factory.NameLoadRewriteCallback("before_method")
    log_method_type: LogElementType = "METHOD"
    call.args.append(factory.Str(log_method_type))
    call.args.append(factory.NameLoad("__name__"))
    call.args.append(factory.NameLoad("__file__"))
    call.args.append(factory.Str(f"{class_name}{function.name}"))
    call.args.append(factory.LineConstant())

    rewrite_ctx.save_func_to_before_method_call(function, call)

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
    call.args.append(dct)

    if filter_kind == FilterKind.log_on_project_call:
        stmts.append(factory.AndExpr(factory.NameLoad("@caller_in_proj"), call))
    else:
        stmts.append(factory.Expr(call))
    return stmts


def _create_except_handler_ast(
    rewrite_ctx: _RewriteCtx,
    factory,
    class_name: str,
    function: ast.FunctionDef,
    last_body_lineno,
    filter_kind: FilterKind,
) -> ast.ExceptHandler:
    # Target code:
    #     import sys as @py_sys
    #     method_except(@py_sys.exc_info())
    #     raise
    #
    # ExceptHandler
    #   Import
    #   Expr
    #     Call
    #       Name
    #         Load
    #       Call
    #         Attribute
    #           Name
    #             Load
    #           Load
    #   Raise
    aliases = [
        ast.alias("sys", "@py_sys", lineno=last_body_lineno, col_offset=0),
    ]

    imports = [
        ast.Import([alias], lineno=last_body_lineno, col_offset=0) for alias in aliases
    ]

    except_handler = factory.ExceptHandler()

    if filter_kind == FilterKind.log_on_project_call:
        if_stmt = factory.If(factory.NameLoad("@caller_in_proj"))
        add_to_body = if_stmt.body = []
        if_stmt.orelse = []
        except_handler.body.append(if_stmt)
    else:
        add_to_body = except_handler.body

    exc_info_attr = factory.Attribute(factory.NameLoad("@py_sys"), "exc_info")
    call_exc_info = factory.Call()
    call_exc_info.func = exc_info_attr

    method_except = factory.NameLoadRewriteCallback("method_except")
    call_method_except = factory.Call()
    call_method_except.func = method_except
    log_method_type: LogElementType = "METHOD"
    call_method_except.args.append(factory.Str(log_method_type))
    call_method_except.args.append(factory.NameLoad("__name__"))
    call_method_except.args.append(factory.NameLoad("__file__"))
    call_method_except.args.append(factory.Str(f"{class_name}{function.name}"))
    call_method_except.args.append(factory.LineConstant())
    call_method_except.args.append(call_exc_info)
    rewrite_ctx.save_func_to_except_method_call(function, call_method_except)

    add_to_body.extend(imports)
    add_to_body.append(factory.Expr(call_method_except))

    except_handler.body.append(factory.Raise())
    return except_handler


def _create_after_method_ast(
    rewrite_ctx: _RewriteCtx, factory, class_name, function, filter_kind
) -> ast.Expr:
    call = factory.Call()
    call.func = factory.NameLoadRewriteCallback("after_method")
    log_method_type: LogElementType = "METHOD"
    call.args.append(factory.Str(log_method_type))
    call.args.append(factory.NameLoad("__name__"))
    call.args.append(factory.NameLoad("__file__"))
    call.args.append(factory.Str(f"{class_name}{function.name}"))
    call.args.append(factory.LineConstant())

    rewrite_ctx.save_func_to_after_method_call(function, call)

    if filter_kind == FilterKind.log_on_project_call:
        return factory.AndExpr(factory.NameLoad("@caller_in_proj"), call)
    else:
        return factory.Expr(call)


def _accept_function_rewrite(function: ast.FunctionDef):
    if function.name.startswith("_") and function.name != "__init__":
        return False

    if not function.body:
        return False
    return True


def _rewrite_funcdef(
    rewrite_ctx: _RewriteCtx, stack, function: ast.FunctionDef, filter_kind
) -> None:
    parent: Any
    # Only rewrite functions which actually have some content.

    class_name = ""
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

    factory = _ast_utils.NodeFactory(
        function_body[0].lineno, function_body[0].col_offset
    )

    before_method_stmts = _create_before_method_ast(
        rewrite_ctx, factory, class_name, function, filter_kind
    )

    for stmt in reversed(before_method_stmts):
        function_body.insert(0, stmt)

    try_finally = factory.Try()
    try_finally.body = function_body

    factory = _ast_utils.NodeFactory(
        function_body[-1].lineno, function_body[-1].col_offset
    )

    after_expr = _create_after_method_ast(
        rewrite_ctx, factory, class_name, function, filter_kind
    )
    try_finally.finalbody = [after_expr]

    except_handler = _create_except_handler_ast(
        rewrite_ctx,
        factory,
        class_name,
        function,
        function_body[-1].lineno,
        filter_kind,
    )

    handlers: List[ast.ExceptHandler] = [except_handler]
    try_finally.handlers = handlers

    function.body = function_body_prefix + [try_finally]


def rewrite_ast_add_callbacks(
    mod: ast.Module,
    filter_kind: FilterKind,
    source: bytes,
    module_path: str,
    config: BaseConfig,
) -> None:
    """Rewrite the module as needed so that the logging is done automatically."""

    if not mod.body:
        # Nothing to do.
        return

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
    imports = _make_import_aliases_ast(lineno, filter_kind)
    mod.body[pos:pos] = imports

    it: Any = _ast_utils.iter_and_replace_nodes(mod)
    node: Any

    rewrite_ctx = _RewriteCtx()
    while True:
        try:
            stack, node = next(it)
        except StopIteration:
            break

        handler = _dispatch.get(node.__class__)
        if handler:
            result = handler(rewrite_ctx, config, module_path, stack, filter_kind, node)
            if result is not None:
                it.send(result)

    if DEBUG:
        print("\n============ New AST (with hooks in place) ==============\n")
        # Note: only python 3.9 onwards.
        print(ast.unparse(mod))  # type: ignore


def _handle_funcdef(
    rewrite_ctx: _RewriteCtx, config, module_path, stack, filter_kind, node
):
    try:
        function: ast.FunctionDef = node
        if not _accept_function_rewrite(function):
            return

        _rewrite_funcdef(rewrite_ctx, stack, node, filter_kind)
    except Exception:
        raise RuntimeError(
            f"Error when rewriting function: {node.name} line: {node.lineno} at: {module_path}"
        )


def _handle_return(
    rewrite_ctx: _RewriteCtx, config, module_path, stack, filter_kind, node
):
    func_and_class_name = _get_function_and_class_name(stack)
    if not func_and_class_name:
        return None

    function, class_name = func_and_class_name
    if not _accept_function_rewrite(function):
        return

    try:
        return _rewrite_return(function, class_name, node)
    except Exception:
        raise RuntimeError(
            f"Error when rewriting function return: {function.name} line: {node.lineno} at: {module_path}"
        )


def _handle_assign(
    rewrite_ctx: _RewriteCtx, config: BaseConfig, module_path, stack, filter_kind, node
):
    if filter_kind != FilterKind.full_log or not config.get_rewrite_assigns():
        return None

    func_and_class_name = _get_function_and_class_name(stack)
    if not func_and_class_name:
        return None

    function, class_name = func_and_class_name
    if not _accept_function_rewrite(function):
        return

    try:
        return _rewrite_assign(function, class_name, node)
    except Exception:
        raise RuntimeError(
            f"Error when rewriting assign: {function.name} line: {node.lineno} at: {module_path}"
        )


def _handle_expr(
    rewrite_ctx: _RewriteCtx, config, module_path, stack, filter_kind, node: ast.Expr
):
    if isinstance(node.value, ast.Yield):
        func_and_class_name = _get_function_and_class_name(stack)
        if not func_and_class_name:
            return None

        function, class_name = func_and_class_name
        if not _accept_function_rewrite(function):
            return

        try:
            before_call: ast.Call
            for before_call in rewrite_ctx.iter_func_calls_from_func(function):
                assert isinstance(before_call.args[0], ast.Str)
                before_call_method_type: ast.Str = before_call.args[0]

                log_method_type: LogElementType = "GENERATOR"
                if filter_kind == FilterKind.log_on_project_call:
                    log_method_type = "UNTRACKED_GENERATOR"
                before_call_method_type.s = log_method_type

            if filter_kind != FilterKind.full_log:
                return None

            return _rewrite_yield(function, class_name, node)
        except Exception:
            raise RuntimeError(
                f"Error when rewriting assign: {function.name} line: {node.lineno} at: {module_path}"
            )


_dispatch: Dict[
    type,
    Callable[[_RewriteCtx, BaseConfig, str, list, FilterKind, Any], Optional[list]],
] = {}
_dispatch[ast.Return] = _handle_return
_dispatch[ast.Assign] = _handle_assign
_dispatch[ast.FunctionDef] = _handle_funcdef

# We can't deal with the Yield directly because it's a field of the Expr statement
# and we can't rewrite a field (so, we have to go to the stmt level to be able to
# rewrite it and then check if it's some expr we want to deal with -- and we also
# need to check whether a yield appears in an assign).
_dispatch[ast.Expr] = _handle_expr
