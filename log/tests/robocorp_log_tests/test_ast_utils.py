import ast


def test_ast_utils_is_generator():
    from robocorp.log import _ast_utils

    tree = ast.parse(
        """
def method():
    def methodinternal():
        yield 1
"""
    )

    functions = list(
        _ast_utils.iter_nodes(
            tree, accept=lambda node: isinstance(node, ast.FunctionDef)
        )
    )
    function1, function2 = functions
    assert not _ast_utils._compute_is_generator(function1)
    assert _ast_utils._compute_is_generator(function2)


def test_ast_utils_iter_nodes():
    from robocorp.log import _ast_utils

    tree = ast.parse(
        """
def method():
    def methodinternal():
        pass
"""
    )

    func_def = None

    def accept(node):
        if not isinstance(node, ast.AST):
            return False
        if not isinstance(node, ast.FunctionDef):
            return True

        nonlocal func_def
        if func_def is None:
            func_def = node
            return True
        return False

    nodes = list(x.__class__.__name__ for x in _ast_utils.iter_nodes(tree))
    assert nodes == ["FunctionDef", "arguments", "FunctionDef", "arguments", "Pass"]
    nodes = list(
        x.__class__.__name__ for x in _ast_utils.iter_nodes(tree, accept=accept)
    )
    assert nodes == ["FunctionDef", "arguments"]

    func_def = next(_ast_utils.iter_nodes(tree))
    nodes = list(x.__class__.__name__ for x in _ast_utils.iter_nodes(func_def))
    assert nodes == ["arguments", "FunctionDef", "arguments", "Pass"]

    nodes = list(
        x.__class__.__name__ for x in _ast_utils.iter_nodes(func_def, accept=accept)
    )
    assert nodes == ["arguments"]
