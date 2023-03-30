from robo import task


def some_method():
    print("In some method")


@task
def main():
    some_method()
