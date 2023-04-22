from robocorp.tasks import task


def some_sub_method():
    print("In some sub method")


@task
def sub():
    some_sub_method()
