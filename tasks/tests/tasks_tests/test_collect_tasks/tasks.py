from robocorp.tasks import task

print("some message while collecting.")


def some_method():
    print("In some method")


@task
def main():
    """
    main method docstring
    """
    some_method()


def raise_an_error():
    raise ValueError("asd")


@task
def main_errors():
    raise_an_error()


@task
def task_with_args(my_input_arg: str, multiplier: int) -> str:
    return my_input_arg * multiplier
