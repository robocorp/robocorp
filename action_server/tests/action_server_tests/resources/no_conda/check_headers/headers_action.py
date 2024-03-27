import json

from robocorp.actions import Request, action


@action
def check_headers(request: Request, name: str, title: str = "Mr.") -> str:
    """
    Gets something from the headers.

    Args:
        name: The name of the person to greet.
        title: The title for the persor (Mr., Mrs., ...).

    Returns:
        The greeting for the person.
    """
    ret = {"headers": dict(request.headers), "cookies": dict(request.cookies)}
    return json.dumps(ret)
