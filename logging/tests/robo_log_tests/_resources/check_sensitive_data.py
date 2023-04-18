import robo_log


def login(user_password):
    return user_password


def method(arg):
    return arg


def dont_log_args(some_arg):
    pass


def something():
    with robo_log.stop_logging_variables():
        dont_log_args(some_arg="dont_log_this_arg")


def dont_log_this_method():
    pass


def run():
    password = "my_pass"
    login(password)

    with robo_log.stop_logging_variables():
        s = "this should not be shown"

    robo_log.hide_from_output(s)
    method(s)
    something()

    with robo_log.stop_logging_methods():
        dont_log_this_method()
