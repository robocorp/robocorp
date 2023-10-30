"""
Python has a syntax limit where at most 20 blocks can be nested.

A try..except..finally block actually consumes 2 blocks.

Initially the basic structure used changed code as:

def func():
  for a in b:
    print(a)

To the code below:

def func():
  try:
    report_method_start()
    try:
      report_for_start()
      for a in b:
        try:
          report_for_step_start()
          print(a)
        except Exception:
          report_for_step_error()
        finally:
          report_for_step_exit()
    except Exception:
      report_for_error()
    finally:
      report_for_exit()
  except Exception:
    report_method_exception()
  finally:
    report_method_exit()

Unfortunately, in this structure the limit for python blocks is reached too
soon (user code in a 3-level for loop in a try..except..finally would already
reach it and it's not such an exceptional use-case).

So, these tests use a different alternative where try..except is not added
to the code but where exceptions can still be detected by rewriting user
try..except as well as leveraging a main `with` statement in the method.
"""

import pytest

from robocorp.log._lifecycle_hooks import MethodLifecycleContext


@pytest.fixture
def in_memory_log():
    from io import StringIO

    from robocorp import log
    from robocorp.log import setup_auto_logging

    s = StringIO()

    def on_write(msg):
        s.write(msg)

    with setup_auto_logging():
        with log.add_in_memory_log_output(
            on_write,
        ):
            yield s


def test_rewrite_strategy_simple_for_iter(in_memory_log, str_regression):
    from robocorp_log_tests.fixtures import pretty_format_logs_from_stream

    def user_method():
        with MethodLifecycleContext(
            ("METHOD", __name__, "filename", "user_method", 1, {})
        ) as ctx:
            ctx.report_for_start(
                1, ("FOR", __name__, "filename", "for a in range(2)", 2)
            )
            for a in range(2):
                ctx.report_for_step_start(
                    2,
                    (
                        "FOR_STEP",
                        __name__,
                        "filename",
                        "for a in range(2)",
                        3,
                        [("a", a)],
                    ),
                )
                pass
                ctx.report_for_step_end(2)
            ctx.report_for_end(1)

    user_method()
    in_memory_log.seek(0)
    contents = pretty_format_logs_from_stream(in_memory_log)
    # print(contents)
    str_regression.check(contents)


def test_rewrite_strategy_simple_for_iter_if_continue(in_memory_log, str_regression):
    from robocorp_log_tests.fixtures import pretty_format_logs_from_stream

    def user_method():
        with MethodLifecycleContext(
            ("METHOD", __name__, "filename", "user_method", 1, {})
        ) as ctx:
            ctx.report_for_start(
                1, ("FOR", __name__, "filename", "for a in range(2)", 2)
            )
            for a in range(2):
                ctx.report_for_step_start(
                    2,
                    (
                        "FOR_STEP",
                        __name__,
                        "filename",
                        "for a in range(2)",
                        3,
                        [("a", a)],
                    ),
                )
                if True:
                    ctx.report_if_start(
                        3,
                        (
                            "IF_SCOPE",
                            __name__,
                            "filename",
                            "if True",
                            4,
                            [],
                        ),
                    )
                    continue
                    # The if end will never be reported...
                    # ctx.report_for_if_end(3)

                ctx.report_for_step_end(2)
            ctx.report_for_end(1)

    user_method()
    in_memory_log.seek(0)
    contents = pretty_format_logs_from_stream(in_memory_log)
    # print(contents)
    str_regression.check(contents)


def test_rewrite_strategy_for_iter_exception(in_memory_log, str_regression):
    from robocorp_log_tests.fixtures import pretty_format_logs_from_stream

    def user_method():
        with MethodLifecycleContext(
            ("METHOD", __name__, "filename", "user_method", 1, {})
        ) as ctx:
            ctx.report_for_start(
                1, ("FOR", __name__, "filename", "for a in range(2)", 2)
            )
            for a in range(2):
                ctx.report_for_step_start(
                    2,
                    (
                        "FOR_STEP",
                        __name__,
                        "filename",
                        "for a in range(2)",
                        3,
                        [("a", a)],
                    ),
                )
                raise RuntimeError("err")
                ctx.report_for_step_end(2)
            ctx.report_for_end(1)

    with pytest.raises(RuntimeError):
        user_method()
    in_memory_log.seek(0)
    contents = pretty_format_logs_from_stream(in_memory_log)
    # print(contents)
    str_regression.check(contents)


def test_rewrite_strategy_for_iter_exception_and_try(in_memory_log, str_regression):
    from robocorp_log_tests.fixtures import pretty_format_logs_from_stream

    def user_method():
        with MethodLifecycleContext(
            ("METHOD", __name__, "filename", "user_method", 1, {})
        ) as ctx:
            try:
                ctx.report_for_start(
                    1, ("FOR", __name__, "filename", "for a in range(2)", 2)
                )
                for a in range(2):
                    ctx.report_for_step_start(
                        2,
                        (
                            "FOR_STEP",
                            __name__,
                            "filename",
                            "for a in range(2)",
                            3,
                            [("a", a)],
                        ),
                    )
                    raise RuntimeError("err")
                    ctx.report_for_step_end(2)
                ctx.report_for_end(1)
            except Exception:
                ctx.report_exception((1, 2))

    user_method()
    in_memory_log.seek(0)
    contents = pretty_format_logs_from_stream(in_memory_log)
    str_regression.check(contents)
