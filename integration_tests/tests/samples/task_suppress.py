# ruff: noqa: F841
from robocorp import log
from robocorp.tasks import task


def some_method(arg):
    another = arg

    for i in range(11):
        pass


@log.suppress
def another_method():
    pass


@task
def check_case_suppress():
    some_method("initial")

    with log.suppress():
        some_method("call not shown")

    with log.suppress_variables():
        some_method("suppress variables")

    log.add_sensitive_variable_name("myvar")

    myvar = "do not show|nthsn|*trsnh*"
    some_method(myvar)

    log.hide_from_output("1")
    some_method("hiding 1")
