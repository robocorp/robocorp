from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import traceback


def setup_log_output(
    output_dir: Path,
    max_file_size: str = "1MB",
    max_files: int = 5,
    log_name: str = "log.html",
):
    from robocorp import robolog

    # This can be called after user code is imported (but still prior to its
    # execution).
    return robolog.add_log_output(
        output_dir=output_dir,
        max_file_size=max_file_size,
        max_files=max_files,
        log_html=output_dir / log_name,
    )


@contextmanager
def setup_stdout_logging():
    from robocorp import robolog
    import threading

    if os.environ.get("RC_LOG_OUTPUT_STDOUT", "").lower() in ("1", "t", "true"):
        original_stdout = sys.stdout

        # Keep printing anything the user provides to the stderr for now.
        # TODO: provide messages given to stdout as expected messages in the output?
        sys.stdout = sys.stderr

        from robocorp.robolog._decoder import Decoder

        decoder = Decoder()

        import queue

        q = queue.Queue()

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
                        decoded = decoder.decode_message_type(message_type, message)
                        if decoded:
                            original_stdout.write(f"{json.dumps(decoded)}\n")
                            # Flush (so, clients don't need to execute as unbuffered).
                            original_stdout.flush()
                except:
                    traceback.print_exc(file=sys.stderr)

        # Note: not daemon, we want all messages to be sent prior to exiting.
        threading.Thread(
            target=in_thread, daemon=False, name="RoboLogStdoutThread"
        ).start()

        def write(msg):
            q.put(msg)

        with robolog.add_in_memory_log_output(write):
            try:
                yield
            finally:
                q.put(EXIT)
                sys.stdout = original_stdout

    else:
        yield  # Nothing to do but respect the contextmanager.
