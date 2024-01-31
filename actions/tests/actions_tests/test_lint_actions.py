import os


def test_lint_action_no_docstring(data_regression):
    from robocorp.actions._lint_action import iter_lint_errors

    contents = """
@action
def my_action():
    pass
"""

    data_regression.check([x.to_lsp_diagnostic() for x in iter_lint_errors(contents)])


def test_lint_action_docstring_not_matching(data_regression):
    from robocorp.actions._lint_action import iter_lint_errors

    contents = """
@action
def my_action(param1: str) -> str:
    '''
    Empty docstring?
    '''
    return ''
"""

    data_regression.check([x.to_lsp_diagnostic() for x in iter_lint_errors(contents)])


def test_lint_action_no_description(data_regression):
    from robocorp.actions._lint_action import iter_lint_errors

    contents = """
@action
def my_action(param1) -> str:
    '''
    Args:
        param1: Some value.
    '''
    return ''
"""

    data_regression.check([x.to_lsp_diagnostic() for x in iter_lint_errors(contents)])


def test_lint_action_argument_untyped(data_regression):
    from robocorp.actions._lint_action import iter_lint_errors

    contents = """
@action
def my_action(param1) -> str:
    '''
    Some Action.
    
    Args:
        param1: Some value.
    '''
    return ''
"""

    data_regression.check([x.to_lsp_diagnostic() for x in iter_lint_errors(contents)])


def test_lint_action_integrated(datadir, data_regression):
    import json

    from devutils.fixtures import robocorp_actions_run

    result = robocorp_actions_run(["list"], returncode="error", cwd=str(datadir))
    try:
        found = json.loads(result.stdout)
    except Exception:
        raise RuntimeError(
            f"stdout: {result.stdout.decode('utf-8')}\nstderr: {result.stderr.decode('utf-8')}"
        )

    lint_result = found["lint_result"]
    new_dict = {}
    for k, v in lint_result.items():
        if k == "file":
            new_dict[k] = os.path.basename(v)
        else:
            new_dict[k] = v

    data_regression.check(new_dict)
