import json
import os
import sys
import traceback
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from threading import RLock
from typing import IO, Any, AnyStr, Iterable, Iterator

from robocorp.log import console_message


class _IORedirector(IO[str]):
    """
    This class works to wrap a stream (stdout/stderr) with an additional redirect.
    """

    def __init__(self, original, stream_name, wrap_buffer=False):
        """
        :param stream original:
            The stream to be wrapped (usually stdout/stderr, but could be None).

        :param bool wrap_buffer:
            Whether to create a buffer attribute (needed to mimick python 3 s
            tdout/stderr which has a buffer to write binary data).
        """
        self.stream_name = stream_name
        self.encoding = os.environ.get("PYTHONIOENCODING", "utf-8")

        self._lock = RLock()
        self._writing = False
        self._original = original
        if wrap_buffer and hasattr(original, "buffer"):
            self.buffer = _IORedirector(original.buffer, False)

    @property
    def mode(self):
        return self._original.mode

    @property
    def name(self):
        return self._original.name

    def close(self):
        return self._original.close()

    @property
    def closed(self):
        return self._original.closed

    def fileno(self):
        return self._original.fileno()

    def flush(self):
        return self._original.flush()

    def isatty(self):
        return self._original.isatty()

    def read(self, *args, **kwargs):
        return self._original.read(*args, **kwargs)

    def readable(self):
        return self._original.readable()

    def readline(self, *args, **kwargs):
        return self._original.readline(*args, **kwargs)

    def readlines(self, *args, **kwargs):
        return self._original.readlines(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._original.seek(*args, **kwargs)

    def seekable(self):
        return self._original.seekable()

    def tell(self):
        return self._original.tell()

    def truncate(self, *args, **kwargs):
        return self._original.truncate(*args, **kwargs)

    def writable(self):
        return self._original.writable()

    def writelines(self, lines: Iterable[AnyStr]):
        return self._original.writelines(lines)

    def __next__(self):
        return self._original.__next__()

    def __iter__(self):
        return self._original.__iter__()

    def __enter__(self):
        return self._original.__enter__()

    def __exit__(self, *args, **kwargs):
        return self._original.__exit__(*args, **kwargs)

    def __getattr__(self, name):
        # catch-all
        return getattr(self._original, name)

    def write(self, s):
        # Note that writing to the original stream may fail for some reasons
        # (such as trying to write something that's not a string or having it closed).
        with self._lock:
            if self._writing:
                return
            self._writing = True
            try:
                try:
                    self._original.write(s)
                finally:
                    if isinstance(s, bytes):
                        s = s.decode(self.encoding, errors="replace")

                    # We've just written to the stream, so, don't write again.
                    console_message(s, self.stream_name, stream=None, flush=False)
            finally:
                self._writing = False


@contextmanager
def _redirect_writes_to_console_messages(
    mode: str, redirect_to_console_messages: bool = True
) -> Iterator[None]:
    stdout_redirector = _IORedirector(sys.stdout, "stdout", wrap_buffer=True)
    stderr_redirector = _IORedirector(sys.stderr, "stderr", wrap_buffer=True)

    with redirect_stdout(stdout_redirector), redirect_stderr(stderr_redirector):
        yield


@contextmanager
def setup_stdout_logging(
    mode: str, redirect_to_console_messages: bool = True
) -> Iterator[None]:
    """
    This function is responsible for setting up the needed stdout/stderr
    redirections (usually managed from robocorp-tasks).

    The redirections needed are:
        - Redirect stdout and stderr to `console_messages` if
          redirect_to_console_messages is True (while still printing to
          the original streams).
        - Write all the messages to the stdout if the mode is "json" or if
          the mode is "" and the "RC_LOG_OUTPUT_STDOUT" is set to
          one of ("1", "t", "true", "json").

    Args:
        mode:
            "": query the RC_LOG_OUTPUT_STDOUT value.
            "no": don't provide log output to the stdout.
            "json": provide json output to the stdout.

        redirect_to_console_messages:
            Whether messages sent to stdout and stderr should be
            redirected to console messages.
    """
    import threading

    from robocorp import log
    from robocorp.log import console

    if not mode:
        rc_log_output_stdout = os.environ.get("RC_LOG_OUTPUT_STDOUT", "").lower()
        if rc_log_output_stdout in ("1", "t", "true", "json"):
            mode = "json"

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        if mode == "json":
            # If we'll be redirecting the output to json we should not use any
            # colors.
            sys.stdout = sys.stderr
            console.set_mode("plain")

        with _redirect_writes_to_console_messages(mode, redirect_to_console_messages):
            if mode == "json":
                from robocorp.log._decoder import Decoder

                decoder = Decoder()

                import queue

                q: "queue.Queue[Any]" = queue.Queue()

                EXIT = object()

                def in_thread():
                    while True:
                        msg = q.get(block=True)
                        if msg is EXIT:
                            return

                        try:
                            line = msg.strip()
                            if line:
                                message_type, message = line.split(" ", 1)
                                decoded = decoder.decode_message_type(
                                    message_type, message
                                )
                                if decoded:
                                    decoded = json.dumps(decoded)
                                    if len(decoded) > 1024:
                                        i = 0
                                        while True:
                                            buf = decoded[i : i + 1024]
                                            if not buf:
                                                break
                                            i += 1024
                                            original_stdout.write(f"{buf}")
                                            original_stdout.flush()
                                        original_stdout.write("\n")
                                    else:
                                        original_stdout.write(f"{decoded}\n")
                                    # Flush (so, clients don't need to execute as unbuffered).
                                    original_stdout.flush()
                        except:
                            traceback.print_exc(file=sys.stderr)

                # Note: not daemon, we want all messages to be sent prior to exiting.
                threading.Thread(
                    target=in_thread, daemon=False, name="RoboLogInMemoryOutput"
                ).start()

                def write(msg):
                    q.put(msg)

                with log.add_in_memory_log_output(write):
                    try:
                        yield
                    finally:
                        q.put(EXIT)

            else:
                yield  # Nothing to do but respect the contextmanager.
    finally:
        sys.stdout = original_stdout
