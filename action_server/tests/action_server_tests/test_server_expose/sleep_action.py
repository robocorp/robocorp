from robocorp.actions import action


@action
def sleep_a_while(time_to_sleep: float) -> float:
    """
    This function sleeps for a while and then returns the time when it
    finished sleeping.

    Args:
        time_to_sleep: The time to sleep.
    """
    import time

    time.sleep(time_to_sleep)
    return time.time()
