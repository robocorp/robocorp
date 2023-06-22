def _dont_log_this():
    pass


def call_another_method(param0, param1, *args, **kwargs):
    "docstring for call_another_method"
    _dont_log_this()
    assert 1 == 1


def some_method():
    call_another_method(1, "arg", ["a", "b"], c=3)
    return 22


def recurse_some_method():
    for _i in range(1000):
        some_method()


class SomeClass:
    def __init__(self, arg1, arg2):
        pass


def another(var):
    pass


def check_if():
    a = 10
    if a < 10:
        y = 9
    else:
        y = 20

    if a == 10:
        y = 30


def check_multiline():
    var = """
This is
a multiline
string
"""
    another(var)


def check_message_really_big():
    v1 = "abcd1234_" * 10000
    v2 = "abcde12345_" * 10000
    call_another_method(v1, v2)


def call_recursive_function():
    # Let some big contents in the frame...
    v1 = "abcd1234_" * 10000
    v2 = "abcde12345_" * 10000
    call_recursive_function()


def check_stack_overflow():
    try:
        call_recursive_function()
    except Exception:
        pass
    else:
        raise AssertionError("Expected stack overflow error")


def check_big_for_in_for():
    rows = 30
    cols = 30

    matrix = []
    for x in range(rows):
        row = []
        for y in range(cols):
            row.append(0)
            if (x == 27 and y == 27) or (x == 28 and y == 28):
                from robocorp import log

                with log.suppress():
                    with log._get_logger_instances() as logger_instances:
                        for robo_logger in logger_instances:
                            # Rotate output at this point
                            robo_logger._robot_output_impl._rotate_output()

        matrix.append(row)

    final_matrix = matrix
