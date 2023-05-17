def _dont_log_this():
    pass


def call_another_method(param0, param1, *args, **kwargs):
    "docstring for call_another_method"
    _dont_log_this()
    assert 1 == 1


def some_method():
    call_another_method(1, "arg", ["a", "b"], c=3)
    return 22
