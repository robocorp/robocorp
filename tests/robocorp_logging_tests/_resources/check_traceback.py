def sub_method(arg_name):
    raise RuntimeError("Fail here")


def another_method():
    sub_method(("arg", "name", 1))


def main():
    another_method()
