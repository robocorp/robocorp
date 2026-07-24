import time

import pytest


def test_wait_for_condition_respects_custom_timeout():
    from robocorp.windows import wait_for_condition

    start = time.monotonic()
    with pytest.raises(TimeoutError):
        wait_for_condition(lambda: False, timeout=0.2)
    elapsed = time.monotonic() - start

    # Regression test for #448: `timeout` used to be silently overwritten with
    # the hardcoded default of 8 seconds.
    assert elapsed < 1.0


def test_wait_for_condition_default_timeout_still_succeeds():
    from robocorp.windows import wait_for_condition

    wait_for_condition(lambda: True)
