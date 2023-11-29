import logging


def test_system_mutex():
    import subprocess
    import sys
    import threading
    import time
    import weakref

    import pytest
    from _pytest.outcomes import Failed

    from robocorp.action_server._robo_utils.system_mutex import (
        SystemMutex,
        _mutex_name_to_info,
        timed_acquire_mutex,
    )

    mutex_name = "mutex_name_test_system_mutex"

    system_mutex = SystemMutex(mutex_name)
    assert system_mutex.get_mutex_aquired()

    class Check2Thread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.worked = False

        def run(self):
            mutex2 = SystemMutex(mutex_name)
            assert not mutex2.get_mutex_aquired()
            self.worked = True

    t = Check2Thread()
    t.start()
    t.join()
    assert t.worked

    assert not system_mutex.disposed
    system_mutex.release_mutex()
    assert system_mutex.disposed

    mutex3 = SystemMutex(mutex_name)
    assert not mutex3.disposed
    assert mutex3.get_mutex_aquired()
    mutex3 = weakref.ref(mutex3)  # Garbage-collected

    # Calling release more times should not be an error
    system_mutex.release_mutex()

    mutex4 = SystemMutex(mutex_name)
    assert mutex4.get_mutex_aquired()

    with pytest.raises(AssertionError):
        SystemMutex("mutex/")  # Invalid name

    time_to_release_mutex = 2
    released_mutex = [False]

    def release_mutex():
        time.sleep(time_to_release_mutex)
        released_mutex[0] = True
        mutex4.release_mutex()

    t = threading.Thread(target=release_mutex)
    t.start()

    def raise_assertion_info_if_prev_acquired_not_detected(mutex_name):
        prev_system_mutex = _mutex_name_to_info.get(mutex_name)
        if prev_system_mutex is None:
            found = []
            for e in _mutex_name_to_info.items():
                found.append((f"{e[0]}: {e[1]}"))

            raise AssertionError(f"Did not find mutex name: {mutex_name} in {found}")

        raise AssertionError(
            f"Mutex info found:\n"
            f"  acquired: {system_mutex.get_mutex_aquired()}\n"
            f"  system_mutex.disposed: {system_mutex.disposed}\n"
            f"  system_mutex.thread_id: {system_mutex.thread_id}\n"
            f"  get_tid(): {threading.get_ident()}\n"
        )

    initial_time = time.time()
    with timed_acquire_mutex(
        mutex_name, check_reentrant=False, raise_error_on_timeout=True
    ):  # The current mutex will be released in a thread, so, check_reentrant=False.
        assert released_mutex[0], "Error: entered before mutex was released!"
        acquired_time = time.time()

        # At this point the lock is acquired (and it was done in this thread).
        # So, check that we get the error saying that it's not possible to get
        # a reentrant lock.
        try:
            with pytest.raises(RuntimeError) as exc:
                with timed_acquire_mutex(
                    mutex_name, timeout=1, raise_error_on_timeout=True
                ):
                    pass
        except Failed:
            raise_assertion_info_if_prev_acquired_not_detected(mutex_name)
        else:
            assert "not a reentrant mutex" in str(exc)

        # Must also fail from another process.
        code = """
from robocorp.action_server._robo_utils.system_mutex import timed_acquire_mutex
mutex_name = "mutex_name_test_system_mutex"
with timed_acquire_mutex(mutex_name, timeout=1, raise_error_on_timeout=True):
    pass
"""
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_call([sys.executable, "-c", code], stderr=subprocess.PIPE)

    assert acquired_time - initial_time > time_to_release_mutex


def test_gen_mutex_name_from_path():
    from robocorp.action_server._robo_utils.system_mutex import generate_mutex_name

    mutex_name = "my/snth\\nsth"
    mutex_name = generate_mutex_name(mutex_name, prefix="my_")
    assert mutex_name == "my_f9c932bf450ef164"


def test_system_mutex_error_on_timeout():
    import os
    import threading

    from robocorp.action_server._robo_utils.system_mutex import SystemMutex

    mutex = SystemMutex("test_system_mutex_error_on_timeout")
    assert mutex.get_mutex_aquired()
    mutex_creation_info = [""]

    def thread():
        mutex2 = SystemMutex("test_system_mutex_error_on_timeout")
        assert not mutex2.get_mutex_aquired()
        mutex_creation_info[0] = mutex2.mutex_creation_info

    t = threading.Thread(target=thread)
    t.start()
    t.join()
    info = mutex_creation_info[0]
    assert str(os.getpid()) in info
    assert 'mutex = SystemMutex("test_system_mutex_error_on_timeout")' in info


def test_system_mutex_timed_acquire_no_error_on_timeout():
    import threading

    from robocorp.action_server._robo_utils import log_custom_handler, system_mutex
    from robocorp.action_server._robo_utils.system_mutex import (
        SystemMutex,
        timed_acquire_mutex,
    )

    event_mutex_acquired = threading.Event()
    event_terminate_thread = threading.Event()

    def thread():
        mutex2 = SystemMutex("test_system_mutex_timed_acquire_no_error_on_timeout")
        assert mutex2.get_mutex_aquired()
        event_mutex_acquired.set()
        event_terminate_thread.wait()

    t = threading.Thread(target=thread)
    t.start()
    event_mutex_acquired.wait()

    mutex = SystemMutex("test_system_mutex_timed_acquire_no_error_on_timeout")
    assert not mutex.get_mutex_aquired()

    # Here we check that a message is logged instead of raising
    # an error on timeout.

    def on_log_emit(msg):
        if "acquired after 1 seconds" in f"{msg.msg % msg.args}":
            event_terminate_thread.set()

    with log_custom_handler.add_handler_callback(
        system_mutex.log, on_log_emit, level=logging.DEBUG
    ):
        with timed_acquire_mutex(
            "test_system_mutex_timed_acquire_no_error_on_timeout", timeout=1
        ):
            pass


def test_system_mutex_locked_on_subprocess():
    import subprocess
    import sys

    from devutils.fixtures import wait_for_condition

    from robocorp.action_server._robo_utils.process import kill_process_and_subprocesses
    from robocorp.action_server._robo_utils.system_mutex import SystemMutex

    code = """
import sys
import time
print('initialized')
from robocorp.action_server._robo_utils.system_mutex import SystemMutex
mutex = SystemMutex('test_system_mutex_locked_on_subprocess')
assert mutex.get_mutex_aquired()
print('acquired mutex')
sys.stdout.flush()
time.sleep(30)
"""
    p = subprocess.Popen(
        [sys.executable, "-c", code], stdout=subprocess.PIPE, stdin=subprocess.PIPE
    )
    wait_for_condition(lambda: p.stdout.readline().strip() == b"acquired mutex")
    mutex = SystemMutex("test_system_mutex_locked_on_subprocess")
    assert not mutex.get_mutex_aquired()

    # i.e.: check that we can acquire the mutex if the related process dies.
    kill_process_and_subprocesses(p.pid)

    def acquire_mutex():
        mutex = SystemMutex("test_system_mutex_locked_on_subprocess")
        return mutex.get_mutex_aquired()

    wait_for_condition(acquire_mutex, timeout=5)
