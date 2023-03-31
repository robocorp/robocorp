from robo import task


def some_method():
    print("In some method")


@task
def main():
    """
    main method docstring
    """
    some_method()
