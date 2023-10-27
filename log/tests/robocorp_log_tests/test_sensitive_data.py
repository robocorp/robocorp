from contextlib import contextmanager

from robocorp import log as robolog


def test_sensitive_data():
    from importlib import reload
    from io import StringIO

    from robocorp_log_tests._resources import check_sensitive_data

    from robocorp.log import iter_decoded_log_format_from_stream

    s = StringIO()

    def write(msg):
        s.write(msg)

    with robolog.setup_auto_logging():
        check_sensitive_data = reload(check_sensitive_data)

        with robolog.add_in_memory_log_output(write):
            check_sensitive_data.run()

    assert "my_pass" not in s.getvalue()
    assert "this should not be shown" not in s.getvalue()
    assert "dont_log_this_arg" not in s.getvalue()
    assert "dont_log_this_method" not in s.getvalue()

    s.seek(0)

    found = []
    for v in iter_decoded_log_format_from_stream(s):
        if v["message_type"] == "EA":
            found.append(v)

    assert found == [
        {
            "message_type": "EA",
            "name": "user_password",
            "type": "str",
            "value": "<redacted>",
        },
        {"message_type": "EA", "name": "arg", "type": "str", "value": "'<redacted>'"},
    ]


def test_sensitive_data_in_traceback():
    from importlib import reload
    from io import StringIO

    from robocorp_log_tests._resources import check_sensitive_data

    from robocorp.log import verify_log_messages_from_stream

    s = StringIO()

    def write(msg):
        s.write(msg)

    with robolog.setup_auto_logging():
        check_sensitive_data = reload(check_sensitive_data)

        with robolog.add_in_memory_log_output(write):
            try:
                check_sensitive_data.run_with_exc()
            except Exception:
                robolog.exception()

    assert "my_pass" not in s.getvalue()

    s.seek(0)

    verify_log_messages_from_stream(
        s,
        [
            {
                "message_type": "TBV",
                "name": "password",
                "type": "str",
                "value": "<redacted>",
            }
        ],
    )


def test_func_or_dec_suppress_handler():
    outer_var = []

    @contextmanager
    def ctx(variables=True, methods=True):
        msg = "start"
        if variables:
            msg += "_v"
        if methods:
            msg += "_m"
        outer_var.append(msg)
        yield
        outer_var.append("stop")

    def suppress(*args, **kwargs):
        from robocorp.log._suppress_helper import SuppressHelper

        helper = SuppressHelper(ctx)
        return helper.handle(*args, **kwargs)

    @suppress
    def some_func():
        outer_var.append("inside")

    some_func()
    assert outer_var == ["start_v_m", "inside", "stop"]
    del outer_var[:]

    with suppress(variables=False):
        outer_var.append("with")
    assert outer_var == ["start_m", "with", "stop"]
    del outer_var[:]

    @suppress(methods=False)
    def another_func(y):
        outer_var.append("args")

    another_func(y=22)
    assert outer_var == ["start_v", "args", "stop"]
