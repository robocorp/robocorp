import ast
from typing import Any, Union, List, Optional, Tuple
from . import _ast_utils
from ._config import BaseConfig, FilterKind

DEBUG = False


def is_rewrite_disabled(docstring: str) -> bool:
    return "NO_LOG" in docstring


def _make_import_aliases_ast(lineno, filter_kind: FilterKind):
    aliases = [
        ast.alias(
            "robo_log._lifecycle_hooks",
            "@robocorp_rewrite_callbacks",
            lineno=lineno,
            col_offset=0,
        ),
    ]

    if filter_kind == FilterKind.log_on_project_call:
        aliases.append(ast.alias("robo_log", "@robo_log", lineno=lineno, col_offset=0))

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


def _rewrite_return(function, class_name, node) -> Optional[list]:
    if function.name.startswith("_"):
        return None

    factory = _ast_utils.NodeFactory(node.lineno, node.col_offset)

    result: list = []

    call = factory.Call()
    call.func = factory.NameLoadRewriteCallback("method_return")
    call.args.append(factory.NameLoad("__package__"))
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


_EMPTY_LIST: list = []


def _create_before_method_ast(factory, class_name, function, filter_kind) -> list:
    # Target code:
    # def method(a, b):
    #     before_method(__package__, __name, __file__, "method_name", 11, {'a': a, 'b': b})
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
    call.args.append(factory.NameLoad("__package__"))
    call.args.append(factory.NameLoad("__name__"))
    call.args.append(factory.NameLoad("__file__"))
    call.args.append(factory.Str(f"{class_name}{function.name}"))
    call.args.append(factory.LineConstant())

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
    factory,
    class_name: str,
    function: ast.FunctionDef,
    last_body_lineno,
    filter_kind: FilterKind,
):
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
    call_method_except.args.append(factory.NameLoad("__package__"))
    call_method_except.args.append(factory.NameLoad("__name__"))
    call_method_except.args.append(factory.NameLoad("__file__"))
    call_method_except.args.append(factory.Str(f"{class_name}{function.name}"))
    call_method_except.args.append(factory.LineConstant())
    call_method_except.args.append(call_exc_info)

    add_to_body.extend(imports)
    add_to_body.append(factory.Expr(call_method_except))

    except_handler.body.append(factory.Raise())
    return except_handler


def _create_after_method_ast(factory, class_name, function, filter_kind):
    call = factory.Call()
    call.func = factory.NameLoadRewriteCallback("after_method")
    call.args.append(factory.NameLoad("__package__"))
    call.args.append(factory.NameLoad("__name__"))
    call.args.append(factory.NameLoad("__file__"))
    call.args.append(factory.Str(f"{class_name}{function.name}"))
    call.args.append(factory.LineConstant())

    if filter_kind == FilterKind.log_on_project_call:
        return factory.AndExpr(factory.NameLoad("@caller_in_proj"), call)
    else:
        return factory.Expr(call)


def _rewrite_funcdef(stack, node, filter_kind):
    parent: Any
    function: ast.FunctionDef = node
    if function.name.startswith("_") and function.name != "__init__":
        return

    if not function.body:
        return
    # Only rewrite functions which actually have some content.

    class_name = ""
    if stack:
        parent = stack[-1]
        if parent.__class__.__name__ == "ClassDef":
            class_name = parent.name + "."

    first_non_constant_stmt_index = 0
    for stmt in function.body:
        if (
            stmt.__class__.__name__ == "Expr"
            and stmt.value.__class__.__name__ == "Constant"
        ):
            first_non_constant_stmt_index += 1
            continue
        break

    function_body = function.body
    function.body = None  # Proper value will be set later.

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
        factory, class_name, function, filter_kind
    )

    for stmt in reversed(before_method_stmts):
        function_body.insert(0, stmt)

    try_finally = factory.Try()
    try_finally.body = function_body

    factory = _ast_utils.NodeFactory(
        function_body[-1].lineno, function_body[-1].col_offset
    )

    after_expr = _create_after_method_ast(factory, class_name, function, filter_kind)
    try_finally.finalbody = [after_expr]

    except_handler = _create_except_handler_ast(
        factory, class_name, function, function_body[-1].lineno, filter_kind
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

    while True:
        try:
            stack, node = next(it)
        except StopIteration:
            break

        if node.__class__.__name__ == "Return":
            func_and_class_name = _get_function_and_class_name(stack)
            if not func_and_class_name:
                continue
            function, class_name = func_and_class_name

            try:
                result = _rewrite_return(function, class_name, node)
            except Exception:
                raise RuntimeError(
                    f"Error when rewriting function return: {function.name} line: {node.lineno} at: {module_path}"
                )

            if result is None:
                continue
            it.send(result)

        elif node.__class__.__name__ == "FunctionDef":
            try:
                _rewrite_funcdef(stack, node, filter_kind)
            except Exception:
                raise RuntimeError(
                    f"Error when rewriting function: {node.name} line: {node.lineno} at: {module_path}"
                )

    if DEBUG:
        print("\n============ New AST (with hooks in place) ==============\n")
        # Note: only python 3.9 onwards.
        print(ast.unparse(mod))  # type: ignore
