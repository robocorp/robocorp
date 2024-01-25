def sub_method(arg_name):
    raise RuntimeError("Fail here")


def another_method():
    sub_method(("arg", "name", 1))


def main():
    another_method()


# Exception while another exception was being handled:


def initial_exc():
    initial0 = "in initial value"  # noqa
    initial1 = "another var"  # noqa
    raise RuntimeError("initial exc")


def new_exc_while_handling_exc():
    try:
        another0 = {"1": 1, "2": 2}  # noqa
        bar = ["aabb"] * 80  # noqa
        initial_exc()
    except RuntimeError:
        raise ValueError("final exc")


def call_exc_with_context():
    new_exc_while_handling_exc()
