import os
import platform
import subprocess
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

T = TypeVar("T")
PathLike = Union[str, Path]
Listener = Callable[[str], Any]

IS_WINDOWS = platform.system() == "Windows"


def daemonize(target, *args):
    thread = Thread(target=target, args=args)
    thread.daemon = True
    thread.start()
    return thread


def exhaust(queue: Queue[T]) -> List[T]:
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
    def __init__(self, returncode, stderr):
        super().__init__()
        self.returncode: int = int(returncode)
        self.stderr: List[str] = stderr

    def __str__(self):
        name = self.__class__.__name__
        lines = "\\n".join(line for line in self.stderr)
        return f"{name}[returncode={self.returncode},stderr='{lines}']"


class Process:
    def __init__(
        self,
        args: List[str],
        cwd: Optional[PathLike] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        self._args = args
        self._cwd = cwd or Path.cwd()
        self._env = {**os.environ, **(env or {})}
        self._listeners: List[Listener] = []
        self._proc: Optional[subprocess.Popen] = None

    def add_listener(self, listener: Listener):
        self._listeners.append(listener)

    def run(self) -> Tuple[List[str], List[str]]:
        kwargs = {
            "env": self._env,
            "cwd": str(self._cwd),
            "shell": IS_WINDOWS,
            "text": True,
            "encoding": "utf-8",
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }

        if self._listeners:
            returncode, stdout, stderr = self._run_stream(self._args, **kwargs)
        else:
            returncode, stdout, stderr = self._run_batch(self._args, **kwargs)

        if returncode != 0:
            raise ProcessError(returncode, stderr)

        return stdout, stderr

    def stop(self):
        if not self._proc:
            return

        if IS_WINDOWS:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(self._proc.pid)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        else:
            self._proc.terminate()

    @staticmethod
    def _run_batch(*args, **kwargs):
        result = subprocess.run(*args, **kwargs)

        stdout_lines = result.stdout.splitlines()
        stderr_lines = result.stderr.splitlines()

        return result.returncode, stdout_lines, stderr_lines

    def _run_stream(self, *args, **kwargs):
        kwargs["bufsize"] = 1  # Line buffered

        with subprocess.Popen(*args, **kwargs) as proc:
            assert proc.stdout
            assert proc.stderr
            assert proc.pid

            self._proc = proc

            stdout = self._create_reader(proc.stdout)
            stderr = self._create_reader(proc.stderr)

            stderr_lines = []

            def handle_stderr():
                lines = exhaust(stderr.queue)
                stderr_lines.extend(lines)
                for line in lines:
                    self._dispatch(line)

            while proc.poll() is None:
                handle_stderr()

            self._proc = None
            stdout.close.set()
            stderr.close.set()

            stdout.thread.join(timeout=5)
            stderr.thread.join(timeout=5)

            stdout_lines = exhaust(stderr.queue)
            handle_stderr()

            return proc.returncode, stdout_lines, stderr_lines

    def _create_reader(self, file: IO[str]):
        queue: Queue[str] = Queue()
        close = Event()
        thread = daemonize(self._reader, file, queue, close)
        return Reader(file, thread, queue, close)

    @staticmethod
    def _reader(file: IO[str], queue: Queue[Any], close: Event):
        while True:
            while line := file.readline().strip():
                queue.put(line)
            if close.is_set():
                break

    def _dispatch(self, line: str):
        for listener in self._listeners:
            listener(line)
