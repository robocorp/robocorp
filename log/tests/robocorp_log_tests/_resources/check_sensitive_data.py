from robocorp import log


def login(user_password):
    return user_password


def method(arg):
    return arg


def dont_log_args(some_arg):
    pass


def something():
    with log.suppress_variables():
        dont_log_args(some_arg="dont_log_this_arg")


def dont_log_this_method():
    pass


@log.suppress_methods()
def dont_log_this_method2():
    pass


@log.suppress(methods=True)
def dont_log_this_method3():
    pass


@log.suppress
def dont_log_this_method4():
    pass


def run():
    password = "my_pass"
    login(password)

    with log.suppress_variables():
        s = "this should not be shown"

    log.hide_from_output(s)
    method(s)
    something()

    with log.suppress_methods():
        dont_log_this_method()

        with log.suppress_methods():
            dont_log_this_method()

    with log.suppress(methods=True):
        dont_log_this_method()

    dont_log_this_method2()
    dont_log_this_method3()
    dont_log_this_method4()


def another_func_with_exc():
    password = "my_pass"  # noqa
    raise RuntimeError("some exc in another_func_with_exc.")


def run_with_exc():
    another_func_with_exc()
