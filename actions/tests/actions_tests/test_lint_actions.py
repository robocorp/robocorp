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


def test_lint_action_big_description(data_regression):
    from robocorp.actions._lint_action import iter_lint_errors

    contents = """
@action
def my_action() -> str:
    '''
    This description is too big. OpenAI just supports 300 hundred chars in desc.
    This description is too big. OpenAI just supports 300 hundred chars in desc.
    This description is too big. OpenAI just supports 300 hundred chars in desc.
    This description is too big. OpenAI just supports 300 hundred chars in desc.
    This description is too big. OpenAI just supports 300 hundred chars in desc.
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


def test_lint_action_secret(data_regression):
    from robocorp.tasks._customization._extension_points import EPManagedParameters
    from robocorp.tasks._customization._plugin_manager import PluginManager

    from robocorp.actions._lint_action import iter_lint_errors
    from robocorp.actions._managed_parameters import ManagedParameters

    contents = """
from robocorp.actions import Secret
from robocorp import actions

@action
def my_action(my_password: Secret, another: actions.Secret) -> str:
    '''
    This is an action.
    '''
    return ''
"""

    pm = PluginManager()
    pm.set_instance(EPManagedParameters, ManagedParameters({}))
    data_regression.check(
        [x.to_lsp_diagnostic() for x in iter_lint_errors(contents, pm=pm)]
    )
