import threading
import time

from robocorp.tasks._interrupts import (
    create_interrupt_this_thread_callback,
    interrupt_main_thread,
)


def test_interrupt_main_thread():
    def interrupt():
        # sleep here so that the main thread in the test can get to the sleep
        # too (otherwise if we interrupt too fast we won't really check that the
        # sleep itself got interrupted -- although if that happens on some tests
        # runs it's not really an issue either).
        time.sleep(1)
        interrupt_main_thread()

    timeout = 20
    initial_time = time.time()
    try:
        t = threading.Thread(target=interrupt)
        t.start()
        time.sleep(timeout)
    except KeyboardInterrupt:
        actual_timeout = time.time() - initial_time
        # If this fails it means that although we interrupted Python actually
        # waited for the next instruction to send the event and didn't really
        # interrupt the thread.
        assert actual_timeout < timeout, (
            "Expected the actual timeout (%s) to be < than the timeout (%s)"
            % (
                actual_timeout,
                timeout,
            )
        )
    else:
        raise AssertionError("KeyboardInterrupt not generated in main thread.")


def test_create_interrupt_this_thread_callback():
    from devutils.fixtures import wait_for_condition

    class MyThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.finished = False
            self.daemon = True
            self.interrupt_thread = None
            self.interrupted = False

        def run(self):
            try:
                self.interrupt_thread = create_interrupt_this_thread_callback()
                while True:
                    time.sleep(0.2)
            except KeyboardInterrupt:
                self.interrupted = True
            finally:
                self.finished = True

    t = MyThread()
    t.start()
    wait_for_condition(lambda: t.interrupt_thread is not None)

    t.interrupt_thread()

    wait_for_condition(lambda: t.finished)

    assert t.interrupted
