import _thread
import ctypes
import os
import signal
import sys
import threading
import traceback
from contextlib import contextmanager
from threading import Event, Thread
from typing import Callable

from robocorp import log


def is_current_thread_main_thread():
    return threading.current_thread() is threading.main_thread()


def interrupt_main_thread() -> None:
    """
    Generates a KeyboardInterrupt in the main thread by sending a Ctrl+C
    or by calling thread.interrupt_main().

    Note: if unable to send a Ctrl+C, the KeyboardInterrupt will only be raised
    when the next Python instruction is about to be executed (so, it won't interrupt
    a sleep(1000)).
    """
    if os.name == "posix":
        # On Linux we can't interrupt 0 as in Windows because it's
        # actually owned by a process -- on the good side, signals
        # work much better on Linux!
        os.kill(os.getpid(), signal.SIGINT)

    elif os.name == "nt":
        # This generates a Ctrl+C only for the current process and not
        # to the process group!
        # Note: there doesn't seem to be any public documentation for this
        # function (although it seems to be  present from Windows Server 2003 SP1
        # onwards
        # according to: https://www.geoffchappell.com/studies/windows/win32/kernel32/api/index.htm)
        ctypes.windll.kernel32.CtrlRoutine(0)  # type:ignore

        # The code below is deprecated because it actually sends a Ctrl+C
        # to the process group, so, if this was a process created without
        # passing `CREATE_NEW_PROCESS_GROUP` the  signal may be sent to the
        # parent process and to sub-processes too (which is not ideal --
        # for instance, when using pytest-xdist, it'll actually stop the
        # testing, even when called in the subprocess).

        # if hasattr_checked(signal, 'CTRL_C_EVENT'):
        #     os.kill(0, signal.CTRL_C_EVENT)
        # else:
        #     # Python 2.6
        #     ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, 0)
    else:
        # In this case, we don't really interrupt a sleep() nor IO operations
        # (this makes the KeyboardInterrupt be sent only when the next Python
        # instruction is about to be executed).
        _thread.interrupt_main()


def create_interrupt_this_thread_callback() -> Callable[[], None]:
    """
    The idea here is returning a callback that when called will generate a
    KeyboardInterrupt in the thread that called this function.

    If this is the main thread, this means that it'll emulate a Ctrl+C (which
    may stop I/O and sleep operations).

    For other threads, this will call PyThreadState_SetAsyncExc to raise a
    KeyboardInterrupt before the next instruction (so, it won't really interrupt
    I/O or sleep operations).

    Returns:
        Returns a callback that will interrupt the current thread (this may be
        called from an auxiliary thread).
    """

    if is_current_thread_main_thread():

        def raise_on_this_thread() -> None:
            log.debug("Interrupting main thread.")
            interrupt_main_thread()

    else:
        # Note: this works in the sense that it can stop some cpu-intensive slow
        # operation, but we can't really interrupt the thread out of some sleep
        # or I/O operation (this will only be raised when Python is about to
        # execute the next instruction).
        tid = threading.get_ident()

        def raise_on_this_thread() -> None:
            log.debug("Interrupting thread: %s", tid)
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(tid), ctypes.py_object(KeyboardInterrupt)
            )

    return raise_on_this_thread


class _Timer(Thread):
    def __init__(self, timeout1, timeout2, on_timeout1, on_timeout2):
        Thread.__init__(self)
        self.timeout1 = timeout1
        self.timeout2 = timeout2
        self.on_timeout1 = on_timeout1
        self.on_timeout2 = on_timeout2
        self.finished = Event()

    def cancel(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()

    def run(self):
        if self.timeout1 > 0:
            self.finished.wait(self.timeout1)
            if not self.finished.is_set():
                self.on_timeout1()

        if self.timeout2 > 0:
            if self.timeout2 <= self.timeout1:
                self.on_timeout2()  # The time already elapsed

            else:
                timeout1 = self.timeout1
                if timeout1 < 0:
                    timeout1 = 0

                self.finished.wait(self.timeout2 - timeout1)
                if not self.finished.is_set():
                    self.on_timeout2()

        self.finished.set()


@contextmanager
def interrupt_on_timeout(
    dump_threads_timeout: float,
    interrupt_timeout: float,
    reason: str,
    arg_name_dump_threads: str,
    env_var_name_dump_threads: str,
    arg_name_interrupt: str,
    env_var_name_interrupt: str,
):
    # Disabled
    if dump_threads_timeout <= 0 and interrupt_timeout <= 0:
        yield
        return

    interrupt_thread = create_interrupt_this_thread_callback()

    def print_and_interrupt():
        dump_threads(
            message=f"""{reason} took longer than expected and will be interrupted 
(took more than {interrupt_timeout:.1f}s).
A thread dump will be shown below.
-- Configure this timeout with '{arg_name_interrupt}' argument 
or '{env_var_name_interrupt}' environment variable.
"""
        )
        interrupt_thread()

    def print_threads():
        dump_threads(
            message=f"""{reason} is taking longer than expected
(took more than {dump_threads_timeout:.1f}s).
A thread dump prior to interruption will be shown below.
-- Configure this timeout with '{arg_name_dump_threads}' argument 
or '{env_var_name_dump_threads}' environment variable.
"""
        )

    t = _Timer(
        dump_threads_timeout,
        interrupt_timeout,
        on_timeout1=print_threads,
        on_timeout2=print_and_interrupt,
    )
    t.daemon = True
    t.start()
    try:
        yield
    finally:
        t.cancel()


def dump_threads(stream=None, message="Threads found"):
    if stream is None:
        stream = sys.stderr

    thread_id_to_name = {}
    try:
        for t in threading.enumerate():
            thread_id_to_name[t.ident] = "%s  (daemon: %s)" % (t.name, t.daemon)
    except Exception:
        pass

    stack_trace = [
        "===============================================================================",
        message,
        "================================= Thread Dump =================================",
    ]

    for thread_id, stack in sys._current_frames().items():
        stack_trace.append(
            "\n-------------------------------------------------------------------------------"
        )
        stack_trace.append(" Thread %s" % thread_id_to_name.get(thread_id, thread_id))
        stack_trace.append("")

        if "self" in stack.f_locals:
            sys.stderr.write(str(stack.f_locals["self"]) + "\n")

        for filename, lineno, name, line in traceback.extract_stack(stack):
            stack_trace.append(' File "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                stack_trace.append("   %s" % (line.strip()))
    stack_trace.append(
        "\n=============================== END Thread Dump ==============================="
    )
    stream.write("\n".join(stack_trace))
