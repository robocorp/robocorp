def sub_method():
    raise RuntimeError("Fail here")


def another_method():
    sub_method()


def main():
    another_method()
