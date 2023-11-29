from robocorp.actions import (
    IAction,
    action,
    action_cache,
    session_cache,
    setup,
    teardown,
)


@setup
def before_greet(action: IAction):
    print("before", action.name)


@teardown(scope="action")
def after_greet(action: IAction):
    print("after", action.name)


@session_cache
def my_cached_session():
    print("my_cached_session called")
    return 0


@action_cache
def my_cached_action():
    print("my_cached_action before")
    yield 1
    print("my_cached_action after")


@action
def greet(name: str, title="Mr.") -> str:
    """
    Provides a greeting for a person.

    Args:
        name: The name of the person to greet.
        title: The title for the persor (Mr., Mrs., ...).

    Returns:
        The greeting for the person.
    """
    assert my_cached_session() == 0
    assert my_cached_action() == 1
    return f"Hello {title} {name}."
