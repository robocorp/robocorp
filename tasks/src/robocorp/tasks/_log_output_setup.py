import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional


def setup_log_output(
    output_dir: Path,
    max_file_size: str = "1MB",
    max_files: int = 5,
    log_name: str = "log.html",
):
    from robocorp import log

    # This can be called after user code is imported (but still prior to its
    # execution).
    return log.add_log_output(
        output_dir=output_dir,
        max_file_size=max_file_size,
        max_files=max_files,
        log_html=output_dir / log_name,
    )


class _LogErrorLock:
    tlocal = threading.local()


@contextmanager
def setup_log_output_to_port() -> Iterator[None]:
    port_in_env: Optional[str] = os.environ.get("ROBOCORP_TASKS_LOG_LISTENER_PORT")
    if not port_in_env:
        yield
        return

    from robocorp import log

    try:
        port = int(port_in_env)
    except Exception:
        log.critical(
            f"ROBOCORP_TASKS_LOG_LISTENER_PORT set to a non-int value: {port_in_env}"
        )
        yield
        return

    try:
        import socket

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("localhost", port))
    except Exception:
        log.exception(
            f"Error connecting to ROBOCORP_TASKS_LOG_LISTENER_PORT ({port_in_env})."
        )
        yield
        return

    def write(msg: str):
        try:
            client_socket.send(msg.encode("utf-8"))
        except Exception:
            try:
                writing = _LogErrorLock.tlocal._writing
            except Exception:
                writing = _LogErrorLock.tlocal._writing = False

            if writing:
                # Prevent recursing printing errors.
                return

            _LogErrorLock.tlocal._writing = True
            try:
                log.exception(
                    f"Error sending data to ROBOCORP_TASKS_LOG_LISTENER_PORT ({port_in_env})."
                )
            finally:
                _LogErrorLock.tlocal._writing = False

    with log.add_in_memory_log_output(write):
        yield

    try:
        client_socket.close()
    except Exception:
        pass
