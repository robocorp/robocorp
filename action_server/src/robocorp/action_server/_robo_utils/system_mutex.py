"""
To use, create a SystemMutex, check if it was acquired (get_mutex_aquired()) and if acquired the
mutex is kept until the instance is collected or release_mutex is called.

I.e.:

    mutex = SystemMutex('my_unique_name')
    if mutex.get_mutex_aquired():
        print('acquired')
    else:
        print('not acquired')
    
    
Or to keep trying to get the mutex until a given timeout elapses:

    with timed_acquire_mutex('mutex_name'):
        # Do something without any racing condition with other processes
        ...

License: Dual-licensed under LGPL and Apache 2.0

Copyright: Brainwy Software
Author: Fabio Zadrozny
"""

import io
import logging
import re
import sys
import tempfile
import threading
import time
import traceback
import weakref
from typing import ContextManager

from .constants import NULL

log = logging.getLogger(__name__)


def check_valid_mutex_name(mutex_name):
    # To be windows/linux compatible we can't use non-valid filesystem names
    # (as on linux it's a file-based lock).

    regexp = re.compile(r'[\*\?"<>|/\\:]')
    result = regexp.findall(mutex_name)
    if result is not None and len(result) > 0:
        raise AssertionError("Mutex name is invalid: %s" % (mutex_name,))


_mutex_name_to_info: "weakref.WeakValueDictionary[str, SystemMutex]" = (
    weakref.WeakValueDictionary()
)
_lock = threading.Lock()


def get_tid():
    return threading.get_ident()  # @UndefinedVariable


def _mark_prev_acquired_in_thread(system_mutex):
    with _lock:
        _mutex_name_to_info[system_mutex.mutex_name] = system_mutex


def _verify_prev_acquired_in_thread(mutex_name):
    with _lock:
        system_mutex = _mutex_name_to_info.get(mutex_name)
        if (
            system_mutex is not None
            and system_mutex.get_mutex_aquired()
            and not system_mutex.disposed
            and system_mutex.thread_id == get_tid()
        ):
            raise RuntimeError(
                "Error: this thread has already acquired a SystemMutex(%s) and it's not a reentrant mutex (so, this would never work)!"
                % (mutex_name,)
            )


def _collect_mutex_allocation_msg(mutex_name):
    try:
        write_contents = []
        try:
            write_contents.append(f"PID: {os.getpid()}")
        except Exception:
            write_contents.append("PID: unable to get pid")

        write_contents.append("\nMutex name:")
        write_contents.append(mutex_name)

        s = io.StringIO()
        traceback.print_stack(file=s, f=sys._getframe().f_back.f_back)
        write_contents.append("\n--- Stack ---\n")
        write_contents.append(s.getvalue())
        return "\n".join(write_contents)
    except BaseException:
        try:
            return str(os.getpid())
        except Exception:
            return "<unable to get pid>"


if sys.platform == "win32":
    import os

    class SystemMutex(object):
        def __init__(
            self, mutex_name, check_reentrant=True, log_info=False, base_dir=None
        ):
            """
            :param check_reentrant:
                Should only be False if this mutex is expected to be released in
                a different thread.
            """
            if base_dir is None:
                base_dir = tempfile.gettempdir()
            os.makedirs(base_dir, exist_ok=True)
            check_valid_mutex_name(mutex_name)
            self.mutex_name = mutex_name
            self.thread_id = get_tid()
            self.mutex_creation_info = ""

            filename = os.path.join(base_dir, mutex_name)
            try:
                os.unlink(filename)
            except Exception:
                pass
            try:
                handle = os.open(filename, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                try:
                    contents = _collect_mutex_allocation_msg(mutex_name)
                    os.write(handle, contents.encode("utf-8", "replace"))
                except Exception:
                    pass  # Ignore this as it's pretty much optional
            except Exception:
                self._release_mutex = NULL
                self._acquired = False
                if check_reentrant:
                    _verify_prev_acquired_in_thread(mutex_name)

                try:
                    with open(filename) as stream:
                        self.mutex_creation_info = stream.read()
                except BaseException:
                    self.mutex_creation_info = "<unable to read>"
            else:

                def release_mutex(*args, **kwargs):
                    # Note: can't use self here!
                    if not getattr(release_mutex, "called", False):
                        release_mutex.called = True
                        try:
                            os.close(handle)
                        except Exception:
                            traceback.print_exc()
                        try:
                            # Removing is optional as we'll try to remove on startup anyways (but
                            # let's do it to keep the filesystem cleaner).
                            os.unlink(filename)
                        except Exception:
                            pass

                # Don't use __del__: this approach doesn't have as many pitfalls.
                self._ref = weakref.ref(self, release_mutex)

                self._release_mutex = release_mutex
                self._acquired = True
                _mark_prev_acquired_in_thread(self)

        @property
        def disposed(self):
            if not self._acquired:
                return True
            release_mutex = self._release_mutex
            if release_mutex is NULL:
                return True
            if getattr(release_mutex, "called", False):
                return True
            return False

        def get_mutex_aquired(self):
            return self._acquired

        def release_mutex(self):
            self._release_mutex()

else:  # Linux
    import fcntl  # @UnresolvedImport
    import os

    class SystemMutex(object):
        def __init__(
            self, mutex_name, check_reentrant=True, log_info=False, base_dir=None
        ):
            """
            :param check_reentrant:
                Should only be False if this mutex is expected to be released in
                a different thread.
            """
            from .process import is_process_alive

            if base_dir is None:
                base_dir = tempfile.gettempdir()
            os.makedirs(base_dir, exist_ok=True)
            check_valid_mutex_name(mutex_name)
            self.mutex_name = mutex_name
            self.mutex_creation_info = ""
            self.thread_id = get_tid()
            filename = os.path.join(base_dir, mutex_name)
            try:
                handle = open(filename, "a+")
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                contents = _collect_mutex_allocation_msg(mutex_name)
                handle.seek(0)
                handle.truncate()
                handle.write(contents)
                handle.flush()
            except Exception:
                self._release_mutex = NULL
                self._acquired = False
                if check_reentrant:
                    _verify_prev_acquired_in_thread(mutex_name)
                try:
                    handle.close()
                except Exception:
                    pass

                try:
                    with open(filename) as stream:
                        self.mutex_creation_info = stream.read()
                except BaseException:
                    self.mutex_creation_info = "<unable to read>"

                # It was unable to get the lock
                if log_info:
                    try:
                        try:
                            with open(filename, "r") as stream:
                                curr_pid = stream.readline().strip()[-1]
                        except BaseException:
                            log.exception("Unable to get locking pid.")
                            curr_pid = "<unable to get locking pid>"

                        try:
                            is_alive = is_process_alive(int(curr_pid))
                        except BaseException:
                            is_alive = "<unknown>"
                        log.info(
                            "Current pid holding lock: %s. Alive: %s. This pid: %s Filename: %s",
                            curr_pid,
                            is_alive,
                            os.getpid(),
                            filename,
                        )
                    except BaseException:
                        if logging.root.level <= logging.DEBUG:
                            log.exception("Error getting lock info on failure.")
            else:

                def release_mutex(*args, **kwargs):
                    # Note: can't use self here!
                    if not getattr(release_mutex, "called", False):
                        release_mutex.called = True
                        try:
                            handle.seek(0)
                            handle.truncate()
                            handle.write("Releasing lock\n")
                            handle.flush()
                        except Exception:
                            traceback.print_exc()
                        try:
                            fcntl.flock(handle, fcntl.LOCK_UN)
                        except Exception:
                            traceback.print_exc()
                        try:
                            handle.close()
                        except Exception:
                            traceback.print_exc()
                        # Don't remove it (so that it doesn't get another inode afterwards).
                        # try:
                        #     os.unlink(filename)
                        # except Exception:
                        #     pass

                # Don't use __del__: this approach doesn't have as many pitfalls.
                self._ref = weakref.ref(self, release_mutex)

                self._release_mutex = release_mutex
                self._acquired = True
                _mark_prev_acquired_in_thread(self)

        @property
        def disposed(self):
            if not self._acquired:
                return True
            release_mutex = self._release_mutex
            if release_mutex is NULL:
                return True
            if getattr(release_mutex, "called", False):
                return True
            return False

        def get_mutex_aquired(self):
            return self._acquired

        def release_mutex(self):
            self._release_mutex()


class _MutexHandle(object):
    def __init__(self, system_mutex, mutex_name):
        self._system_mutex = system_mutex
        self._mutex_name = mutex_name
        # log.info("Obtained mutex: %s in pid: %s", mutex_name, os.getpid())

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        self._system_mutex.release_mutex()
        # log.info("Released mutex: %s in pid: %s", self._mutex_name, os.getpid())


def timed_acquire_mutex(
    mutex_name,
    timeout=20,
    sleep_time=0.15,
    check_reentrant=True,
    base_dir=None,
    raise_error_on_timeout=False,
) -> ContextManager:
    """
    Acquires the mutex given its name, a number of attempts and a time to sleep between each attempt.

    :throws RuntimeError if it was not possible to get the mutex in the given time.

    To be used as:

    with timed_acquire_mutex('mutex_name'):
        # Do something without any racing condition with other processes
        ...


    :param check_reentrant:
        Should only be False if this mutex is expected to be released in
        a different thread.
    """
    finish_at = time.time() + timeout
    logged = False
    while True:
        last_attempt = time.time() >= finish_at
        mutex = SystemMutex(
            mutex_name,
            check_reentrant=check_reentrant,
            log_info=last_attempt,
            base_dir=base_dir,
        )
        if not mutex.get_mutex_aquired():
            if last_attempt:
                if not logged:
                    logged = True

                    will_retry_msg = ""
                    if not raise_error_on_timeout:
                        will_retry_msg = " (will keep trying)"

                    log.info(
                        "The mutex %s still hasn't been acquired after %s seconds%s.\nMutex info: %s",
                        mutex_name,
                        timeout,
                        will_retry_msg,
                        mutex.mutex_creation_info,
                    )
                    if raise_error_on_timeout:
                        raise RuntimeError(
                            f"Could not get mutex: {mutex_name} after: {timeout} secs."
                        )

            time.sleep(sleep_time)

            del mutex
        else:
            return _MutexHandle(mutex, mutex_name)


def generate_mutex_name(target_name, prefix=""):
    """
    A mutex name must be a valid filesystem path, so, this generates a hash
    that can be used in case the original name would have conflicts.
    """
    import hashlib

    if not isinstance(target_name, bytes):
        target_name = target_name.encode("utf-8")

    return prefix + (hashlib.sha224(target_name).hexdigest()[:16])
