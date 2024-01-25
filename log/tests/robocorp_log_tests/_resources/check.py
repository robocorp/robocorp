from contextlib import contextmanager

from robocorp import log


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
        y = 9  # noqa
    else:
        y = 20  # noqa

    if a == 10:
        y = 30  # noqa


def check_if_exception():
    for i in range(2):
        if i == 1:
            raise RuntimeError()


def check_else_exception():
    for i in range(2):
        if i == 0:
            pass
        else:
            raise RuntimeError()


def check_if_generator():
    for a in if_generator():
        pass


def if_generator():
    a = 10
    if a < 10:
        yield 9
    else:
        yield 20

    if a == 10:
        yield 30


def call1():
    return "ret 1"


def call2():
    return 2


def check_return():
    call1()
    call2()


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
    v1 = "abcd1234_" * 10000  # noqa
    v2 = "abcde12345_" * 10000  # noqa
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

    final_matrix = matrix  # noqa


def check_for_with_continue_break():
    for i in range(6):
        if i < 2:
            continue

        if i == 5:
            break


def check_for_with_continue_break_2():
    for i in range(2):
        for j in range(2):
            if j == 0:
                break

        if i == 1:
            raise RuntimeError()


def some_call_with_exc():
    v = 10  # noqa
    raise RuntimeError("some_exc")


def check_suppress_exc_values():
    with log.suppress_variables():
        some_call_with_exc()


def check_failed_exception():
    a = 10
    assert a > 10


def check_exception_with_cause():
    try:
        raise RuntimeError("foo")
    except Exception as err:
        raise err  # This error must be shown in the trecaback in the final error.
    finally:
        raise RuntimeError("final error")


@contextmanager
def ctx():
    yield 22


def check(name, version):
    if name == 2 and version == 2:
        raise RuntimeError("foobar")


def check_with_and_for_and_yield():
    with ctx():
        for name in range(3):
            versions = range(3)
            for version in versions:
                check(name, version)


def check_dont_redact_simple():
    log.add_sensitive_variable_name("myvar")
    log.add_sensitive_variable_name("myvar2")
    log.add_sensitive_variable_name("myvar3")

    # The assign will appear redacted, but afterwards
    # printing it will appear.
    myvar = None
    myvar2 = "a"
    myvar3 = "ab"

    log.debug(None)
    log.debug("a")
    log.debug("ab")
    log.debug(myvar)
    log.debug(myvar2)
    log.debug(myvar3)


def check_dont_redact_configure():
    config = log.hide_strings_config()

    config.hide_strings.add("something")
    config.hide_strings.add("value")
    config.hide_strings.add("sss")

    config.dont_hide_strings.add("value")
    config.dont_hide_strings_smaller_or_equal_to = 3

    log.debug("something")
    log.debug("value")
    log.debug("sss")
