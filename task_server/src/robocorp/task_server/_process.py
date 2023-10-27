from __future__ import annotations

import logging
import os
import platform
import subprocess
import traceback
from itertools import count
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
from typing import IO, Any, Callable, NamedTuple, Optional, TypeVar, Union

T = TypeVar("T")
PathLike = Union[str, Path]
Listener = Callable[[str], Any]

LOGGER = logging.getLogger(__name__)
IS_WINDOWS = platform.system() == "Windows"


def daemonize(target, *args):
    thread = Thread(target=target, args=args)
    thread.daemon = True
    thread.start()
    return thread


def exhaust(queue: Queue[T]) -> list[T]:
    output = []
    try:
        while True:
            event = queue.get_nowait()
            output.append(event)
    except Empty:
        return output


class Reader(NamedTuple):
    file: IO[str]
    thread: Thread
    queue: Queue[str]
    close: Event


class ProcessError(RuntimeError):
    def __init__(self, returncode, stderr) -> None:
        super().__init__()
        self.returncode: int = int(returncode)
        self.stderr: list[str] = stderr

    def __str__(self):
        name = self.__class__.__name__
        lines = "\\n".join(line for line in self.stderr)
        return f"{name}[returncode={self.returncode},stderr='{lines}']"


class Process:
    _UID = count(1)

    def __init__(
        self,
        args: list[str],
        cwd: Optional[PathLike] = None,
        env: Optional[dict[str, str]] = None,
    ):
        self._args = args
        self._cwd = cwd or Path.cwd()
        self._env = {**os.environ, **(env or {})}
        self._listeners: list[Listener] = []
        self._proc: Optional[subprocess.Popen] = None

    def add_listener(self, listener: Listener):
        self._listeners.append(listener)

    def run(self) -> tuple[str, str]:
        uid = next(self._UID)
        kwargs = {
            "env": self._env,
            "cwd": str(self._cwd),
            "shell": IS_WINDOWS,
            "text": True,
            "encoding": "utf-8",
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }

        LOGGER.debug("Subprocess start [args=%s,uid=%d]", self._args, uid)
        if self._listeners:
            returncode, stdout, stderr = self._run_stream(self._args, **kwargs)
        else:
            returncode, stdout, stderr = self._run_batch(self._args, **kwargs)

        LOGGER.debug("Subprocess end [returncode=%s,uid=%s]", returncode, uid)
        if returncode != 0:
            raise ProcessError(returncode, stderr)

        return stdout, stderr

    def stop(self) -> None:
        if not self._proc:
            return

        if IS_WINDOWS:
            result = subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(self._proc.pid)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if result.returncode != 0:
                LOGGER.error(
                    "Failed to stop process:\n%s", result.stdout.decode("utf-8")
                )
        else:
            self._proc.terminate()

    @staticmethod
    def _run_batch(*args, **kwargs) -> tuple[int, str, str]:
        result = subprocess.run(*args, **kwargs)  # pylint: disable=subprocess-run-check
        return result.returncode, result.stdout, result.stderr

    def _run_stream(self, *args, **kwargs) -> tuple[int, str, str]:
        kwargs["bufsize"] = 1  # Line buffered

        with subprocess.Popen(*args, **kwargs) as proc:
            assert proc.stdout
            assert proc.stderr
            assert proc.pid

            self._proc = proc

            stdout_reader = self._create_reader(proc.stdout)
            stderr_reader = self._create_reader(proc.stderr)

            stdout_lines = []

            def handle_stdout():
                lines = exhaust(stdout_reader.queue)
                stdout_lines.extend(lines)
                for line in lines:
                    self._dispatch(line)

            while proc.poll() is None:
                handle_stdout()

            self._proc = None

            stdout_reader.close.set()
            stderr_reader.close.set()

            stdout_reader.thread.join(timeout=5)
            stderr_reader.thread.join(timeout=5)

            handle_stdout()
            stderr_lines = exhaust(stderr_reader.queue)

            stdout = "\n".join(stdout_lines)
            stderr = "\n".join(stderr_lines)
            return proc.returncode, stdout, stderr

    def _create_reader(self, file: IO[str]) -> Reader:
        queue: Queue[str] = Queue()
        close = Event()
        thread = daemonize(self._reader, file, queue, close)
        return Reader(file, thread, queue, close)

    @staticmethod
    def _reader(file: IO[str], queue: Queue[Any], close: Event) -> None:
        try:
            while True:
                while line := file.readline().strip():
                    queue.put(line)
                if close.is_set():
                    break
        except ValueError as err:
            LOGGER.debug("Reading output failed [err=%s]", err)

    def _dispatch(self, line: str) -> None:
        for listener in self._listeners:
            try:
                listener(line)
            except Exception:  # pylint: disable=broad-except
                error = traceback.format_exc()
                LOGGER.error(f"Unhandled exception in listener:\n{error}")
