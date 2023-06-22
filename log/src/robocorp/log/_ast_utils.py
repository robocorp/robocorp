import ast
import ast as ast_module
import itertools
import sys
import types
from ast import AST
from contextlib import contextmanager
from functools import partial
from typing import (
    Generator,
    Generic,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from robocorp.log._lifecycle_hooks import Callback


class _NodesProviderVisitor(ast_module.NodeVisitor):
    def __init__(self, on_node=lambda node: None):
        ast_module.NodeVisitor.__init__(self)
        self._stack = []
        self.on_node = on_node

    def generic_visit(self, node):
        self._stack.append(node)
        self.on_node(self._stack, node)
        ast_module.NodeVisitor.generic_visit(self, node)
        self._stack.pop()


class _PrinterVisitor(ast_module.NodeVisitor):
    def __init__(self, stream):
        ast_module.NodeVisitor.__init__(self)
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

            ast_module.NodeVisitor.generic_visit(self, node)
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


def iter_nodes(node, accept=lambda _node: True) -> Iterator[ast_module.AST]:
    for _field, value in ast_module.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast_module.AST):
                    if accept(item):
                        yield item
                        yield from iter_nodes(item, accept)

        elif isinstance(value, ast_module.AST):
            if accept(value):
                yield value
                yield from iter_nodes(value, accept)


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

    def __init__(self, parent, node):
        # The parent node.
        self.parent = parent

        # This is the current node in the cursor.
        self._node = node

    @property
    def node(self):  # read-only (to change, change 'current')
        return self._node

    @property
    def after(self):
        return self._after

    @property
    def before(self):
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


ASTRewriteEv = Literal["before", "after"]


class ASTRewriter:
    def __init__(self, ast: AST) -> None:
        self._ast = ast
        self._stack: List[AST] = []
        self._cursor_stack: List[_RewriteCursor] = []
        self._next_var_id: "partial[int]" = partial(next, itertools.count())
        self._is_generator_cache: dict = {}
        self._funcdef_memo_stack: List[FuncdefMemoStack] = [FuncdefMemoStack()]
        self._on_context_id_generated = Callback()

    def iter_and_replace_nodes(
        self,
    ) -> Generator[
        Tuple[ASTRewriteEv, List[AST], AST], Optional[types.GeneratorType], None
    ]:
        yield from self._iter_and_replace_nodes(self._ast)

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
        stack = self._funcdef_memo_stack[-1]
        next_id = stack.next_context_id()
        self._on_context_id_generated(stack, next_id)
        return next_id

    @contextmanager
    def record_context_ids(self) -> Iterator[List[int]]:
        curr = self._funcdef_memo_stack[-1]
        ids = []

        def on_generated(stack, next_id):
            if stack is curr:
                ids.append(next_id)

        with self._on_context_id_generated.register(on_generated):
            yield ids

    def current_funcdef_memo_stack(self) -> FuncdefMemoStack:
        return self._funcdef_memo_stack[-1]

    def _iter_and_replace_nodes(
        self, node
    ) -> Generator[
        Tuple[ASTRewriteEv, List[AST], AST], Optional[types.GeneratorType], None
    ]:
        if isinstance(node, ast.FunctionDef):
            self._funcdef_memo_stack.append(FuncdefMemoStack())
        try:
            yield from self._inner_iter_and_replace_nodes(node)
        finally:
            if isinstance(node, ast.FunctionDef):
                self._funcdef_memo_stack.pop(-1)

    def _inner_iter_and_replace_nodes(
        self, node
    ) -> Generator[
        Tuple[ASTRewriteEv, List[AST], AST], Optional[types.GeneratorType], None
    ]:
        """
        :note: the yielded stack is actually always the same (mutable) list, so,
        clients that want to return it somewhere else should create a copy.
        """
        stack: List[AST] = self._stack

        for field, value in ast_module.iter_fields(node):
            if isinstance(value, list):
                new_value: List[AST] = []
                changed = False

                for item in value:
                    if isinstance(item, AST):
                        self._cursor_stack.append(_RewriteCursor(node, item))

                        gen = yield "before", stack, item
                        if gen is not None:
                            try:
                                next(gen)
                            except StopIteration:
                                raise AssertionError(
                                    f"Expected generator {gen} to yield once!"
                                )

                        stack.append(item)
                        yield from self._iter_and_replace_nodes(item)
                        stack.pop()

                        try:
                            if gen is not None:
                                next(gen)
                        except StopIteration:
                            pass
                        yield "after", stack, item

                        last_cursor = self._cursor_stack.pop(-1)
                        if last_cursor.before is not None:
                            if isinstance(last_cursor.before, list):
                                new_value.extend(last_cursor.before)
                            else:
                                assert isinstance(last_cursor.before, AST)
                                new_value.append(last_cursor.before)
                            changed = True

                        if last_cursor.current is not None:
                            if isinstance(last_cursor.current, list):
                                new_value.extend(last_cursor.current)
                            else:
                                assert isinstance(last_cursor.current, AST)
                                new_value.append(last_cursor.current)
                            changed = True
                        else:
                            new_value.append(item)

                        if last_cursor.after is not None:
                            if isinstance(last_cursor.after, list):
                                new_value.extend(last_cursor.after)
                            else:
                                assert isinstance(last_cursor.after, AST)
                                new_value.append(last_cursor.after)
                            changed = True

                if changed:
                    setattr(node, field, new_value)

            elif isinstance(value, AST):
                self._cursor_stack.append(_RewriteCursor(node, value))

                yield "before", stack, value
                stack.append(value)
                yield from self._iter_and_replace_nodes(value)
                stack.pop()
                yield "after", stack, value

                last_cursor = self._cursor_stack.pop(-1)
                if last_cursor.before is not None or last_cursor.after is not None:
                    stack_repr = "\n".join(str(x) for x in self._stack)
                    raise RuntimeError(
                        f"Cannot rewrite before/after in attribute, just in list.\nField: '{field}'\nStack:\n{stack_repr}"
                    )

                if last_cursor.current is not None:
                    assert isinstance(last_cursor.current, ast.AST)
                    setattr(node, field, last_cursor.current)

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
        return _compute_is_generator(self._is_generator_cache, function)


def _compute_is_generator(cache, function):
    try:
        return cache[function]
    except KeyError:
        pass
    for node in iter_nodes(function, dont_accept_class_nor_funcdef):
        if isinstance(node, (ast.Yield, ast.YieldFrom)):
            cache[function] = True
            return True

    cache[function] = False
    return False


def dont_accept_class_nor_funcdef(node):
    return not isinstance(node, (ast.FunctionDef, ast.ClassDef))


def copy_line_and_col(from_node, to_node):
    to_node.lineno = from_node.lineno
    to_node.col_offset = from_node.col_offset


class NodeFactory:
    def __init__(
        self, lineno: int, col_offset: int, next_var_id: Optional["partial[int]"] = None
    ):
        self.lineno = lineno
        self.col_offset = col_offset
        if next_var_id is None:
            next_var_id = partial(next, itertools.count())
        self.next_var_id = next_var_id

    def _set_line_col(self, node):
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

    def If(self, cond) -> ast.If:
        return self._set_line_col(ast.If(cond))

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

    def LineConstant(self) -> ast.Constant:
        return self._set_line_col(ast.Constant(self.lineno))

    def IntConstant(self, value: int) -> ast.Constant:
        return self._set_line_col(ast.Constant(value))

    def NoneConstant(self) -> ast.Constant:
        return self._set_line_col(ast.Constant(None))

    def ExceptHandler(self) -> ast.ExceptHandler:
        return self._set_line_col(ast.ExceptHandler(body=[]))

    def Raise(self) -> ast.Raise:
        return self._set_line_col(ast.Raise())
