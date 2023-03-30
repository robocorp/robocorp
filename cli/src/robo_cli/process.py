import logging
import os
import platform
import subprocess
import time
from pathlib import Path
from threading import Event, Thread
from typing import IO, Any, Callable, Dict, List, Optional, Tuple, Union

PathLike = Union[str, Path]
Listener = Callable[[str], Any]

IS_WINDOWS = platform.system() == "Windows"
LOGGER = logging.getLogger(__name__)


class Reader(Thread):
    def __init__(self, file: IO[str], listeners: List[Listener], interval=0.1):
        super().__init__()
        self._file = file
        self._listeners = listeners
        self._interval = float(interval)
        self._lines: List[str] = []
        self._close = Event()

    @property
    def lines(self):
        return list(self._lines)

    def close(self):
        self._close.set()

    def run(self):
        try:
            while not self._close.is_set():
                self._readlines()
                time.sleep(self._interval)
        except ValueError as err:
            LOGGER.warning("Reading output failed: %s", err)

        # Ensure everything is read after close
        self._readlines()

    def _readlines(self):
        while line := self._file.readline().strip():
            self._lines.append(line)
            for listener in self._listeners:
                try:
                    listener(line)
                except Exception as exc:
                    LOGGER.warning("Unhandled exception in listener: %s", exc)


class ProcessError(RuntimeError):
    def __init__(
        self,
        returncode: int,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ):
        super().__init__()
        self.returncode = returncode
        self.stdout: str = stdout or ""
        self.stderr: str = stderr or ""

    def __str__(self):
        name = self.__class__.__name__
        return f"{name}[returncode={self.returncode}]"


class Process:
    def __init__(
        self,
        args: List[str],
        cwd: Optional[PathLike] = None,
        env: Optional[Dict[str, str]] = None,
        shell=IS_WINDOWS,  # TODO: Remove later
    ):
        self._args = args
        self._cwd = cwd or Path.cwd()
        self._env = {**os.environ, **(env or {})}
        self._shell = shell

        self._on_stdout: List[Listener] = []
        self._on_stderr: List[Listener] = []
        self._proc: Optional[subprocess.Popen] = None

    def on_stdout(self, listener: Listener):
        self._on_stdout.append(listener)

    def on_stderr(self, listener: Listener):
        self._on_stderr.append(listener)

    def run(self) -> Tuple[str, str]:
        options = {
            "env": self._env,
            "cwd": str(self._cwd),
            "shell": self._shell,
            "text": True,
            "bufsize": 1,  # Line buffered
            "encoding": "utf-8",
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
        }

        with subprocess.Popen(self._args, **options) as proc:
            assert proc.stdout
            assert proc.stderr
            assert proc.pid

            stdout_reader = Reader(proc.stdout, self._on_stdout)
            stderr_reader = Reader(proc.stderr, self._on_stderr)

            stdout_reader.start()
            stderr_reader.start()

            self._proc = proc
            self._proc.wait()

            stdout_reader.close()
            stderr_reader.close()

            stdout_reader.join(timeout=5)
            stderr_reader.join(timeout=5)

            returncode = self._proc.returncode
            stdout = "\n".join(stdout_reader.lines)
            stderr = "\n".join(stderr_reader.lines)

        if returncode != 0:
            raise ProcessError(returncode, stdout, stderr)

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
