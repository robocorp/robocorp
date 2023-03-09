def call_another_method(param0, param1, *args, **kwargs):
    assert 1 == 1


def some_method():
    call_another_method(1, "arg", ["a", "b"], c=3)
    return 22


class SomeClass:
    def __init__(self, arg1, arg2):
        pass
