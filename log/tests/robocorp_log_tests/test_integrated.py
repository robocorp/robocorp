from importlib import reload
from pathlib import Path

import pytest
from robocorp_log_tests._resources import check, check_iterators
from robocorp_log_tests.fixtures import (
    AutoLogConfigForTest,
    basic_log_setup,
    pretty_format_logs_from_log_html,
)

from robocorp.log import setup_log, verify_log_messages_from_log_html


@pytest.fixture(autouse=True)
def _reset_hide_strings_config():
    from robocorp.log import hide_strings_config

    config = hide_strings_config()
    config.hide_strings.clear()
    config.dont_hide_strings_smaller_or_equal_to = 2
    config.dont_hide_strings.clear()
    config.dont_hide_strings.update(("None", "True", "False"))


def test_log_with_yield_iterator(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).main()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))


def test_log_with_yield_iterator_augassign(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).main_yield_augassign()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))


def test_log_with_yield_and_for(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).for_and_yield()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))


def test_log_with_yield_and_for_1(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).for_and_yield(1)

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))


def test_log_with_yield_and_for_5(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).for_and_yield(5)

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))


def test_log_with_yield_from_iterator(tmpdir, ui_regenerate):
    from robocorp.log._decoder import (
        MESSAGE_TYPE_YIELD_FROM_RESUME,
        MESSAGE_TYPE_YIELD_FROM_SUSPEND,
    )

    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).main_yield_from()

    log_target = setup_info.log_target
    assert log_target.exists()
    verify_log_messages_from_log_html(
        log_target,
        [
            {
                "message_type": MESSAGE_TYPE_YIELD_FROM_SUSPEND,
                "name": "yield_from",
                "libname": "robocorp_log_tests._resources.check_iterators",
            },
            {
                "message_type": MESSAGE_TYPE_YIELD_FROM_RESUME,
                "name": "yield_from",
                "libname": "robocorp_log_tests._resources.check_iterators",
            },
        ],
    )
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_log_with_for_loop(tmpdir, ui_regenerate):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).for_iter()

    log_target = setup_info.log_target
    assert log_target.exists()
    verify_log_messages_from_log_html(
        log_target,
        [
            {"message_type": "SE", "name": "for i in range(5)", "type": "FOR"},
            {"message_type": "EE", "type": "FOR", "status": "PASS"},
            {
                "message_type": "SE",
                "name": "Step: for i in range(5)",
                "type": "FOR_STEP",
            },
            {"message_type": "EA", "name": "i", "type": "int", "value": "2"},
            {
                "message_type": "AS",
                "name": "for_iter",
                "target": "a",
                "type": "int",
                "value": "2",
            },
            {"message_type": "EE", "type": "FOR_STEP", "status": "PASS"},
        ],
    )
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_log_with_for_loop_and_exception(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        try:
            reload(check_iterators).for_iter_exc()
        except RuntimeError:
            pass
        else:
            raise AssertionError("Expected RuntimeError.")

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_log_with_for_loop_and_early_return(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).for_early_return()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_log_with_for_loop_multiple_targets(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).for_iter_multiple_targets()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_log_with_while_loop(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).while_loop_multiple_targets()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_log_with_for_loop_and_exception_inside_for(
    tmpdir, ui_regenerate, str_regression
):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check_iterators).for_with_exception()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_exception_suppress_variables(tmpdir, ui_regenerate, str_regression):
    __tracebackhide__ = 1
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        try:
            reload(check).check_suppress_exc_values()
        except RuntimeError:
            pass
        else:
            raise AssertionError("Expected RuntimeError")

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(
        pretty_format_logs_from_log_html(log_target, show_exception_vars=True)
    )
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_dont_redact_simple(tmpdir, ui_regenerate, str_regression):
    __tracebackhide__ = 1
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check).check_dont_redact_simple()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(
        pretty_format_logs_from_log_html(log_target, show_log_messages=True)
    )
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_dont_redact_configure(tmpdir, ui_regenerate, str_regression):
    __tracebackhide__ = 1
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check).check_dont_redact_configure()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(
        pretty_format_logs_from_log_html(log_target, show_log_messages=True)
    )
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_log_multiline_str(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check).check_multiline()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_log_with_and_for_and_yield(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        with pytest.raises(RuntimeError):
            reload(check).check_with_and_for_and_yield()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_log_if_stmt(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check).check_if()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_log_if_stmt_with_exception(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        with pytest.raises(RuntimeError):
            reload(check).check_if_exception()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_log_else_stmt_with_exception(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        with pytest.raises(RuntimeError):
            reload(check).check_else_exception()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_log_if_stmt_generator(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check).check_if_generator()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_log_return(tmpdir, ui_regenerate, str_regression):
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check).check_return()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_limits_and_corner_cases(tmpdir, ui_regenerate, str_regression) -> None:
    """
    This tests checks limits for messages and checks that the logging
    still behaves properly on corner cases (such as when a message would
    be greater than the max log size).
    """

    config = AutoLogConfigForTest()

    with setup_log(max_value_repr_size="50kb"):
        with basic_log_setup(
            tmpdir, config=config, max_file_size="10kb", max_files=2
        ) as setup_info:
            reload(check).check_message_really_big()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    files = list(log_target.parent.glob("*.robolog"))
    assert len(files) == 1
    f: Path = files[0]

    # i.e.: the file has more than 100kb because of the min_messages_per_file.
    assert f.stat().st_size > 100_000
    # setup_info.open_log_target()


def _test_stack_overflow_error(tmpdir, ui_regenerate, str_regression):
    """
    This test checks the stack overflow case (disabled for now).
    """

    config = AutoLogConfigForTest()
    with basic_log_setup(
        tmpdir, config=config, max_file_size="100kb", max_files=2
    ) as setup_info:
        reload(check).check_stack_overflow()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_partial_logs(tmpdir, ui_regenerate, str_regression) -> None:
    """ """

    config = AutoLogConfigForTest()

    with setup_log(max_value_repr_size="100kb"):
        with basic_log_setup(
            tmpdir, config=config, max_file_size="10MB", max_files=2
        ) as setup_info:
            reload(check).check_big_for_in_for()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    files = list(log_target.parent.glob("*.robolog"))
    assert len(files) == 2

    # setup_info.open_log_target()


def test_assertion_failed_error(tmpdir, ui_regenerate, str_regression):
    __tracebackhide__ = 1
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        try:
            reload(check).check_failed_exception()
        except AssertionError:
            pass
        else:
            raise AssertionError("Expected AssertionError")

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(
        pretty_format_logs_from_log_html(log_target, show_exception_vars=True)
    )


def test_for_with_continue_break(tmpdir, ui_regenerate, str_regression):
    __tracebackhide__ = 1
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        reload(check).check_for_with_continue_break()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_for_with_continue_break_2(tmpdir, ui_regenerate, str_regression):
    __tracebackhide__ = 1
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        with pytest.raises(RuntimeError):
            reload(check).check_for_with_continue_break_2()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(pretty_format_logs_from_log_html(log_target))
    # setup_info.open_log_target()


def test_exception_with_cause(tmpdir, ui_regenerate, str_regression):
    __tracebackhide__ = 1
    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        with pytest.raises(RuntimeError):
            reload(check).check_exception_with_cause()

    log_target = setup_info.log_target
    assert log_target.exists()
    str_regression.check(
        pretty_format_logs_from_log_html(log_target, show_exception_vars=True)
    )
