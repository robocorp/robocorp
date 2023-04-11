def sub_method(arg_name):
    raise RuntimeError("Fail here")


def another_method():
    sub_method(("arg", "name", 1))


def main():
    another_method()


# Exception while another exception was being handled:


def initial_exc():
    v0 = "in initial value"
    raise RuntimeError("initial exc")


def new_exc_while_handling_exc():
    try:
        v1 = {"1": 1, "2": 2}
        initial_exc()
    except RuntimeError:
        raise ValueError("final exc")


def call_exc_with_context():
    new_exc_while_handling_exc()
