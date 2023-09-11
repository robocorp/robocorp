import ast
import itertools
import sys
from ast import AST
from contextlib import contextmanager
from functools import partial
from typing import Any, Generic, Iterator, List, Optional, Tuple, TypeVar, Union

from robocorp.log._lifecycle_hooks import Callback


class _NodesProviderVisitor(ast.NodeVisitor):
    def __init__(self, on_node=lambda node: None):
        ast.NodeVisitor.__init__(self)
        self._stack = []
        self.on_node = on_node

    def generic_visit(self, node):
        self._stack.append(node)
        self.on_node(self._stack, node)
        ast.NodeVisitor.generic_visit(self, node)
        self._stack.pop()


class _PrinterVisitor(ast.NodeVisitor):
    def __init__(self, stream):
        ast.NodeVisitor.__init__(self)
        self._level = 0
        self._stream = stream

    def _replace_spacing(self, txt):
        curr_len = len(txt)
        delta = 80 - curr_len
        return txt.replace("*SPACING*", " " * delta)

    def generic_visit(self, node):
        # Note: prints line and col offsets 0-based (even if the ast is 1-based for
        # lines and 0-based for columns).
        self._level += 1
        try:
            indent = "  " * self._level
            node_lineno = getattr(node, "lineno", -1)
            if node_lineno != -1:
                # Make 0-based
                node_lineno -= 1
            node_end_lineno = getattr(node, "end_lineno", -1)
            if node_end_lineno != -1 and node_end_lineno is not None:
                # Make 0-based
                node_end_lineno -= 1
            self._stream.write(
                self._replace_spacing(
                    "%s%s *SPACING* (%s, %s) -> (%s, %s)\n"
                    % (
                        indent,
                        node.__class__.__name__,
                        node_lineno,
                        getattr(node, "col_offset", -1),
                        node_end_lineno,
                        getattr(node, "end_col_offset", -1),
                    )
                )
            )
            tokens = getattr(node, "tokens", [])
            for token in tokens:
                token_lineno = token.lineno
                if token_lineno != -1:
                    # Make 0-based
                    token_lineno -= 1

                self._stream.write(
                    self._replace_spacing(
                        "%s- %s, '%s' *SPACING* (%s, %s->%s)\n"
                        % (
                            indent,
                            token.type,
                            token.value.replace("\n", "\\n").replace("\r", "\\r"),
                            token_lineno,
                            token.col_offset,
                            token.end_col_offset,
                        )
                    )
                )

            ast.NodeVisitor.generic_visit(self, node)
        finally:
            self._level -= 1


T = TypeVar("T")
Y = TypeVar("Y", covariant=True)


class NodeInfo(Generic[Y]):
    stack: Tuple[AST, ...]
    node: Y

    __slots__ = ["stack", "node"]

    def __init__(self, stack, node):
        self.stack = stack
        self.node = node

    def __str__(self):
        return f"NodeInfo({self.node.__class__.__name__})"

    __repr__ = __str__


def iter_nodes(
    node, accept=lambda node: isinstance(node, ast.AST)
) -> Iterator[ast.AST]:
    for field in node._fields:
        value = getattr(node, field, None)
        if isinstance(value, list):
            for item in value:
                if accept(item):
                    yield item
                    yield from iter_nodes(item, accept)

        elif accept(value):
            yield value  # type: ignore
            yield from iter_nodes(value, accept)


def iter_nodes_to_collect_names(node: ast.AST) -> Iterator[ast.AST]:
    """
    Same as iter_nodes but with the accept hardcoded (so that it's a bit faster).
    """
    for field in node._fields:
        value = getattr(node, field, None)
        if isinstance(value, list):
            for item in value:
                if isinstance(
                    item,
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
                ):
                    yield item
                    yield from iter_nodes_to_collect_names(item)

        elif isinstance(
            value,
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
        ):
            yield value
            yield from iter_nodes_to_collect_names(value)


def print_ast(node, stream=None):
    if stream is None:
        stream = sys.stderr
    errors_visitor = _PrinterVisitor(stream)
    errors_visitor.visit(node)


class _RewriteCursor:
    # These can be set in the instance to change the current node or
    # something around it.
    _before: Optional[List[AST]] = None
    _after: Optional[List[AST]] = None

    current: Optional[Union[AST, List[AST]]] = None

    def __init__(self, parent, node: AST):
        # The parent node.
        self.parent = parent

        # This is the current node in the cursor.
        self._node = node

    @property
    def node(self) -> AST:  # read-only (to change, change 'current')
        return self._node

    @property
    def after(self) -> Optional[List[AST]]:
        return self._after

    @property
    def before(self) -> Optional[List[AST]]:
        return self._before

    def before_append(self, node: AST):
        if self._before is None:
            self._before = [node]
        else:
            self._before.append(node)

    def after_append(self, node: AST):
        if self._after is None:
            self._after = [node]
        else:
            self._after.append(node)

    def after_prepend(self, node: AST):
        if self._after is None:
            self._after = [node]
        else:
            self._after.insert(0, node)

    def __eq__(self, o):
        if isinstance(o, _RewriteCursor):
            return self.node == o.node

        return False


class FuncdefMemoStack:
    def __init__(self):
        self._ctx_id = itertools.count(1)

    def next_context_id(self):
        return next(self._ctx_id)


class DontGoIntoNode:
    pass


class _FuncDefMemoStackQueue:
    __slots__ = ["_stack"]

    def __init__(self) -> None:
        # Note: start with none and fill with the actual instance
        # only when needed.
        self._stack: List[Optional[FuncdefMemoStack]] = [None]

    def push(self) -> None:
        self._stack.append(None)

    def pop(self) -> None:
        self._stack.pop(-1)

    def peek(self) -> FuncdefMemoStack:
        s = self._stack[-1]
        if s is None:
            # Lazily create it (so,
            s = FuncdefMemoStack()
            self._stack[-1] = s
        return s


class ASTRewriter:
    """
    The `before handler` callback can return a generator which can be used to have
    control in the callback of the start/end of the node being traversed.

    If the generator yields `DONT_GO_INTO_NODE`, that node won't be traversed.

    The `after handler` is called after the node is traversed (and is usually
    the place where modifications should happen -- note that modifications
    can still happen in the `before handler`, but in this case, the modified
    node will be traversed and not the original one found in the AST).
    """

    # In a before this may be yielded so that we don't go into a node.
    DONT_GO_INTO_NODE = DontGoIntoNode()

    def __init__(self, ast: AST, dispatch_data: Any, config, module_path, kind) -> None:
        self._ast = ast
        self._cursor_stack: List[_RewriteCursor] = []
        self._next_var_id: "partial[int]" = partial(next, itertools.count())
        self._is_generator_cache: dict = {}
        self._funcdef_memo_stack: _FuncDefMemoStackQueue = _FuncDefMemoStackQueue()
        self._on_context_id_generated = Callback()

        # Optional info (the user can fill it with any data).
        self.dispatch_data = dispatch_data

        self.stack: List[AST] = []

        self._get_before_handler = dispatch_data.dispatch_before.get
        self._get_after_handler = dispatch_data.dispatch_after.get

        self._config = config
        self._module_path = module_path
        self._kind = kind

    def next_context_id(self) -> int:
        """
        The id returned should be used for control statements such as for or
        while loops.

        If there's some structure with an except it needs to mark all control
        statements that were unfinished.

        i.e.: Something as:

        try:
            id = next_context_id()
            before_iter(id, ...)
            for a in xxx:
                id2 = next_context_id()
                before_step_iter(id2, ...)
                ...
                after_step_iter(id2, ...)
            after_iter(id)
        except:
            handle_except((id, id2))
        """
        stack = self._funcdef_memo_stack.peek()
        next_id = stack.next_context_id()
        self._on_context_id_generated(stack, next_id)
        return next_id

    @contextmanager
    def record_context_ids(self) -> Iterator[List[int]]:
        curr: FuncdefMemoStack = self._funcdef_memo_stack.peek()
        ids = []

        def on_generated(stack, next_id):
            if stack is curr:
                ids.append(next_id)

        with self._on_context_id_generated.register(on_generated):
            yield ids

    def get_function_and_class_name(
        self,
    ) -> Optional[Tuple[ast.FunctionDef, str]]:
        if not self.stack:
            return None
        stack_it = reversed(self.stack)
        for function in stack_it:
            funcname = function.__class__.__name__
            if funcname == "FunctionDef":
                break
            continue
        else:
            return None

        class_name = ""
        try:
            parent = next(stack_it)
            if parent.__class__.__name__ == "ClassDef":
                class_name = parent.name + "."  # type: ignore
        except StopIteration:
            pass

        return function, class_name  # type: ignore

    def iter_and_replace_nodes(self, curr_node: ast.AST) -> None:
        """
        Traverses all the nodes under the given node.
        """
        is_func_def: bool = isinstance(curr_node, ast.FunctionDef)
        field: str
        if is_func_def:
            self._funcdef_memo_stack.push()

        DONT_GO_INTO_NODE = self.DONT_GO_INTO_NODE

        stack: List[AST] = self.stack

        get_before = self._get_before_handler
        get_after = self._get_after_handler

        for field in curr_node._fields:
            value = getattr(curr_node, field, None)
            if isinstance(value, list):
                new_value: List[AST] = []
                changed: bool = False

                for item in value:
                    if isinstance(item, AST):
                        handler_before = get_before(item.__class__)
                        handler_after = get_after(item.__class__)

                        go_into: bool = True
                        self._cursor_stack.append(_RewriteCursor(curr_node, item))

                        gen = None
                        if handler_before is not None:
                            gen = handler_before(
                                self,
                                self._config,
                                self._module_path,
                                self._kind,
                                item,
                            )
                            if gen is not None:
                                try:
                                    if next(gen) is DONT_GO_INTO_NODE:
                                        go_into = False
                                except StopIteration:
                                    raise AssertionError(
                                        f"Expected generator {gen} to yield once. Handling: {ast.unparse(item)}"
                                    )

                        if go_into:
                            stack.append(item)
                            self.iter_and_replace_nodes(item)
                            stack.pop()

                        try:
                            if gen is not None:
                                next(gen)
                        except StopIteration:
                            pass

                        # After node
                        if handler_after:
                            result = handler_after(
                                self,
                                self._config,
                                self._module_path,
                                self._kind,
                                item,
                            )
                            if result is not None:
                                self.cursor.current = result

                        last_cursor: _RewriteCursor = self._cursor_stack.pop(-1)
                        last_cursor_before: Optional[List[AST]] = last_cursor._before
                        if last_cursor_before is not None:
                            new_value.extend(last_cursor_before)
                            changed = True

                        last_cursor_current: Optional[
                            Union[AST, List[AST]]
                        ] = last_cursor.current
                        if last_cursor_current is not None:
                            if isinstance(last_cursor_current, list):
                                new_value.extend(last_cursor_current)
                            else:
                                assert isinstance(last_cursor_current, AST)
                                new_value.append(last_cursor_current)
                            changed = True
                        else:
                            new_value.append(item)

                        last_cursor_after: Optional[List[AST]] = last_cursor._after
                        if last_cursor_after is not None:
                            new_value.extend(last_cursor_after)
                            changed = True

                    else:
                        new_value.append(item)

                if changed:
                    setattr(curr_node, field, new_value)

            elif isinstance(value, AST):
                self._cursor_stack.append(_RewriteCursor(curr_node, value))

                go_into = True

                # Before node
                handler_before = get_before(value.__class__)
                gen = None
                if handler_before is not None:
                    gen = handler_before(
                        self, self._config, self._module_path, self._kind, value
                    )
                    if gen is not None:
                        try:
                            if next(gen) is DONT_GO_INTO_NODE:
                                go_into = False
                        except StopIteration:
                            raise AssertionError(
                                f"Expected generator {gen} to yield once. Handling: {ast.unparse(value)}"
                            )

                if go_into:
                    stack.append(value)
                    self.iter_and_replace_nodes(value)
                    stack.pop()
                try:
                    if gen is not None:
                        next(gen)
                except StopIteration:
                    pass

                # After node
                handler_after = get_after(value.__class__)
                if handler_after:
                    result = handler_after(
                        self, self._config, self._module_path, self._kind, value
                    )
                    if result is not None:
                        self.cursor.current = result

                last_cursor = self._cursor_stack.pop(-1)
                if last_cursor._before is not None or last_cursor._after is not None:
                    stack_repr = "\n".join(str(x) for x in self.stack)
                    raise RuntimeError(
                        f"Cannot rewrite before/after in attribute, just in list.\nField: '{field}'\nStack:\n{stack_repr}"
                    )

                if last_cursor.current is not None:
                    assert isinstance(last_cursor.current, ast.AST)
                    setattr(curr_node, field, last_cursor.current)

        if is_func_def:
            self._funcdef_memo_stack.pop()

    @property
    def cursor(self) -> _RewriteCursor:
        return self._cursor_stack[-1]

    @property
    def stmts_cursor(self) -> _RewriteCursor:
        for cursor in reversed(self._cursor_stack):
            if isinstance(cursor.node, ast.stmt):
                return cursor

        stack_repr = "\n".join(str(x.node) for x in self._cursor_stack)
        raise RuntimeError(f"Did not find stmts cursor.\nStack:\n{stack_repr}")

    def NodeFactory(self, lineno: int, col_offset: int) -> "NodeFactory":
        return NodeFactory(lineno, col_offset, self._next_var_id)

    def is_generator(self, function: ast.FunctionDef):
        # Note: caching is important as it must be called once before the function
        # is changed.
        try:
            return self._is_generator_cache[function]
        except KeyError:
            pass
        is_generator = self._is_generator_cache[function] = _compute_is_generator(
            function
        )
        return is_generator


def _compute_is_generator(function: ast.FunctionDef) -> bool:
    stack: List[ast.AST] = [function]
    field: str
    current_node: ast.AST

    while stack:
        current_node = stack.pop()

        for field in current_node._fields:
            value = getattr(current_node, field, None)

            if isinstance(value, list):
                for item in value:
                    if isinstance(
                        item, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)
                    ):
                        continue

                    if isinstance(item, (ast.Yield, ast.YieldFrom)):
                        return True

                    if isinstance(item, ast.AST):
                        stack.append(item)

            else:
                if isinstance(
                    value, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)
                ):
                    continue

                if isinstance(value, (ast.Yield, ast.YieldFrom)):
                    return True

                if isinstance(value, ast.AST):
                    stack.append(value)

    return False


def dont_accept_class_nor_funcdef(node):
    return not isinstance(node, (ast.FunctionDef, ast.ClassDef))


def copy_line_and_col(from_node, to_node):
    to_node.lineno = from_node.lineno
    to_node.col_offset = from_node.col_offset


class NodeFactory:
    def __init__(self, lineno: int, col_offset: int, next_var_id=None):
        self.lineno = lineno
        self.col_offset = col_offset
        if next_var_id is None:
            next_var_id = partial(next, itertools.count())
        self.next_var_id = next_var_id

    def _set_line_col(self, node: ast.AST):
        node.lineno = self.lineno
        node.col_offset = self.col_offset
        return node

    def Call(self, func: ast.expr) -> ast.Call:
        """
        Args:
            func: The function call expression.

        Example:
            factory.Call(factory.NameLoad("some_name"))
        """
        call = ast.Call(keywords=[], args=[])
        if func is not None:
            call.func = func
        return self._set_line_col(call)

    def FunctionDefTemp(self) -> ast.FunctionDef:
        name = f"@tmp_{self.next_var_id()}"
        args = self._set_line_col(
            ast.arguments(
                posonlyargs=[], args=[], kwonlyargs=[], defaults=[], kw_defaults=[]
            )
        )
        function_def = ast.FunctionDef(name, body=[], decorator_list=[], args=args)
        return self._set_line_col(function_def)

    def YieldFrom(self, value=None) -> ast.YieldFrom:
        yield_from = ast.YieldFrom(value=value)
        return self._set_line_col(yield_from)

    def Yield(self, value=None) -> ast.Yield:
        yield_from = ast.Yield(value=value)
        return self._set_line_col(yield_from)

    def Assign(self, targets=[], value=None) -> ast.Assign:
        assign = ast.Assign(targets=targets, value=value)
        return self._set_line_col(assign)

    def NameLoad(self, name: str) -> ast.Name:
        return self._set_line_col(ast.Name(name, ast.Load()))

    def Tuple(self, *elts) -> ast.Tuple:
        return self._set_line_col(ast.Tuple(elts=list(elts), ctx=ast.Load()))

    def Return(self, value: ast.expr) -> ast.Return:
        return self._set_line_col(ast.Return(value))

    def NameTempStore(self) -> ast.Name:
        name = f"@tmp_{self.next_var_id()}"
        return self.NameStore(name)

    def NameStore(self, name) -> ast.Name:
        return self._set_line_col(ast.Name(name, ast.Store()))

    def Attribute(self, name: ast.AST, attr_name: str) -> ast.Attribute:
        return self._set_line_col(ast.Attribute(name, attr_name, ast.Load()))

    def NameLoadRewriteCallback(self, builtin_name: str) -> ast.Attribute:
        ref = self.NameLoad("@robo_lifecycle_hooks")

        return self._set_line_col(self.Attribute(ref, builtin_name))

    def NameLoadCtx(self, attr_name: str) -> ast.Attribute:
        ref = self.NameLoad("@ctx")

        return self._set_line_col(self.Attribute(ref, attr_name))

    def NameLoadRobo(self, builtin_name: str) -> ast.Attribute:
        ref = self.NameLoad("@robolog")

        return self._set_line_col(self.Attribute(ref, builtin_name))

    def Str(self, s) -> ast.Str:
        return self._set_line_col(ast.Str(s))

    def Constant(self, s) -> ast.Constant:
        return self._set_line_col(ast.Constant(s))

    def FormattedValue(self, s) -> ast.FormattedValue:
        v = ast.FormattedValue(value=s)
        v.conversion = -1
        v.format_spec = None
        return self._set_line_col(v)

    def If(self, cond: ast.expr) -> ast.If:
        return self._set_line_col(ast.If(cond))

    def NotUnaryOp(self, operand: ast.expr) -> ast.UnaryOp:
        return self._set_line_col(
            ast.UnaryOp(operand=operand, op=self._set_line_col(ast.Not()))
        )

    def AndExpr(self, expr1, expr2) -> ast.Expr:
        andop = self._set_line_col(ast.And())
        bool_op = self._set_line_col(ast.BoolOp(op=andop, values=[expr1, expr2]))

        return self.Expr(bool_op)

    def Expr(self, expr) -> ast.Expr:
        return self._set_line_col(ast.Expr(expr))

    def Try(self) -> ast.Try:
        try_node = ast.Try(handlers=[], orelse=[])
        return self._set_line_col(try_node)

    def WithStmt(self, **kwargs) -> ast.With:
        with_node = ast.With(**kwargs)
        return self._set_line_col(with_node)

    def withitem(self, **kwargs) -> ast.With:
        with_node = ast.withitem(**kwargs)
        return self._set_line_col(with_node)

    def TryFinally(
        self,
        body: List[ast.stmt],
        final_body: List[ast.stmt],
        handlers: Optional[List[ast.ExceptHandler]] = None,
    ) -> ast.Try:
        try_node = ast.Try(handlers=handlers or [], orelse=[])
        try_node.body = body
        try_node.finalbody = final_body
        return self._set_line_col(try_node)

    def Dict(self) -> ast.Dict:
        return self._set_line_col(ast.Dict())

    def LineConstantAt(self, lineno) -> ast.Constant:
        return self._set_line_col(ast.Constant(lineno))

    def IntConstant(self, value: int) -> ast.Constant:
        return self._set_line_col(ast.Constant(value))

    def NoneConstant(self) -> ast.Constant:
        return self._set_line_col(ast.Constant(None))

    def ExceptHandler(self) -> ast.ExceptHandler:
        return self._set_line_col(ast.ExceptHandler(body=[]))

    def Raise(self) -> ast.Raise:
        return self._set_line_col(ast.Raise())

    def JoinedStr(self) -> ast.JoinedStr:
        return self._set_line_col(ast.JoinedStr())
