# ruff: noqa: F841
from robocorp.tasks import task


def recurse_back(i):
    recurse_and_error(i)


def recurse_and_error(i=0):
    if i == 40:
        raise RuntimeError("Some error was not\nbeing expected.")
    some_local_variable = (
        """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
"""
        * 3
    )
    recurse_back(i + 1)


@task
def check_exception():
    recurse_and_error()
