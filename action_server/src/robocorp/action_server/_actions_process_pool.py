import itertools
import json
import logging
import socket as socket_module
import subprocess
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set

from robocorp.action_server._models import Action, ActionPackage

from ._settings import Settings, is_frozen

log = logging.getLogger(__name__)

AF_INET, SOCK_STREAM, SHUT_WR, SOL_SOCKET, SO_REUSEADDR, IPPROTO_TCP, socket = (
    socket_module.AF_INET,
    socket_module.SOCK_STREAM,
    socket_module.SHUT_WR,
    socket_module.SOL_SOCKET,
    socket_module.SO_REUSEADDR,
    socket_module.IPPROTO_TCP,
    socket_module.socket,
)

if sys.platform == "win32":
    SO_EXCLUSIVEADDRUSE = socket_module.SO_EXCLUSIVEADDRUSE


class _Key(tuple):
    pass


def _create_server_socket(host: str, port: int):
    try:
        server = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        if sys.platform == "win32":
            server.setsockopt(SOL_SOCKET, SO_EXCLUSIVEADDRUSE, 1)
        else:
            server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        server.bind((host, port))
        server.settimeout(None)
    except Exception:
        server.close()
        raise

    return server


def _connect_to_socket(host, port):
    """connects to a host/port"""
    s = socket(AF_INET, SOCK_STREAM)

    #  Set TCP keepalive on an open socket.
    #  It activates after 1 second (TCP_KEEPIDLE,) of idleness,
    #  then sends a keepalive ping once every 3 seconds (TCP_KEEPINTVL),
    #  and closes the connection after 5 failed ping (TCP_KEEPCNT), or 15 seconds
    try:
        s.setsockopt(SOL_SOCKET, socket_module.SO_KEEPALIVE, 1)
    except (AttributeError, OSError):
        pass  # May not be available everywhere.
    try:
        s.setsockopt(socket_module.IPPROTO_TCP, socket_module.TCP_KEEPIDLE, 1)
    except (AttributeError, OSError):
        pass  # May not be available everywhere.
    try:
        s.setsockopt(socket_module.IPPROTO_TCP, socket_module.TCP_KEEPINTVL, 3)
    except (AttributeError, OSError):
        pass  # May not be available everywhere.
    try:
        s.setsockopt(socket_module.IPPROTO_TCP, socket_module.TCP_KEEPCNT, 5)
    except (AttributeError, OSError):
        pass  # May not be available everywhere.

    timeout = 20
    s.settimeout(timeout)
    s.connect((host, port))
    s.settimeout(None)  # no timeout after connected
    return s


class ProcessHandle:
    def __init__(self, settings: Settings, action_package: ActionPackage):
        from queue import Queue

        from robocorp.action_server._preload_actions.preload_actions_streams import (
            JsonRpcStreamWriter,
        )
        from robocorp.action_server._robo_utils.callback import Callback

        from ._actions_run_helpers import (
            _add_preload_actions_dir_to_env_pythonpath,
            get_action_package_cwd,
        )
        from ._preload_actions.preload_actions_streams import JsonRpcStreamReaderThread
        from ._robo_utils.process import build_python_launch_env

        self.key = _get_process_handle_key(settings, action_package)
        env = json.loads(action_package.env_json)
        _add_preload_actions_dir_to_env_pythonpath(env)
        env = build_python_launch_env(env)

        if settings.reuse_processes:
            # When reusing processes we don't want to dump threads if
            # the process doesn't exit!
            env["RC_DUMP_THREADS_AFTER_RUN"] = "0"

        if "PYTHON_EXE" in env:
            python_exe = env["PYTHON_EXE"]
        else:
            if is_frozen():
                log.critical(
                    f"Unable to create process for action package: {action_package} "
                    "(environment does not contain PYTHON_EXE)."
                )
                return

            python_exe = sys.executable

        use_tcp = False
        if use_tcp:
            assert False, "Not currently supported!"
            server_socket = _create_server_socket("", 0)
            host, port = server_socket.getsockname()
            cmdline = [
                python_exe,
                "-m",
                "preload_actions_server_main",
                "--tcp",
                f"--host={host}",
                f"--port={port}",
            ]
        else:
            # Will start things using the stdin/stdout for communicating.
            cmdline = [
                python_exe,
                "-m",
                "preload_actions_server_main",
            ]
        cwd = get_action_package_cwd(settings, action_package)

        self._process = subprocess.Popen(
            cmdline,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            cwd=cwd,
            env=env,
        )
        self._on_stderr = Callback()

        pid = self._process.pid

        def _stderr_reader(stderr):
            while True:
                line = stderr.readline()
                if not line:
                    break
                line = line.decode("utf-8", "replace")
                print(f"output (pid: {pid}): {line.strip()}\n", end="")
                self._on_stderr(line)

        stderr = self._process.stderr
        t = threading.Thread(target=_stderr_reader, args=(stderr,))
        t.name = f"Stderr reader (pid: {pid})"
        t.start()

        write_to = self._process.stdin
        read_from = self._process.stdout
        self._writer = JsonRpcStreamWriter(write_to, sort_keys=True)
        self._read_queue: "Queue[dict]" = Queue()
        self._reader = JsonRpcStreamReaderThread(
            read_from, self._read_queue, lambda *args, **kwargs: None
        )
        self._reader.start()

    @property
    def pid(self):
        return self._process.pid

    def is_alive(self) -> bool:
        from ._robo_utils.process import is_process_alive

        if self._process.poll() is not None:
            return False

        return is_process_alive(self._process.pid)

    def kill(self) -> None:
        from ._robo_utils.process import kill_process_and_subprocesses

        if not self.is_alive():
            return

        log.debug("Subprocess kill [pid=%s]", self._process.pid)
        kill_process_and_subprocesses(self._process.pid)

    def _do_run_action(
        self,
        action: Action,
        input_json: Path,
        robot_artifacts: Path,
        result_json: Path,
        headers: Dict[str, str],
    ) -> int:
        msg = {
            "command": "run_action",
            "action_name": action.name,
            "action_file": f"{action.file}",
            "input_json": f"{input_json}",
            "robot_artifacts": f"{robot_artifacts}",
            "result_json": f"{result_json}",
            "headers": headers,
        }
        self._writer.write(msg)
        queue = self._read_queue
        result_msg = queue.get(block=True)
        return result_msg["returncode"]

    def run_action(
        self,
        action: Action,
        input_json: Path,
        robot_artifacts: Path,
        output_file: Path,
        result_json: Path,
        headers: Dict[str, str],
    ) -> int:
        """
        Runs the action and returns the returncode from running the action.

        (returncode=0 means everything is Ok).
        """
        with output_file.open("w") as stream:

            def on_output(line):
                stream.write(line)

            with self._on_stderr.register(on_output):
                # stdout is now used for communicating, so, don't hear on it.
                returncode = self._do_run_action(
                    action,
                    input_json,
                    robot_artifacts,
                    result_json,
                    headers,
                )
                return returncode


def _get_process_handle_key(settings: Settings, action_package: ActionPackage) -> _Key:
    """
    Given an action provides a key where the key identifies whether a
    given action can be run at a given ProcessHandle.
    """
    from ._actions_run_helpers import get_action_package_cwd

    env = tuple(sorted(json.loads(action_package.env_json).items()))
    cwd = get_action_package_cwd(settings, action_package)
    return _Key((env, cwd))


class ActionsProcessPool:
    def __init__(
        self,
        settings: Settings,
        action_package_id_to_action_package: Dict[str, ActionPackage],
        actions: List[Action],
    ):
        self._settings = settings
        self.action_package_id_to_action_package = action_package_id_to_action_package

        # We just want the actions which are enabled.
        self.actions = [action for action in actions if action.enabled]

        # An iterator which keeps cycling over the actions.
        self._cycle_actions_iterator = itertools.cycle(self.actions)

        self._lock = threading.Lock()
        self._running_processes: Dict[_Key, Set[ProcessHandle]] = {}
        self._idle_processes: Dict[_Key, Set[ProcessHandle]] = {}

        # Semaphore used to track running processes.
        self._processes_running_semaphore = threading.Semaphore(self.max_processes)

        self._warmup_processes()

    @property
    def _reuse_processes(self) -> bool:
        """
        Returns:
            Whether processes can be reused.
        """
        return self._settings.reuse_processes

    @property
    def max_processes(self) -> int:
        """
        Returns:
            The maximum number of processes that may be created by the process
            pool.
        """
        return self._settings.max_processes

    @property
    def min_processes(self) -> int:
        return self._settings.min_processes

    def _create_process(self, action: Action):
        action_package: ActionPackage = self.action_package_id_to_action_package[
            action.action_package_id
        ]

        process_handle = ProcessHandle(self._settings, action_package)
        assert self._lock.locked(), "Lock must be acquired at this point."
        self._add_to_idle_processes(process_handle)

    def dispose(self):
        with self._lock:
            for processes in itertools.chain(
                self._idle_processes.values(), self._running_processes.values()
            ):
                for process_handle in processes:
                    process_handle.kill()
            self._idle_processes.clear()
            self._running_processes.clear()

    def get_idle_processes_count(self) -> int:
        with self._lock:
            return self._get_idle_processes_count_unlocked()

    def _get_idle_processes_count_unlocked(self) -> int:
        assert self._lock.locked(), "Lock must be acquired at this point."
        count = 0
        for v in self._idle_processes.values():
            count += len(v)
        return count

    def get_running_processes_count(self) -> int:
        with self._lock:
            return self._get_running_processes_count_unlocked()

    def _get_running_processes_count_unlocked(self) -> int:
        assert self._lock.locked(), "Lock must be acquired at this point."
        count = 0
        for v in self._running_processes.values():
            count += len(v)
        return count

    def _count_total_processes(self) -> int:
        assert self._lock.locked(), "Lock must be acquired at this point."
        count = 0
        for v in itertools.chain(
            self._running_processes.values(), self._idle_processes.values()
        ):
            count += len(v)
        return count

    def _add_to_idle_processes(self, process_handle: ProcessHandle):
        assert self._lock.locked(), "Lock must be acquired at this point."
        processes = self._idle_processes.get(process_handle.key)
        if processes is None:
            processes = self._idle_processes[process_handle.key] = set()
        processes.add(process_handle)

    def _add_to_running_processes(self, process_handle: ProcessHandle):
        assert self._lock.locked(), "Lock must be acquired at this point."
        self._processes_running_semaphore.acquire()
        processes = self._running_processes.get(process_handle.key)
        if processes is None:
            processes = self._running_processes[process_handle.key] = set()
        processes.add(process_handle)

    def _remove_from_running_processes(self, process_handle: ProcessHandle):
        assert self._lock.locked(), "Lock must be acquired at this point."
        self._processes_running_semaphore.release()
        processes = self._running_processes.get(process_handle.key)
        if not processes:
            return
        processes.discard(process_handle)

    def _warmup_processes(self):
        if not self.actions:
            return

        with self._lock:
            while self._count_total_processes() < self._settings.min_processes:
                one_action = next(self._cycle_actions_iterator)
                self._create_process(one_action)

    @contextmanager
    def obtain_process_for_action(self, action: Action) -> Iterator[ProcessHandle]:
        action_package: ActionPackage = self.action_package_id_to_action_package[
            action.action_package_id
        ]

        key = _get_process_handle_key(self._settings, action_package)
        process_handle: Optional[ProcessHandle] = None
        while True:
            with self._lock:
                processes = self._idle_processes.get(key)
                if processes:
                    # Get any process from the (compatible) idle processes.
                    process_handle = processes.pop()
                    log.debug(
                        f"Process Pool: Using idle process ({process_handle.pid})."
                    )
                    self._add_to_running_processes(process_handle)
                else:
                    # No compatible process: we need to create one now.
                    n_running = self._get_running_processes_count_unlocked()
                    if n_running < self.max_processes:
                        self._create_process(action)
                        processes = self._idle_processes.get(key)
                        assert (
                            processes
                        ), f"Expected idle processes bound to key: {key} at this point!"
                        process_handle = processes.pop()
                        log.debug(
                            f"Process Pool: Created process ({process_handle.pid})."
                        )
                        self._add_to_running_processes(process_handle)
                    else:
                        log.critical(
                            f"Delayed running action: {action.name} because "
                            f"{self.max_processes} actions are already running ("
                            f"waiting for another action to finish running)."
                        )

            if process_handle is not None:
                break
            else:
                # Each 5 seconds check again and print delayed message if still
                # not able to run.
                if self._processes_running_semaphore.acquire(timeout=5):
                    self._processes_running_semaphore.release()

        if process_handle is not None:
            try:
                yield process_handle
            finally:
                with self._lock:
                    self._remove_from_running_processes(process_handle)
                    if process_handle.is_alive():
                        if self._reuse_processes:
                            curr_idle = self._get_idle_processes_count_unlocked()
                            if self.min_processes <= curr_idle:
                                log.debug(
                                    f"Process Pool: Exited process ({process_handle.pid}) -- min processes already satisfied."
                                )
                                # We cannot reuse it!
                                process_handle.kill()
                            else:
                                log.debug(
                                    f"Process Pool: Adding back to pool ({process_handle.pid})."
                                )
                                self._add_to_idle_processes(process_handle)
                        else:
                            log.debug(
                                f"Process Pool: Exited process ({process_handle.pid}) -- not reusing processes."
                            )
                            # We cannot reuse it!
                            process_handle.kill()

                # If needed recreate idle processes which were removed (needed
                # especially when not reusing processes, but if some process
                # crashes it's also needed).
                self._warmup_processes()

            return

        raise AssertionError("Expected process_handle to be not None!")


_actions_process_pool: Optional[ActionsProcessPool] = None


@contextmanager
def setup_actions_process_pool(
    settings: Settings,
    action_package_id_to_action_package: Dict[str, ActionPackage],
    actions: List[Action],
):
    global _actions_process_pool

    _actions_process_pool = ActionsProcessPool(
        settings, action_package_id_to_action_package, actions
    )
    yield
    _actions_process_pool = None


def get_actions_process_pool() -> ActionsProcessPool:
    assert _actions_process_pool is not None
    return _actions_process_pool
