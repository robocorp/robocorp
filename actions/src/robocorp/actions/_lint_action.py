import ast as ast_module
from dataclasses import dataclass
from typing import Any, Iterator, List, Optional, Tuple, TypedDict, Union, overload

from robocorp.tasks._customization._plugin_manager import PluginManager


def _iter_nodes(
    node, internal_stack: Optional[List[Any]] = None, recursive=True
) -> Iterator[Tuple[List[Any], Any]]:
    """
    :note: the yielded stack is actually always the same (mutable) list, so,
    clients that want to return it somewhere else should create a copy.
    """
    stack: List[Any]
    if internal_stack is None:
        stack = []
        if node.__class__.__name__ != "File":
            stack.append(node)
    else:
        stack = internal_stack

    if recursive:
        for _field, value in ast_module.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast_module.AST):
                        yield stack, item
                        stack.append(item)
                        yield from _iter_nodes(item, stack, recursive=True)
                        stack.pop()

            elif isinstance(value, ast_module.AST):
                yield stack, value
                stack.append(value)

                yield from _iter_nodes(value, stack, recursive=True)

                stack.pop()
    else:
        # Not recursive
        for _field, value in ast_module.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast_module.AST):
                        yield stack, item

            elif isinstance(value, ast_module.AST):
                yield stack, value


class PositionTypedDict(TypedDict):
    # Line position in a document (zero-based).
    line: int

    # Character offset on a line in a document (zero-based). Assuming that
    # the line is represented as a string, the `character` value represents
    # the gap between the `character` and `character + 1`.
    #
    # If the character value is greater than the line length it defaults back
    # to the line length.
    character: int


class RangeTypedDict(TypedDict):
    start: PositionTypedDict
    end: PositionTypedDict


class DiagnosticsTypedDict(TypedDict, total=False):
    # The range at which the message applies.
    range: RangeTypedDict

    # The diagnostic's severity. Can be omitted. If omitted it is up to the
    # client to interpret diagnostics as error, warning, info or hint.
    severity: Optional[int]  # DiagnosticSeverity

    # The diagnostic's code, which might appear in the user interface.
    code: Union[int, str]

    # An optional property to describe the error code.
    #
    # @since 3.16.0
    codeDescription: Any

    # A human-readable string describing the source of this
    # diagnostic, e.g. 'typescript' or 'super lint'.
    source: Optional[str]

    # The diagnostic's message.
    message: str

    # Additional metadata about the diagnostic.
    #
    # @since 3.15.0
    tags: list  # DiagnosticTag[];

    # An array of related diagnostic information, e.g. when symbol-names within
    # a scope collide all definitions can be marked via this property.
    relatedInformation: list  # DiagnosticRelatedInformation[];

    # A data entry field that is preserved between a
    # `textDocument/publishDiagnostics` notification and
    # `textDocument/codeAction` request.
    #
    # @since 3.16.0
    data: Optional[Any]  # unknown;


class DiagnosticSeverity:
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class Error(object):
    __slots__ = "msg start end severity tags data".split(" ")

    def __init__(
        self,
        msg: str,
        start: Tuple[int, int],
        end: Tuple[int, int],
        severity: int = DiagnosticSeverity.Error,
    ):
        """
        Note: `start` and `end` are tuples with (line, col).
        """
        self.msg = msg
        self.start = start
        self.end = end
        self.severity = severity
        self.data: Any = None

    def to_dict(self):
        ret = {
            "msg": self.msg,
            "start": self.start,
            "end": self.end,
            "severity": self.severity,
        }
        tags = getattr(self, "tags", None)
        if tags:
            ret["tags"] = tags
        if self.data is not None:
            ret["data"] = self.data
        return ret

    def __repr__(self):
        import json

        return json.dumps(self.to_dict())

    __str__ = __repr__

    def to_lsp_diagnostic(self) -> DiagnosticsTypedDict:
        tags = getattr(self, "tags", None)
        ret: DiagnosticsTypedDict = {
            "range": {
                "start": {"line": self.start[0], "character": self.start[1]},
                "end": {"line": self.end[0], "character": self.end[1]},
            },
            "severity": self.severity,
            "source": "robocorp.actions",
            "message": self.msg,
        }
        if tags:
            ret["tags"] = tags
        if self.data is not None:
            ret["data"] = self.data
        return ret


def _make_error(
    node: ast_module.AST, msg, severity=DiagnosticSeverity.Error, coldelta=0
) -> Error:
    if isinstance(node, ast_module.FunctionDef):
        return Error(
            msg,
            (node.lineno, node.col_offset + coldelta),
            (node.lineno, node.col_offset + coldelta + len(node.name)),
            severity,
        )
    else:
        return Error(
            msg,
            (node.lineno, node.col_offset + coldelta),
            (
                node.end_lineno or node.lineno,
                (node.end_col_offset or node.col_offset) + coldelta,
            ),
            severity,
        )


def _check_return_type(node: ast_module.FunctionDef) -> Iterator[Error]:
    return_type = node.returns
    if not return_type:
        yield _make_error(
            node,
            "@action without return annotation defined "
            "(`str` considered as the return type).",
            severity=DiagnosticSeverity.Warning,
            coldelta=4,
        )


def _check_return_statement(node: ast_module.FunctionDef) -> Iterator[Error]:
    for _stack, maybe_return_node in _iter_nodes(node, recursive=True):
        if isinstance(maybe_return_node, ast_module.Return):
            break
    else:
        # Return not found!
        yield _make_error(
            node,
            "@action without a `return` (an `@action` must have a return value).",
            coldelta=4,
        )


def _check_docstring_contents(
    pm: Optional[PluginManager], node: ast_module.FunctionDef, docstring: str
) -> Iterator[Error]:
    import docstring_parser
    from robocorp.tasks._commands import _is_managed_param

    assert docstring, "Expected docstring to be given."

    arguments = node.args
    contents = docstring_parser.parse(docstring)

    param_name_to_description = {}
    for docparam in contents.params:
        if docparam.description:
            param_name_to_description[docparam.arg_name] = docparam.description

    if not contents.short_description or contents.short_description.strip() == "Args:":
        yield _make_error(
            node,
            "No description found in docstring. "
            "Please update docstring to add it as an LLM needs this info "
            "to understand when to call this action.",
            coldelta=4,
        )
        return

    if contents.short_description and contents.long_description:
        doc_desc = f"{contents.short_description}\n{contents.long_description}"
    else:
        doc_desc = contents.long_description or contents.short_description or ""

    doc_desc_len = len(doc_desc)
    if doc_desc_len > 300:
        yield _make_error(
            node,
            f"Description has {doc_desc_len} chars. OpenAI just supports "
            "300 chars in the description (note: this may not be a problem "
            "in other integrations).",
            coldelta=4,
            severity=DiagnosticSeverity.Warning,
        )

    if arguments.args:
        for arg in arguments.args:
            desc = param_name_to_description.pop(arg.arg, None)
            if pm is not None and _is_managed_param(pm, arg.arg, node=node):
                continue

            if not desc:
                yield _make_error(
                    arg,
                    f"Parameter: `{arg.arg}` documentation not found in docstring. "
                    "Please update docstring to add it as an LLM needs this info "
                    "to understand what needs to be passed to call this action.",
                )

            if not arg.annotation and not arg.type_comment:
                yield _make_error(
                    arg,
                    f"Parameter: `{arg.arg}` without annotation "
                    "(considering `str` as the expected type).",
                    severity=DiagnosticSeverity.Warning,
                )


def iter_lint_errors(
    action_contents_file: str | bytes, pm: Optional[PluginManager] = None
) -> Iterator[Error]:
    ast = ast_module.parse(action_contents_file, "<string>")
    for _stack, node in _iter_nodes(ast, recursive=False):
        if isinstance(node, ast_module.FunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast_module.Name) and decorator.id == "action":
                    # We found an @action. Do the needed checks.

                    # Check for docstring
                    docstring: str = ast_module.get_docstring(node) or ""
                    if docstring:
                        docstring = docstring.strip()

                    yield from _check_return_type(node)
                    yield from _check_return_statement(node)

                    if not docstring:
                        yield _make_error(
                            node,
                            "@action docstring not found. Please define it as this is what "
                            "an LLM would use to decide whether to call this action.",
                            coldelta=4,
                        )
                    else:
                        yield from _check_docstring_contents(pm, node, docstring)


_severity_id_to_severity = {
    DiagnosticSeverity.Error: "error",
    DiagnosticSeverity.Warning: "warning",
    DiagnosticSeverity.Information: "information",
    DiagnosticSeverity.Hint: "hint",
}


@dataclass
class FormattedLintResult:
    message: str
    found_critical: bool


class LintResultTypedDict(TypedDict):
    file: str
    errors: List[DiagnosticsTypedDict]


@overload
def format_lint_results(
    lint_result: LintResultTypedDict,
) -> Optional[FormattedLintResult]:
    ...


@overload
def format_lint_results(
    lint_result: dict,
) -> Optional[FormattedLintResult]:
    ...


def format_lint_results(
    lint_result: Union[dict, LintResultTypedDict],
) -> Optional[FormattedLintResult]:
    f = lint_result.get("file")
    errors = lint_result.get("errors")
    if not isinstance(f, str) or not isinstance(errors, list):
        return None

    msg_parts = []
    msg_parts.append(f"Action lint error(s) found at file: {f}")
    msg_parts.append(
        "(note: it's possible to skip linting by passing `--skip-lint` in the command line)"
    )
    found_critical = False
    for error in errors:
        pos = error.get("range", {}).get("start", {})
        line = pos.get("line", -1)

        severity_level = error.get("severity", -1)
        if severity_level == DiagnosticSeverity.Error:
            found_critical = True

        severity_msg = _severity_id_to_severity.get(
            severity_level if severity_level is not None else -1, "Unknown severity"
        )
        message = error.get("message")
        msg_parts.append(f"{severity_msg.title()} (line {line}): {message}")

    return FormattedLintResult(
        message="\n".join(msg_parts), found_critical=found_critical
    )
