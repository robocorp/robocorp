from robocorp import log


def login(user_password):
    return user_password


def method(arg):
    return arg


def dont_log_args(some_arg):
    pass


def something():
    with log.stop_logging_variables():
        dont_log_args(some_arg="dont_log_this_arg")


def dont_log_this_method():
    pass


def run():
    password = "my_pass"
    login(password)

    with log.stop_logging_variables():
        s = "this should not be shown"

    log.hide_from_output(s)
    method(s)
    something()

    with log.stop_logging_methods():
        dont_log_this_method()
