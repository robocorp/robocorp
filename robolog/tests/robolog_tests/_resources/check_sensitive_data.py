from robocorp import robolog


def login(user_password):
    return user_password


def method(arg):
    return arg


def dont_log_args(some_arg):
    pass


def something():
    with robolog.stop_logging_variables():
        dont_log_args(some_arg="dont_log_this_arg")


def dont_log_this_method():
    pass


def run():
    password = "my_pass"
    login(password)

    with robolog.stop_logging_variables():
        s = "this should not be shown"

    robolog.hide_from_output(s)
    method(s)
    something()

    with robolog.stop_logging_methods():
        dont_log_this_method()
