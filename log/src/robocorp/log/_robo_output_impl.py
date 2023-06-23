import datetime
import itertools
import json
import os
import string
import sys
import threading
import time
import traceback
import weakref
from datetime import timezone
from functools import partial
from pathlib import Path
from types import FrameType
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
)

from .protocols import LogElementType, OptExcInfo

WRITE_CONTENTS_TO_STDERR: bool = False


_valid_chars = tuple(string.ascii_letters + string.digits)


def _gen_id(level: int = 1) -> Iterator[str]:
    iter_in = tuple(_valid_chars for _ in range(level))
    for entry in itertools.product(*iter_in):
        yield "".join(entry)

    # Recursively generate ids...
    yield from _gen_id(level + 1)


def _pprint_secs(secs):
    """Format seconds in a human readable form."""
    now = time.time()
    secs_ago = int(now - secs)
    if secs_ago < 60 * 60 * 24:
        fmt = "%H:%M:%S"
    else:
        fmt = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.fromtimestamp(secs).strftime(fmt)


# see: http://goo.gl/kTQMs
SYMBOLS = {
    "customary": ("B", "K", "M", "G", "T", "P", "E", "Z", "Y"),
    "customary_ext": (
        "byte",
        "kilo",
        "mega",
        "giga",
        "tera",
        "peta",
        "exa",
        "zetta",
        "iotta",
    ),
    "iec": ("Bi", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi"),
    "iec_ext": ("byte", "kibi", "mebi", "gibi", "tebi", "pebi", "exbi", "zebi", "yobi"),
}


def bytes2human(n, format="%(value).1f %(symbol)s", symbols="customary"):
    """
    Bytes-to-human / human-to-bytes converter.
    Based on: http://goo.gl/kTQMs
    Working with Python 2.x and 3.x.

    Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
    License: MIT
    """

    """
    Convert n bytes into a human readable string based on format.
    symbols can be either "customary", "customary_ext", "iec" or "iec_ext",
    see: http://goo.gl/kTQMs

      >>> bytes2human(0)
      '0.0 B'
      >>> bytes2human(0.9)
      '0.0 B'
      >>> bytes2human(1)
      '1.0 B'
      >>> bytes2human(1.9)
      '1.0 B'
      >>> bytes2human(1024)
      '1.0 K'
      >>> bytes2human(1048576)
      '1.0 M'
      >>> bytes2human(1099511627776127398123789121)
      '909.5 Y'

      >>> bytes2human(9856, symbols="customary")
      '9.6 K'
      >>> bytes2human(9856, symbols="customary_ext")
      '9.6 kilo'
      >>> bytes2human(9856, symbols="iec")
      '9.6 Ki'
      >>> bytes2human(9856, symbols="iec_ext")
      '9.6 kibi'

      >>> bytes2human(10000, "%(value).1f %(symbol)s/sec")
      '9.8 K/sec'

      >>> # precision can be adjusted by playing with %f operator
      >>> bytes2human(10000, format="%(value).5f %(symbol)s")
      '9.76562 K'
    """
    n = int(n)
    if n < 0:
        raise ValueError("n < 0")
    symbols = SYMBOLS[symbols]
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i + 1) * 10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)


def format_memory_info(memory_info):
    return f"Total: {bytes2human(memory_info.total)}, Available: {bytes2human(memory_info.available)}, Used: {memory_info.percent} %"


class _Config:
    # Loaded from constructor args
    output_dir: Optional[str]
    max_file_size_in_bytes: int
    max_files: int

    # Note that this limit is counted without considering the messages
    # written internally right after the rotation, which add info
    # on the part or the python version.
    min_messages_per_file: int

    log_html: Optional[str]
    log_html_style: int
    uuid: str

    # Loaded from constructor kwargs (to be used
    # only when used as an API).
    write: Optional[Callable[[str], None]] = None
    initial_time: Optional[datetime.datetime] = None
    additional_info: Optional[Sequence[str]] = None

    def __init__(self, uuid=None):
        if uuid is None:
            import uuid as uuid_module

            uuid = f"{uuid_module.uuid1()}"
        self.uuid = uuid
        self.output_dir = "./out_"


class _RotateHandler:
    def __init__(self, max_file_size_in_bytes: int, max_files: int):
        if max_files <= 0:
            raise ValueError(f"max_files must be > 0. Found: {max_files}")

        self._max_file_size_in_bytes = max_file_size_in_bytes
        self._total_bytes = 0

        self._found_files: List[Path] = []
        self._max_files = max_files

    def add_bytes(self, bytes_len):
        self._total_bytes += bytes_len

    def rotate_after(self):
        if self._total_bytes >= self._max_file_size_in_bytes:
            self._total_bytes = 0
            return True
        return False

    def register_file(self, filepath: Path):
        self._found_files.append(filepath)

        while len(self._found_files) > self._max_files:
            p: Path = self._found_files.pop(0)
            try:
                os.remove(p)
            except:
                traceback.print_exc()

    def iter_found_files(self):
        yield from iter(self._found_files)


class _StackEntry:
    def __init__(
        self, entry_type, entry_id, msg_type, replay_msg_type, hide_from_logs, write_it
    ) -> None:
        self.entry_type = entry_type
        self.entry_id = entry_id
        self.msg_type = msg_type
        self.replay_msg_type = replay_msg_type
        self.hide_from_logs = hide_from_logs
        self._messages: List[str] = []
        self.write_it = write_it

    def rewrite(self, robot_output_impl):
        self.write_it(robot_output_impl, self.replay_msg_type)

    def __str__(self):
        return f"StackEntry({self.entry_type}, {self.entry_id}, {self.msg_type}, hide: {self.hide_from_logs})"

    __repr__ = __str__


class _StackHandler:
    def __init__(self, robot_output_impl):
        self._queue = []
        self._robot_output_impl = weakref.ref(robot_output_impl)

    def push_record(
        self,
        entry_type: str,
        entry_id: str,
        msg_type: str,
        replay_msg_type: str,
        hide_from_logs: bool,
        write_it: Callable[[Any, str], Any],
    ) -> None:
        entry = _StackEntry(
            entry_type, entry_id, msg_type, replay_msg_type, hide_from_logs, write_it
        )
        write_it(self._robot_output_impl(), msg_type)
        self._queue.append(entry)

    def pop(self, entry_type, entry_id) -> Optional[_StackEntry]:
        if not self._queue:
            impl = self._robot_output_impl()
            if impl is not None:
                impl.show_error_message(
                    f"Robocorp Log Warning: unable to pop {entry_type} - {entry_id} (empty queue).\n"
                )
        else:
            stack_entry = self._queue[-1]
            if (
                stack_entry.entry_type == entry_type
                and stack_entry.entry_id == entry_id
            ):
                return self._queue.pop(-1)

            else:
                for i, stack_entry in enumerate(reversed(self._queue)):
                    if (
                        stack_entry.entry_type == entry_type
                        and stack_entry.entry_id == entry_id
                    ):
                        for _ in range(i):
                            stack_entry = self._queue.pop(-1)
                            impl = self._robot_output_impl()
                            if impl is not None:
                                impl.show_error_message(
                                    f"Robocorp Log Warning: {stack_entry.entry_type} - {stack_entry.entry_id} did not have a corresponding pop.\n"
                                )

                        # The current one (which is a match).
                        return self._queue.pop(-1)

                if entry_type in ("task", "run"):
                    for i, stack_entry in enumerate(reversed(self._queue)):
                        if stack_entry.entry_type == entry_type:
                            for _ in range(i):
                                stack_entry = self._queue.pop(-1)
                                impl = self._robot_output_impl()
                                if impl is not None:
                                    impl.show_error_message(
                                        f"Robocorp Log Warning: {stack_entry.entry_type} - {stack_entry.entry_id} did not have a corresponding pop.\n"
                                    )

                            # The current one (which is a partial match).
                            stack_entry = self._queue.pop(-1)
                            impl = self._robot_output_impl()
                            if impl is not None:
                                impl.show_error_message(
                                    f"Robocorp Log Warning: {stack_entry.entry_type} - {stack_entry.entry_id} pop just by type. Actual request: {entry_type} - {entry_id}\n"
                                )
                            return stack_entry

                impl = self._robot_output_impl()
                if impl is not None:
                    impl.show_error_message(
                        f"Robocorp Log Warning: unable to pop {entry_type} - {entry_id} because it does not match the current top: {stack_entry.entry_type} - {stack_entry.entry_id}\n"
                    )

        return None

    def __iter__(self):
        for stack_entry in self._queue:
            assert isinstance(stack_entry, _StackEntry)
            yield stack_entry


class _RoboOutputImpl:
    def __init__(self, config: _Config):
        self._written_initial = False
        self._closed = False

        # Base memory for all streams (rotated or not)
        self._base_memo: Dict[str, str] = {}
        self._base_loc_memo: Dict[Tuple[str, str, str, int], str] = {}

        # Memory just for the current stream (if a name is not
        # here it has to be added because the output was rotated).
        self._current_memo: Dict[str, str] = {}
        self._current_loc_memo: Dict[Tuple[str, str, str, int], str] = {}

        self._config = config
        self._id = config.uuid

        if config.output_dir is None:
            self._output_dir = None
        else:
            self._output_dir = Path(config.output_dir)
            self._output_dir.mkdir(exist_ok=True)
        self._write = config.write

        self._move_old_runs()

        self._current_entry = 0
        self._messages_written_after_rotation = 0
        self._current_file: Optional[Path] = None

        from io import BufferedWriter

        self._stream: Optional[BufferedWriter] = None

        if config.initial_time is None:
            self._initial_time = datetime.datetime.now(timezone.utc)
        else:
            self._initial_time = config.initial_time
        self._initial_time_in_seconds = time.time()

        self._stack_handler = _StackHandler(self)

        self._rotating = False
        self._rotate_handler = _RotateHandler(
            config.max_file_size_in_bytes, config.max_files
        )
        self._id_generator = _gen_id()

        if self._output_dir is not None:
            self._rotate_output()
        else:
            self._current_entry = 1
            self._write_on_start_or_after_rotate()

        self.on_show_error_message = None
        self._hide_strings_re: Optional[Pattern[str]] = None
        self._hide_strings: Set[str] = set()

        self._next_int: "partial[int]" = partial(next, itertools.count(0))

    def show_error_message(self, msg):
        sys.stderr.write(msg)
        if self.on_show_error_message:
            self.on_show_error_message(msg)

    def hide_from_output(self, string_to_hide: str) -> None:
        import re

        if string_to_hide in self._hide_strings:
            return

        self._hide_strings.add(string_to_hide)
        lst = []
        for s in self._hide_strings:
            lst.append(re.escape(s))

        self._hide_strings_re = re.compile("|".join(lst))

    @property
    def current_file(self) -> Optional[Path]:
        return self._current_file

    @property
    def initial_time(self) -> datetime.datetime:
        return self._initial_time

    def _rotate_output(self) -> None:
        if self._output_dir is None:
            return

        if self._rotating:
            # Prevent trying to rotate while in the rotation already
            # (on corner case where just the initial messages would
            # be too much).
            return

        self._rotating = True
        try:
            self._current_memo = {}
            self._current_loc_memo = {}

            self._current_entry += 1
            if self._current_entry != 1:
                self._current_file = (
                    self._output_dir / f"output_{self._current_entry}.robolog"
                )
            else:
                self._current_file = self._output_dir / f"output.robolog"

            if self._stream is not None:
                self._stream.close()
                self._stream = None

            self._rotate_handler.register_file(self._current_file)

            self._stream = self._current_file.open("wb")
            self._write_on_start_or_after_rotate()
            self._messages_written_after_rotation = 0
        finally:
            self._rotating = False

    def _write_on_start_or_after_rotate(self):
        from ._decoder import DOC_VERSION

        # if self._current_file is not None:
        #     print("Robocorp Log output:", self._current_file.absolute())

        self._write_with_separator("V ", (DOC_VERSION,))
        self._write_with_separator(
            "T ", (self._initial_time.isoformat(timespec="milliseconds"),)
        )
        self._write_with_separator("ID ", (f"{self._current_entry}", self._id))
        if self._config.additional_info:
            for info in self._config.additional_info:
                self._write_json("I ", info)
        else:
            self._write_json("I ", f"sys.platform={sys.platform}")
            self._write_json("I ", f"python={sys.version}")

        for stack_entry in self._stack_handler:
            stack_entry.rewrite(self)

    def _do_write(self, s: str) -> None:
        if self._write is not None:
            self._write(s)

        in_bytes = s.encode("utf-8", errors="replace")
        if self._stream is not None:
            self._stream.write(in_bytes)
            self._stream.flush()

        self._messages_written_after_rotation += 1
        self._rotate_handler.add_bytes(len(in_bytes))

    def _rotate_if_needed(self):
        if (
            self._messages_written_after_rotation > self._config.min_messages_per_file
            and not self._rotating
        ):
            if self._rotate_handler.rotate_after():
                self._rotate_output()

    def _write_json(self, msg_type, args):
        args_as_str = json.dumps(args)
        s = f"{msg_type}{args_as_str}\n"
        self._do_write(s)
        return s

    def _write_with_separator(self, msg_type, args):
        args_as_str = "|".join(args)
        s = f"{msg_type}{args_as_str}\n"
        self._do_write(s)
        return s

    def get_time_delta(self) -> float:
        delta = time.time() - self._initial_time_in_seconds
        return round(delta, 3)

    def _move_old_runs(self):
        pass
        # TODO: Handle old runs (move to old runs).
        # for entry in self._output_dir.iterdir():
        #     print(entry)

    def _gen_id(self) -> str:
        while True:
            gen = next(self._id_generator)
            if gen not in self._base_memo:
                return gen

    def _obtain_id(self, s: str) -> str:
        curr_id = self._current_memo.get(s)
        if curr_id is not None:
            return curr_id

        curr_id = self._base_memo.get(s)
        if curr_id is not None:
            self._write_json(f"M {curr_id}:", s)
            self._current_memo[s] = curr_id
            return curr_id

        new_id = self._gen_id()
        self._write_json(f"M {new_id}:", s)
        self._base_memo[s] = new_id
        self._current_memo[s] = new_id
        return new_id

    def _obtain_loc_id(
        self, name: str, libname: str, source: str, lineno: int, docstring: str = ""
    ) -> str:
        key = (name, libname, source, lineno)
        curr_id = self._current_loc_memo.get(key)
        if curr_id is not None:
            return curr_id
        oid = self._obtain_id

        curr_id = self._base_loc_memo.get(key)
        if curr_id is not None:
            self._do_write(
                f"P {curr_id}:{oid(name)}|{oid(libname)}|{oid(source)}|{oid(docstring)}|{lineno}\n"
            )
            self._current_loc_memo[key] = curr_id
            return curr_id

        new_id = self._gen_id()
        self._do_write(
            f"P {new_id}:{oid(name)}|{oid(libname)}|{oid(source)}|{oid(docstring)}|{lineno}\n"
        )
        self._base_loc_memo[key] = new_id
        self._current_loc_memo[key] = new_id
        return new_id

    def _number(self, v):
        return str(v)

    class _WriteStartRun:
        def __init__(self, name, time_delta):
            self.name = name
            self.time_delta = time_delta

        def __call__(self, robot_impl, msg_type):
            oid = robot_impl._obtain_id
            robot_impl._write_with_separator(
                f"{msg_type} ",
                [
                    oid(self.name),
                    robot_impl._number(self.time_delta),
                ],
            ),

    def start_run(self, name: str, time_delta: float) -> None:
        self._stack_handler.push_record(
            "run", name, "SR", "RR", False, self._WriteStartRun(name, time_delta)
        )

    def end_run(self, name: str, status: str, time_delta: float) -> None:
        oid = self._obtain_id
        self._write_with_separator(
            "ER ",
            [
                oid(status),
                self._number(time_delta),
            ],
        )
        self._stack_handler.pop("run", name)

    class _WriteStartTask:
        def __init__(self, name, libname, source, line, doc, time_delta):
            self.name = name
            self.libname = libname
            self.source = source
            self.line = line
            self.doc = doc
            self.time_delta = time_delta

        def __call__(self, robot_impl, msg_type):
            loc_id = robot_impl._obtain_loc_id

            robot_impl._write_with_separator(
                f"{msg_type} ",
                [
                    loc_id(self.name, self.libname, self.source, self.line, self.doc),
                    robot_impl._number(self.time_delta),
                ],
            ),

    def start_task(
        self,
        name: str,
        libname: str,
        source: str,
        line: int,
        doc: str,
        time_delta: float,
    ):
        self._rotate_if_needed()

        task_id = f"{libname}.{name}"
        self._stack_handler.push_record(
            "task",
            task_id,
            "ST",
            "RT",
            False,
            self._WriteStartTask(name, libname, source, line, doc, time_delta),
        )

    def send_info(self, info: str):
        self._write_json("I ", info)

    def send_start_time_delta(self, time_delta_in_seconds: float):
        self._write_with_separator("S ", (self._number(time_delta_in_seconds),))

    def end_task(
        self, name: str, libname: str, status: str, message: str, time_delta: float
    ):
        oid = self._obtain_id
        self._write_with_separator(
            "ET ",
            [
                oid(status),
                oid(message),
                self._number(time_delta),
            ],
        )
        task_id = f"{libname}.{name}"
        self._stack_handler.pop("task", task_id)

    class _WriteProcessSnapshot:
        def __init__(self, time_delta):
            self.time_delta = time_delta

        def __call__(self, robot_impl, msg_type):
            oid = robot_impl._obtain_id
            robot_impl._write_with_separator(
                f"{msg_type} ",
                [
                    oid("Process snapshot"),
                    robot_impl._number(self.time_delta),
                ],
            ),

    def process_snapshot(self, hide_vars: bool) -> None:
        self._rotate_if_needed()

        entry_id = f"ps_{self._next_int()}"
        entry_type = "process_snapshot"

        self._stack_handler.push_record(
            entry_type,
            entry_id,
            "SPS",
            "RPS",
            False,
            self._WriteProcessSnapshot(self.get_time_delta()),
        )

        try:
            try:
                import psutil
                from psutil import AccessDenied, NoSuchProcess, ZombieProcess
            except ImportError:
                pass
            else:
                curr_process = psutil.Process()

                def log_info(message):
                    self.log_message(
                        "I", message, False, "", "", "", 0, self.get_time_delta()
                    )

                memory_info = "<unknown>"
                try:
                    memory_info = format_memory_info(psutil.virtual_memory())
                    memory_info = format_memory_info(psutil.virtual_memory())
                except:
                    pass

                log_info(
                    f"""System information:
Memory: {memory_info}
CPUs: {os.cpu_count()}"""
                )

                for child_i, child in enumerate(
                    itertools.chain(
                        [curr_process], curr_process.children(recursive=True)
                    )
                ):
                    name = "<unknown>"
                    status = "<unknown>"
                    create_time = "<unknown>"
                    ppid = "<unknown>"
                    cmdline = "<unknown>"
                    rss = "<unknown>"
                    vms = "<unknown>"

                    try:
                        with child.oneshot():
                            try:
                                name = child.name()
                                status = child.status()
                                try:
                                    create_time = _pprint_secs(child.create_time())
                                except:
                                    pass
                                ppid = str(child.ppid())
                                cmdline = " ".join(child.cmdline())
                                proc_memory_info = child.memory_info()
                                rss = bytes2human(proc_memory_info.rss)
                                vms = bytes2human(proc_memory_info.vms)
                            except ZombieProcess:
                                status = "zombie"
                            except NoSuchProcess:
                                status = "terminated"
                            except AccessDenied:
                                pass
                            except Exception:
                                pass
                    except:
                        pass

                    message = f"""{"Subprocess" if child_i > 0 else "Current Process"}: {name} (pid: {child.pid}, status: {status})
Command Line: {cmdline}
Started: {create_time}
Parent pid: {ppid}
Resident Set Size: {rss}
Virtual Memory Size: {vms}"""
                    log_info(message)

            self._dump_threads(hide_vars)
        finally:
            self._stack_handler.pop(entry_type, entry_id)
            self._write_with_separator(f"EPS ", [self._number(self.get_time_delta())])

    def _dump_threads(self, hide_vars: bool) -> None:
        for thread_id, frame in sys._current_frames().items():
            try:
                thread = threading._active[thread_id]  # type: ignore [attr-defined] # @UndefinedVariable
                title = f"{thread.name}|Thread ID: {thread_id} ({'daemon' if thread.daemon else 'non daemon'})"
            except KeyError:
                title = f"{thread_id}|(not active)"

            f: Optional[FrameType] = frame
            stack: List[tuple] = []
            while f is not None:
                if "__tracebackhide__" in f.f_locals:
                    break
                stack.append((f, f.f_lineno))
                f = f.f_back
            stack = list(reversed(stack))

            self._write_stack(
                title,
                stack,
                entry_type="thread_dump",
                start_message_types=("STD", "RTD", "ETD"),
                hide_vars=hide_vars,
            )

    def log_method_except(
        self,
        exc_info: OptExcInfo,
        unhandled: bool,
        hide_vars: bool,
    ) -> bool:
        """
        :param exc_info:
            The actual exception information gotten from sys.exc_info().

        :param unhandled:
            Whether the exception should be considered unhandled at this point.
            If it's unhandled it'll always be shown (it means it's bubbling up
            at the task level), otherwise we'll only show the exception if this
            is the first place where it'd be shown (if it's not the first place
            and we're dealing with an unhandled exception it won't be logged
            at this point).

        :returns:
            Whether the exception was added to the log or not -- this may be
            because the exc_info is not complete or cases where the exception
            was already previously logged (see the `unhandled` parameter for
            details on the use-cases where it may be skipped).
        """
        self._rotate_if_needed()

        exception_type, exception, tb = exc_info
        if exception is None or tb is None or exception_type is None:
            return False

        f = tb.tb_frame.f_back
        stack: List[tuple] = []
        while f is not None:
            if "__tracebackhide__" in f.f_locals:
                break
            stack.append((f, f.f_lineno))
            f = f.f_back

        stack = list(reversed(stack))

        # For the current one the lineno must be gotten from the traceback.
        stack.append((tb.tb_frame, tb.tb_lineno))

        tb = tb.tb_next
        while tb is not None:
            frame, tb_lineno = tb.tb_frame, tb.tb_lineno

            if not unhandled and "@py_sys" in frame.f_locals:
                # The exception should've been shown previously, so, don't
                # show it at this level again.
                return False

            stack.append((frame, tb_lineno))
            tb = tb.tb_next

        self._write_stack(
            f"{exception_type.__name__}: {exception}",
            stack,
            entry_type="traceback",
            start_message_types=("STB", "RTB", "ETB"),
            hide_vars=hide_vars,
        )
        return True

    class _WriteStack:
        def __init__(self, title, time_delta):
            self.title = title
            self.time_delta = time_delta

        def __call__(self, robot_impl, msg_type):
            oid = robot_impl._obtain_id
            robot_impl._write_with_separator(
                f"{msg_type} ",
                [oid(self.title), robot_impl._number(self.time_delta)],
            ),

    def _write_stack(
        self,
        title: str,
        stack: List[tuple],
        entry_type: str,
        start_message_types: Tuple[str, str, str],
        hide_vars: bool,
    ) -> None:
        start_message_type, restart_message_type, end_message_type = start_message_types

        # Write the stack now.
        import linecache

        from ._obj_info_repr import get_obj_type_and_repr

        oid = self._obtain_id
        entry_id = f"tb_{self._next_int()}"

        self._stack_handler.push_record(
            entry_type,
            entry_id,
            start_message_type,
            restart_message_type,
            False,
            self._WriteStack(title, self.get_time_delta()),
        )

        for frame, tb_lineno in stack:
            code = frame.f_code
            code_filename = code.co_filename
            try:
                line_content = linecache.getline(code_filename, tb_lineno).strip()
            except:
                line_content = ""  # Unable to get contents.

            self._write_with_separator(
                "TBE ",
                [
                    oid(code_filename),
                    self._number(tb_lineno),
                    oid(code.co_name),
                    oid(line_content),
                ],
            )

            if not hide_vars:
                for key, val in tuple(frame.f_locals.items()):
                    if key.startswith("@"):
                        # Skip our own variables.
                        continue

                    obj_type, obj_repr = get_obj_type_and_repr(val)

                    hide_strings_re = self._hide_strings_re
                    if hide_strings_re:
                        obj_repr = hide_strings_re.sub("<redacted>", obj_repr)
                    self._write_with_separator(
                        "TBV ",
                        [
                            oid(str(key)),
                            oid(obj_type),
                            oid(obj_repr),
                        ],
                    )

        stack_entry = self._stack_handler.pop(entry_type, entry_id)
        assert stack_entry

        self._write_with_separator(
            f"{end_message_type} ", [self._number(self.get_time_delta())]
        )

    class _WriteStartElement:
        def __init__(
            self, name, libname, source, lineno, doc, element_type, start_time_delta
        ):
            self.name = name
            self.libname = libname
            self.source = source
            self.lineno = lineno
            self.doc = doc
            self.element_type = element_type
            self.start_time_delta = start_time_delta

        def __call__(self, robot_impl, msg_type):
            oid = robot_impl._obtain_id
            loc_id = robot_impl._obtain_loc_id

            robot_impl._write_with_separator(
                f"{msg_type} ",
                [
                    loc_id(self.name, self.libname, self.source, self.lineno, self.doc),
                    oid(self.element_type),
                    robot_impl._number(self.start_time_delta),
                ],
            )

    def start_element(
        self,
        name: str,
        libname: str,
        element_type: LogElementType,
        doc: str,
        source: str,
        lineno: int,
        start_time_delta: float,
        args: Sequence[Tuple[str, str, str]],
        hide_from_logs: bool,
    ) -> None:
        self._rotate_if_needed()

        from ._null import NULL

        oid = self._obtain_id
        element_id = f"{libname}.{name}"

        ctx: Any = NULL

        if hide_from_logs:
            # I.e.: add to internal stack but don't write it.
            write_it = lambda self, msg_type: None
        else:
            write_it = self._WriteStartElement(
                name, libname, source, lineno, doc, element_type, start_time_delta
            )

        if element_type not in ("UNTRACKED_GENERATOR", "IF", "ELSE"):
            # We don't change the scope for untracked generators as
            # we have no idea when it'll pause/resume.
            self._stack_handler.push_record(
                "element", element_id, "SE", "RE", hide_from_logs, write_it
            )
            if hide_from_logs:
                # I.e.: add to internal stack but don't write anything else.
                return
        else:
            if hide_from_logs:
                # Don't write anything
                return
            # Just write, don't add to stack.
            write_it(self, "SE")

        if args:
            for name, arg_type, arg in args:
                hide_strings_re = self._hide_strings_re
                if hide_strings_re:
                    arg = hide_strings_re.sub("<redacted>", arg)

                self._write_with_separator(
                    "EA ",
                    [
                        oid(name),
                        oid(arg_type),
                        oid(arg),
                    ],
                )

    def end_method(
        self,
        element_type: LogElementType,
        name: str,
        libname: str,
        status: str,
        time_delta: float,
    ):
        element_id = f"{libname}.{name}"

        if element_type != "UNTRACKED_GENERATOR":
            stack_entry = self._stack_handler.pop("element", element_id)
            if stack_entry is None or stack_entry.hide_from_logs:
                # If the start wasn't logged, the stop shouldn't be logged either
                # (and if it was logged, the stop should also be logged).
                return

        oid = self._obtain_id
        self._write_with_separator(
            "EE ",
            [
                oid(element_type),
                oid(status),
                self._number(time_delta),
            ],
        )

    def yield_suspend(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
        yielded_value_type: str,
        yielded_value_repr: str,
        time_delta: float,
    ):
        """
        Note: the yield_suspend is effectively the same thing as the `end_method`
        because we're leaving the method (the difference being that it can be
        resumed afterwards and we have the yielded value right now).
        """

        element_id = f"{libname}.{name}"
        stack_entry = self._stack_handler.pop("element", element_id)
        if stack_entry is None or stack_entry.hide_from_logs:
            # If the start wasn't logged, the stop shouldn't be logged either
            # (and if it was logged, the stop should be also logged).
            return

        self._rotate_if_needed()

        oid = self._obtain_id

        hide_strings_re = self._hide_strings_re
        if hide_strings_re:
            yielded_value_repr = hide_strings_re.sub("<redacted>", yielded_value_repr)

        self._write_with_separator(
            "YS ",
            [
                self._obtain_loc_id(name, libname, source, lineno),
                oid(yielded_value_type),
                oid(yielded_value_repr),
                self._number(time_delta),
            ],
        )

    def method_return(
        self,
        name: str,
        libname: str,
        filename: str,
        lineno: int,
        return_type: str,
        return_repr: str,
        time_delta: float,
    ):
        oid = self._obtain_id

        hide_strings_re = self._hide_strings_re
        if hide_strings_re:
            return_repr = hide_strings_re.sub("<redacted>", return_repr)

        self._write_with_separator(
            "R ",
            [
                self._obtain_loc_id(name, libname, filename, lineno),
                oid(return_type),
                oid(return_repr),
                self._number(time_delta),
            ],
        )

    class _WriteYieldResume:
        def __init__(self, name, libname, source, lineno, time_delta):
            self.name = name
            self.libname = libname
            self.source = source
            self.lineno = lineno
            self.time_delta = time_delta

        def __call__(self, robot_impl, msg_type):
            loc_id = robot_impl._obtain_loc_id
            robot_impl._write_with_separator(
                f"{msg_type} ",
                [
                    loc_id(self.name, self.libname, self.source, self.lineno),
                    robot_impl._number(self.time_delta),
                ],
            )

    def yield_resume(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
        time_delta: float,
        hide_from_logs: bool,
    ):
        """
        Note that a yield resume is semantically very close to a start element
        but it doesn't have any arguments.
        """
        self._rotate_if_needed()

        element_id = f"{libname}.{name}"
        if hide_from_logs:
            write_it = lambda self, msg_type: None
        else:
            write_it = self._WriteYieldResume(name, libname, source, lineno, time_delta)

        self._stack_handler.push_record(
            "element", element_id, "YR", "RYR", hide_from_logs, write_it
        )

    def yield_from_suspend(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
        time_delta: float,
    ):
        """
        Note: the yield_suspend is effectively the same thing as the `end_method`
        because we're leaving the method (the difference being that it can be
        resumed afterwards and we have the yielded value right now).
        """

        element_id = f"{libname}.{name}"
        stack_entry = self._stack_handler.pop("element", element_id)
        if stack_entry is None or stack_entry.hide_from_logs:
            # If the start wasn't logged, the stop shouldn't be logged either
            # (and if it was logged, the stop should be also logged).
            return

        self._rotate_if_needed()

        self._write_with_separator(
            "YFS ",
            [
                self._obtain_loc_id(name, libname, source, lineno),
                self._number(time_delta),
            ],
        )

    class _WriteYieldFromResume:
        def __init__(self, name, libname, source, lineno, time_delta):
            self.name = name
            self.libname = libname
            self.source = source
            self.lineno = lineno
            self.time_delta = time_delta

        def __call__(self, robot_impl, msg_type):
            loc_id = robot_impl._obtain_loc_id
            robot_impl._write_with_separator(
                f"{msg_type} ",
                [
                    loc_id(self.name, self.libname, self.source, self.lineno),
                    robot_impl._number(self.time_delta),
                ],
            )

    def yield_from_resume(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
        time_delta: float,
        hide_from_logs: bool,
    ):
        """
        Note that a yield resume is semantically very close to a start element
        but it doesn't have any arguments.
        """
        self._rotate_if_needed()

        element_id = f"{libname}.{name}"
        if hide_from_logs:
            # I.e.: add to internal stack but don't write it.
            write_it = lambda self, msg_type: None
        else:
            write_it = self._WriteYieldFromResume(
                name, libname, source, lineno, time_delta
            )
        self._stack_handler.push_record(
            "element", element_id, "YFR", "RYFR", hide_from_logs, write_it
        )

    def after_assign(
        self,
        name: str,
        libname: str,
        source: str,
        lineno: int,
        assign_name: str,
        assign_type: str,
        assign_repr: str,
        time_delta: float,
    ):
        self._rotate_if_needed()

        oid = self._obtain_id

        hide_strings_re = self._hide_strings_re
        if hide_strings_re:
            assign_repr = hide_strings_re.sub("<redacted>", assign_repr)

        self._write_with_separator(
            "AS ",
            [
                self._obtain_loc_id(name, libname, source, lineno),
                oid(assign_name),
                oid(assign_type),
                oid(assign_repr),
                self._number(time_delta),
            ],
        )

    def log_message(
        self,
        level: str,
        message: str,
        html: bool,
        name,
        libname,
        source,
        lineno,
        time_delta,
    ) -> None:
        self._rotate_if_needed()
        oid = self._obtain_id

        msg_type = "L "
        if html in ("true", "yes", 1, True):
            # From output.xml it's "true", from listener it's "yes".
            msg_type = "LH "

            hide_strings_re = self._hide_strings_re
            if hide_strings_re:
                message = hide_strings_re.sub("&lt;redacted&gt;", message)
        else:
            hide_strings_re = self._hide_strings_re
            if hide_strings_re:
                message = hide_strings_re.sub("<redacted>", message)

        self._write_with_separator(
            msg_type,
            [
                # ERROR = E
                # FAIL = F
                # INFO = I
                # WARN = W
                level[0].upper(),
                oid(message),
                self._obtain_loc_id(name, libname, source, lineno),
                self._number(lineno),
                self._number(time_delta),
            ],
        )

    def console_message(
        self,
        message: str,
        kind: str,
        time_delta: float,
    ) -> None:
        self._rotate_if_needed()
        hide_strings_re = self._hide_strings_re
        if hide_strings_re:
            message = hide_strings_re.sub("&lt;redacted&gt;", message)

        self._write_with_separator(
            "C ",
            [
                self._obtain_id(kind),
                self._obtain_id(message),
                self._number(time_delta),
            ],
        )

    def close(self):
        if self._closed:
            return

        self._closed = True

        log_html = self._config.log_html
        if log_html:
            target = os.path.abspath(log_html)
            dirname = os.path.dirname(target)
            if not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)
            print(f"Robocorp Log (html): {target}")

            from robocorp.log import _index_v3 as index

            has_separate_bundle_js = "bundle.js" in index.FILE_CONTENTS

            for name, contents in index.FILE_CONTENTS.items():
                if name == "index.html":
                    if has_separate_bundle_js:
                        self._write_simple(target, contents)
                    else:
                        self._write_index_updating_sample(target, contents)
                elif name == "bundle.js":
                    self._write_bundle_updating_sample(
                        os.path.join(dirname, name), contents
                    )
                else:
                    self._write_simple(os.path.join(dirname, name), contents)

    def _write_simple(self, target, contents):
        with open(target, "wb") as stream:
            stream.write(contents.encode("utf-8"))

    def _write_bundle_updating_sample(self, target, contents):
        with open(target, "wb") as stream:
            sample_contents_index = contents.index("function getSampleContents() {")

            return_json_parse_index = contents.index(
                "return JSON.parse", sample_contents_index
            )
            assert return_json_parse_index > 0

            end_of_json_parse_index = contents.index("\n}", return_json_parse_index) + 1
            assert end_of_json_parse_index > 0
            self._write_updating_sample(
                stream, contents, return_json_parse_index, end_of_json_parse_index
            )

    def _write_index_updating_sample(self, target, contents):
        with open(target, "wb") as stream:
            string_start = contents.index("String.raw`V 0.0.2")
            string_end = contents.index("`", string_start + 18)
            string_end = contents.index("}", string_end)

            assert string_start > 0, f'Could not find "String.raw`V 0.0.2" in {target}.'
            assert string_end > 0, f"Could not find the string end in {target}."

            # Now, go a bit back in the string and find the `const XXX=` to also remove that.
            i = string_start
            found = []
            while i > 0:
                c = contents[i]
                found.insert(0, c)

                if "".join(found).startswith("const "):
                    string_start = i
                    break
                i -= 1

            self._write_updating_sample(stream, contents, string_start, string_end)

    def _write_updating_sample(self, stream, contents, start_index, end_index):
        import base64

        stream.write(contents[:start_index].encode("utf-8"))

        import zlib

        write = stream.write
        if WRITE_CONTENTS_TO_STDERR:
            stream_write = write

            def write(b):
                stream_write(b)
                sys.stderr.buffer.write(b)

        write(b"\nlet chunks = [")
        for f in self._rotate_handler.iter_found_files():
            with open(f, "rb") as fsrc:
                while True:
                    chunk = fsrc.read(1024 * 8)
                    if not chunk:
                        break
                    write(b'"')
                    chunk = zlib.compress(chunk)
                    write(base64.b64encode(chunk))
                    write(b'",\n')
        write(b"];\n")

        # Add code to decompress the data we added.
        write(
            b"""
/*! pako 2.1.0 https://github.com/nodeca/pako @license (MIT AND Zlib) */
!function(e,t){"object"==typeof exports&&"undefined"!=typeof module?t(exports):"function"==typeof define&&define.amd?define(["exports"],t):t((e="undefined"!=typeof globalThis?globalThis:e||self).pako={})}(this,(function(e){"use strict";var t=(e,t,i,n)=>{let a=65535&e|0,r=e>>>16&65535|0,o=0;for(;0!==i;){o=i>2e3?2e3:i,i-=o;do{a=a+t[n++]|0,r=r+a|0}while(--o);a%=65521,r%=65521}return a|r<<16|0};const i=new Uint32Array((()=>{let e,t=[];for(var i=0;i<256;i++){e=i;for(var n=0;n<8;n++)e=1&e?3988292384^e>>>1:e>>>1;t[i]=e}return t})());var n=(e,t,n,a)=>{const r=i,o=a+n;e^=-1;for(let i=a;i<o;i++)e=e>>>8^r[255&(e^t[i])];return-1^e};const a=16209;var r=function(e,t){let i,n,r,o,s,l,d,f,c,h,u,w,b,m,k,_,g,p,v,x,y,E,R,A;const Z=e.state;i=e.next_in,R=e.input,n=i+(e.avail_in-5),r=e.next_out,A=e.output,o=r-(t-e.avail_out),s=r+(e.avail_out-257),l=Z.dmax,d=Z.wsize,f=Z.whave,c=Z.wnext,h=Z.window,u=Z.hold,w=Z.bits,b=Z.lencode,m=Z.distcode,k=(1<<Z.lenbits)-1,_=(1<<Z.distbits)-1;e:do{w<15&&(u+=R[i++]<<w,w+=8,u+=R[i++]<<w,w+=8),g=b[u&k];t:for(;;){if(p=g>>>24,u>>>=p,w-=p,p=g>>>16&255,0===p)A[r++]=65535&g;else{if(!(16&p)){if(0==(64&p)){g=b[(65535&g)+(u&(1<<p)-1)];continue t}if(32&p){Z.mode=16191;break e}e.msg="invalid literal/length code",Z.mode=a;break e}v=65535&g,p&=15,p&&(w<p&&(u+=R[i++]<<w,w+=8),v+=u&(1<<p)-1,u>>>=p,w-=p),w<15&&(u+=R[i++]<<w,w+=8,u+=R[i++]<<w,w+=8),g=m[u&_];i:for(;;){if(p=g>>>24,u>>>=p,w-=p,p=g>>>16&255,!(16&p)){if(0==(64&p)){g=m[(65535&g)+(u&(1<<p)-1)];continue i}e.msg="invalid distance code",Z.mode=a;break e}if(x=65535&g,p&=15,w<p&&(u+=R[i++]<<w,w+=8,w<p&&(u+=R[i++]<<w,w+=8)),x+=u&(1<<p)-1,x>l){e.msg="invalid distance too far back",Z.mode=a;break e}if(u>>>=p,w-=p,p=r-o,x>p){if(p=x-p,p>f&&Z.sane){e.msg="invalid distance too far back",Z.mode=a;break e}if(y=0,E=h,0===c){if(y+=d-p,p<v){v-=p;do{A[r++]=h[y++]}while(--p);y=r-x,E=A}}else if(c<p){if(y+=d+c-p,p-=c,p<v){v-=p;do{A[r++]=h[y++]}while(--p);if(y=0,c<v){p=c,v-=p;do{A[r++]=h[y++]}while(--p);y=r-x,E=A}}}else if(y+=c-p,p<v){v-=p;do{A[r++]=h[y++]}while(--p);y=r-x,E=A}for(;v>2;)A[r++]=E[y++],A[r++]=E[y++],A[r++]=E[y++],v-=3;v&&(A[r++]=E[y++],v>1&&(A[r++]=E[y++]))}else{y=r-x;do{A[r++]=A[y++],A[r++]=A[y++],A[r++]=A[y++],v-=3}while(v>2);v&&(A[r++]=A[y++],v>1&&(A[r++]=A[y++]))}break}}break}}while(i<n&&r<s);v=w>>3,i-=v,w-=v<<3,u&=(1<<w)-1,e.next_in=i,e.next_out=r,e.avail_in=i<n?n-i+5:5-(i-n),e.avail_out=r<s?s-r+257:257-(r-s),Z.hold=u,Z.bits=w};const o=15,s=new Uint16Array([3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258,0,0]),l=new Uint8Array([16,16,16,16,16,16,16,16,17,17,17,17,18,18,18,18,19,19,19,19,20,20,20,20,21,21,21,21,16,72,78]),d=new Uint16Array([1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577,0,0]),f=new Uint8Array([16,16,16,16,17,17,18,18,19,19,20,20,21,21,22,22,23,23,24,24,25,25,26,26,27,27,28,28,29,29,64,64]);var c=(e,t,i,n,a,r,c,h)=>{const u=h.bits;let w,b,m,k,_,g,p=0,v=0,x=0,y=0,E=0,R=0,A=0,Z=0,S=0,T=0,O=null;const U=new Uint16Array(16),D=new Uint16Array(16);let I,B,N,C=null;for(p=0;p<=o;p++)U[p]=0;for(v=0;v<n;v++)U[t[i+v]]++;for(E=u,y=o;y>=1&&0===U[y];y--);if(E>y&&(E=y),0===y)return a[r++]=20971520,a[r++]=20971520,h.bits=1,0;for(x=1;x<y&&0===U[x];x++);for(E<x&&(E=x),Z=1,p=1;p<=o;p++)if(Z<<=1,Z-=U[p],Z<0)return-1;if(Z>0&&(0===e||1!==y))return-1;for(D[1]=0,p=1;p<o;p++)D[p+1]=D[p]+U[p];for(v=0;v<n;v++)0!==t[i+v]&&(c[D[t[i+v]]++]=v);if(0===e?(O=C=c,g=20):1===e?(O=s,C=l,g=257):(O=d,C=f,g=0),T=0,v=0,p=x,_=r,R=E,A=0,m=-1,S=1<<E,k=S-1,1===e&&S>852||2===e&&S>592)return 1;for(;;){I=p-A,c[v]+1<g?(B=0,N=c[v]):c[v]>=g?(B=C[c[v]-g],N=O[c[v]-g]):(B=96,N=0),w=1<<p-A,b=1<<R,x=b;do{b-=w,a[_+(T>>A)+b]=I<<24|B<<16|N|0}while(0!==b);for(w=1<<p-1;T&w;)w>>=1;if(0!==w?(T&=w-1,T+=w):T=0,v++,0==--U[p]){if(p===y)break;p=t[i+c[v]]}if(p>E&&(T&k)!==m){for(0===A&&(A=E),_+=x,R=p-A,Z=1<<R;R+A<y&&(Z-=U[R+A],!(Z<=0));)R++,Z<<=1;if(S+=1<<R,1===e&&S>852||2===e&&S>592)return 1;m=T&k,a[m]=E<<24|R<<16|_-r|0}}return 0!==T&&(a[_+T]=p-A<<24|64<<16|0),h.bits=E,0},h={Z_NO_FLUSH:0,Z_PARTIAL_FLUSH:1,Z_SYNC_FLUSH:2,Z_FULL_FLUSH:3,Z_FINISH:4,Z_BLOCK:5,Z_TREES:6,Z_OK:0,Z_STREAM_END:1,Z_NEED_DICT:2,Z_ERRNO:-1,Z_STREAM_ERROR:-2,Z_DATA_ERROR:-3,Z_MEM_ERROR:-4,Z_BUF_ERROR:-5,Z_NO_COMPRESSION:0,Z_BEST_SPEED:1,Z_BEST_COMPRESSION:9,Z_DEFAULT_COMPRESSION:-1,Z_FILTERED:1,Z_HUFFMAN_ONLY:2,Z_RLE:3,Z_FIXED:4,Z_DEFAULT_STRATEGY:0,Z_BINARY:0,Z_TEXT:1,Z_UNKNOWN:2,Z_DEFLATED:8};const{Z_FINISH:u,Z_BLOCK:w,Z_TREES:b,Z_OK:m,Z_STREAM_END:k,Z_NEED_DICT:_,Z_STREAM_ERROR:g,Z_DATA_ERROR:p,Z_MEM_ERROR:v,Z_BUF_ERROR:x,Z_DEFLATED:y}=h,E=16180,R=16190,A=16191,Z=16192,S=16194,T=16199,O=16200,U=16206,D=16209,I=e=>(e>>>24&255)+(e>>>8&65280)+((65280&e)<<8)+((255&e)<<24);function B(){this.strm=null,this.mode=0,this.last=!1,this.wrap=0,this.havedict=!1,this.flags=0,this.dmax=0,this.check=0,this.total=0,this.head=null,this.wbits=0,this.wsize=0,this.whave=0,this.wnext=0,this.window=null,this.hold=0,this.bits=0,this.length=0,this.offset=0,this.extra=0,this.lencode=null,this.distcode=null,this.lenbits=0,this.distbits=0,this.ncode=0,this.nlen=0,this.ndist=0,this.have=0,this.next=null,this.lens=new Uint16Array(320),this.work=new Uint16Array(288),this.lendyn=null,this.distdyn=null,this.sane=0,this.back=0,this.was=0}const N=e=>{if(!e)return 1;const t=e.state;return!t||t.strm!==e||t.mode<E||t.mode>16211?1:0},C=e=>{if(N(e))return g;const t=e.state;return e.total_in=e.total_out=t.total=0,e.msg="",t.wrap&&(e.adler=1&t.wrap),t.mode=E,t.last=0,t.havedict=0,t.flags=-1,t.dmax=32768,t.head=null,t.hold=0,t.bits=0,t.lencode=t.lendyn=new Int32Array(852),t.distcode=t.distdyn=new Int32Array(592),t.sane=1,t.back=-1,m},z=e=>{if(N(e))return g;const t=e.state;return t.wsize=0,t.whave=0,t.wnext=0,C(e)},F=(e,t)=>{let i;if(N(e))return g;const n=e.state;return t<0?(i=0,t=-t):(i=5+(t>>4),t<48&&(t&=15)),t&&(t<8||t>15)?g:(null!==n.window&&n.wbits!==t&&(n.window=null),n.wrap=i,n.wbits=t,z(e))},L=(e,t)=>{if(!e)return g;const i=new B;e.state=i,i.strm=e,i.window=null,i.mode=E;const n=F(e,t);return n!==m&&(e.state=null),n};let M,H,j=!0;const K=e=>{if(j){M=new Int32Array(512),H=new Int32Array(32);let t=0;for(;t<144;)e.lens[t++]=8;for(;t<256;)e.lens[t++]=9;for(;t<280;)e.lens[t++]=7;for(;t<288;)e.lens[t++]=8;for(c(1,e.lens,0,288,M,0,e.work,{bits:9}),t=0;t<32;)e.lens[t++]=5;c(2,e.lens,0,32,H,0,e.work,{bits:5}),j=!1}e.lencode=M,e.lenbits=9,e.distcode=H,e.distbits=5},P=(e,t,i,n)=>{let a;const r=e.state;return null===r.window&&(r.wsize=1<<r.wbits,r.wnext=0,r.whave=0,r.window=new Uint8Array(r.wsize)),n>=r.wsize?(r.window.set(t.subarray(i-r.wsize,i),0),r.wnext=0,r.whave=r.wsize):(a=r.wsize-r.wnext,a>n&&(a=n),r.window.set(t.subarray(i-n,i-n+a),r.wnext),(n-=a)?(r.window.set(t.subarray(i-n,i),0),r.wnext=n,r.whave=r.wsize):(r.wnext+=a,r.wnext===r.wsize&&(r.wnext=0),r.whave<r.wsize&&(r.whave+=a))),0};var Y={inflateReset:z,inflateReset2:F,inflateResetKeep:C,inflateInit:e=>L(e,15),inflateInit2:L,inflate:(e,i)=>{let a,o,s,l,d,f,h,B,C,z,F,L,M,H,j,Y,G,X,W,q,J,Q,V=0;const $=new Uint8Array(4);let ee,te;const ie=new Uint8Array([16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]);if(N(e)||!e.output||!e.input&&0!==e.avail_in)return g;a=e.state,a.mode===A&&(a.mode=Z),d=e.next_out,s=e.output,h=e.avail_out,l=e.next_in,o=e.input,f=e.avail_in,B=a.hold,C=a.bits,z=f,F=h,Q=m;e:for(;;)switch(a.mode){case E:if(0===a.wrap){a.mode=Z;break}for(;C<16;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if(2&a.wrap&&35615===B){0===a.wbits&&(a.wbits=15),a.check=0,$[0]=255&B,$[1]=B>>>8&255,a.check=n(a.check,$,2,0),B=0,C=0,a.mode=16181;break}if(a.head&&(a.head.done=!1),!(1&a.wrap)||(((255&B)<<8)+(B>>8))%31){e.msg="incorrect header check",a.mode=D;break}if((15&B)!==y){e.msg="unknown compression method",a.mode=D;break}if(B>>>=4,C-=4,J=8+(15&B),0===a.wbits&&(a.wbits=J),J>15||J>a.wbits){e.msg="invalid window size",a.mode=D;break}a.dmax=1<<a.wbits,a.flags=0,e.adler=a.check=1,a.mode=512&B?16189:A,B=0,C=0;break;case 16181:for(;C<16;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if(a.flags=B,(255&a.flags)!==y){e.msg="unknown compression method",a.mode=D;break}if(57344&a.flags){e.msg="unknown header flags set",a.mode=D;break}a.head&&(a.head.text=B>>8&1),512&a.flags&&4&a.wrap&&($[0]=255&B,$[1]=B>>>8&255,a.check=n(a.check,$,2,0)),B=0,C=0,a.mode=16182;case 16182:for(;C<32;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}a.head&&(a.head.time=B),512&a.flags&&4&a.wrap&&($[0]=255&B,$[1]=B>>>8&255,$[2]=B>>>16&255,$[3]=B>>>24&255,a.check=n(a.check,$,4,0)),B=0,C=0,a.mode=16183;case 16183:for(;C<16;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}a.head&&(a.head.xflags=255&B,a.head.os=B>>8),512&a.flags&&4&a.wrap&&($[0]=255&B,$[1]=B>>>8&255,a.check=n(a.check,$,2,0)),B=0,C=0,a.mode=16184;case 16184:if(1024&a.flags){for(;C<16;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}a.length=B,a.head&&(a.head.extra_len=B),512&a.flags&&4&a.wrap&&($[0]=255&B,$[1]=B>>>8&255,a.check=n(a.check,$,2,0)),B=0,C=0}else a.head&&(a.head.extra=null);a.mode=16185;case 16185:if(1024&a.flags&&(L=a.length,L>f&&(L=f),L&&(a.head&&(J=a.head.extra_len-a.length,a.head.extra||(a.head.extra=new Uint8Array(a.head.extra_len)),a.head.extra.set(o.subarray(l,l+L),J)),512&a.flags&&4&a.wrap&&(a.check=n(a.check,o,L,l)),f-=L,l+=L,a.length-=L),a.length))break e;a.length=0,a.mode=16186;case 16186:if(2048&a.flags){if(0===f)break e;L=0;do{J=o[l+L++],a.head&&J&&a.length<65536&&(a.head.name+=String.fromCharCode(J))}while(J&&L<f);if(512&a.flags&&4&a.wrap&&(a.check=n(a.check,o,L,l)),f-=L,l+=L,J)break e}else a.head&&(a.head.name=null);a.length=0,a.mode=16187;case 16187:if(4096&a.flags){if(0===f)break e;L=0;do{J=o[l+L++],a.head&&J&&a.length<65536&&(a.head.comment+=String.fromCharCode(J))}while(J&&L<f);if(512&a.flags&&4&a.wrap&&(a.check=n(a.check,o,L,l)),f-=L,l+=L,J)break e}else a.head&&(a.head.comment=null);a.mode=16188;case 16188:if(512&a.flags){for(;C<16;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if(4&a.wrap&&B!==(65535&a.check)){e.msg="header crc mismatch",a.mode=D;break}B=0,C=0}a.head&&(a.head.hcrc=a.flags>>9&1,a.head.done=!0),e.adler=a.check=0,a.mode=A;break;case 16189:for(;C<32;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}e.adler=a.check=I(B),B=0,C=0,a.mode=R;case R:if(0===a.havedict)return e.next_out=d,e.avail_out=h,e.next_in=l,e.avail_in=f,a.hold=B,a.bits=C,_;e.adler=a.check=1,a.mode=A;case A:if(i===w||i===b)break e;case Z:if(a.last){B>>>=7&C,C-=7&C,a.mode=U;break}for(;C<3;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}switch(a.last=1&B,B>>>=1,C-=1,3&B){case 0:a.mode=16193;break;case 1:if(K(a),a.mode=T,i===b){B>>>=2,C-=2;break e}break;case 2:a.mode=16196;break;case 3:e.msg="invalid block type",a.mode=D}B>>>=2,C-=2;break;case 16193:for(B>>>=7&C,C-=7&C;C<32;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if((65535&B)!=(B>>>16^65535)){e.msg="invalid stored block lengths",a.mode=D;break}if(a.length=65535&B,B=0,C=0,a.mode=S,i===b)break e;case S:a.mode=16195;case 16195:if(L=a.length,L){if(L>f&&(L=f),L>h&&(L=h),0===L)break e;s.set(o.subarray(l,l+L),d),f-=L,l+=L,h-=L,d+=L,a.length-=L;break}a.mode=A;break;case 16196:for(;C<14;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if(a.nlen=257+(31&B),B>>>=5,C-=5,a.ndist=1+(31&B),B>>>=5,C-=5,a.ncode=4+(15&B),B>>>=4,C-=4,a.nlen>286||a.ndist>30){e.msg="too many length or distance symbols",a.mode=D;break}a.have=0,a.mode=16197;case 16197:for(;a.have<a.ncode;){for(;C<3;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}a.lens[ie[a.have++]]=7&B,B>>>=3,C-=3}for(;a.have<19;)a.lens[ie[a.have++]]=0;if(a.lencode=a.lendyn,a.lenbits=7,ee={bits:a.lenbits},Q=c(0,a.lens,0,19,a.lencode,0,a.work,ee),a.lenbits=ee.bits,Q){e.msg="invalid code lengths set",a.mode=D;break}a.have=0,a.mode=16198;case 16198:for(;a.have<a.nlen+a.ndist;){for(;V=a.lencode[B&(1<<a.lenbits)-1],j=V>>>24,Y=V>>>16&255,G=65535&V,!(j<=C);){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if(G<16)B>>>=j,C-=j,a.lens[a.have++]=G;else{if(16===G){for(te=j+2;C<te;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if(B>>>=j,C-=j,0===a.have){e.msg="invalid bit length repeat",a.mode=D;break}J=a.lens[a.have-1],L=3+(3&B),B>>>=2,C-=2}else if(17===G){for(te=j+3;C<te;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}B>>>=j,C-=j,J=0,L=3+(7&B),B>>>=3,C-=3}else{for(te=j+7;C<te;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}B>>>=j,C-=j,J=0,L=11+(127&B),B>>>=7,C-=7}if(a.have+L>a.nlen+a.ndist){e.msg="invalid bit length repeat",a.mode=D;break}for(;L--;)a.lens[a.have++]=J}}if(a.mode===D)break;if(0===a.lens[256]){e.msg="invalid code -- missing end-of-block",a.mode=D;break}if(a.lenbits=9,ee={bits:a.lenbits},Q=c(1,a.lens,0,a.nlen,a.lencode,0,a.work,ee),a.lenbits=ee.bits,Q){e.msg="invalid literal/lengths set",a.mode=D;break}if(a.distbits=6,a.distcode=a.distdyn,ee={bits:a.distbits},Q=c(2,a.lens,a.nlen,a.ndist,a.distcode,0,a.work,ee),a.distbits=ee.bits,Q){e.msg="invalid distances set",a.mode=D;break}if(a.mode=T,i===b)break e;case T:a.mode=O;case O:if(f>=6&&h>=258){e.next_out=d,e.avail_out=h,e.next_in=l,e.avail_in=f,a.hold=B,a.bits=C,r(e,F),d=e.next_out,s=e.output,h=e.avail_out,l=e.next_in,o=e.input,f=e.avail_in,B=a.hold,C=a.bits,a.mode===A&&(a.back=-1);break}for(a.back=0;V=a.lencode[B&(1<<a.lenbits)-1],j=V>>>24,Y=V>>>16&255,G=65535&V,!(j<=C);){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if(Y&&0==(240&Y)){for(X=j,W=Y,q=G;V=a.lencode[q+((B&(1<<X+W)-1)>>X)],j=V>>>24,Y=V>>>16&255,G=65535&V,!(X+j<=C);){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}B>>>=X,C-=X,a.back+=X}if(B>>>=j,C-=j,a.back+=j,a.length=G,0===Y){a.mode=16205;break}if(32&Y){a.back=-1,a.mode=A;break}if(64&Y){e.msg="invalid literal/length code",a.mode=D;break}a.extra=15&Y,a.mode=16201;case 16201:if(a.extra){for(te=a.extra;C<te;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}a.length+=B&(1<<a.extra)-1,B>>>=a.extra,C-=a.extra,a.back+=a.extra}a.was=a.length,a.mode=16202;case 16202:for(;V=a.distcode[B&(1<<a.distbits)-1],j=V>>>24,Y=V>>>16&255,G=65535&V,!(j<=C);){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if(0==(240&Y)){for(X=j,W=Y,q=G;V=a.distcode[q+((B&(1<<X+W)-1)>>X)],j=V>>>24,Y=V>>>16&255,G=65535&V,!(X+j<=C);){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}B>>>=X,C-=X,a.back+=X}if(B>>>=j,C-=j,a.back+=j,64&Y){e.msg="invalid distance code",a.mode=D;break}a.offset=G,a.extra=15&Y,a.mode=16203;case 16203:if(a.extra){for(te=a.extra;C<te;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}a.offset+=B&(1<<a.extra)-1,B>>>=a.extra,C-=a.extra,a.back+=a.extra}if(a.offset>a.dmax){e.msg="invalid distance too far back",a.mode=D;break}a.mode=16204;case 16204:if(0===h)break e;if(L=F-h,a.offset>L){if(L=a.offset-L,L>a.whave&&a.sane){e.msg="invalid distance too far back",a.mode=D;break}L>a.wnext?(L-=a.wnext,M=a.wsize-L):M=a.wnext-L,L>a.length&&(L=a.length),H=a.window}else H=s,M=d-a.offset,L=a.length;L>h&&(L=h),h-=L,a.length-=L;do{s[d++]=H[M++]}while(--L);0===a.length&&(a.mode=O);break;case 16205:if(0===h)break e;s[d++]=a.length,h--,a.mode=O;break;case U:if(a.wrap){for(;C<32;){if(0===f)break e;f--,B|=o[l++]<<C,C+=8}if(F-=h,e.total_out+=F,a.total+=F,4&a.wrap&&F&&(e.adler=a.check=a.flags?n(a.check,s,F,d-F):t(a.check,s,F,d-F)),F=h,4&a.wrap&&(a.flags?B:I(B))!==a.check){e.msg="incorrect data check",a.mode=D;break}B=0,C=0}a.mode=16207;case 16207:if(a.wrap&&a.flags){for(;C<32;){if(0===f)break e;f--,B+=o[l++]<<C,C+=8}if(4&a.wrap&&B!==(4294967295&a.total)){e.msg="incorrect length check",a.mode=D;break}B=0,C=0}a.mode=16208;case 16208:Q=k;break e;case D:Q=p;break e;case 16210:return v;default:return g}return e.next_out=d,e.avail_out=h,e.next_in=l,e.avail_in=f,a.hold=B,a.bits=C,(a.wsize||F!==e.avail_out&&a.mode<D&&(a.mode<U||i!==u))&&P(e,e.output,e.next_out,F-e.avail_out),z-=e.avail_in,F-=e.avail_out,e.total_in+=z,e.total_out+=F,a.total+=F,4&a.wrap&&F&&(e.adler=a.check=a.flags?n(a.check,s,F,e.next_out-F):t(a.check,s,F,e.next_out-F)),e.data_type=a.bits+(a.last?64:0)+(a.mode===A?128:0)+(a.mode===T||a.mode===S?256:0),(0===z&&0===F||i===u)&&Q===m&&(Q=x),Q},inflateEnd:e=>{if(N(e))return g;let t=e.state;return t.window&&(t.window=null),e.state=null,m},inflateGetHeader:(e,t)=>{if(N(e))return g;const i=e.state;return 0==(2&i.wrap)?g:(i.head=t,t.done=!1,m)},inflateSetDictionary:(e,i)=>{const n=i.length;let a,r,o;return N(e)?g:(a=e.state,0!==a.wrap&&a.mode!==R?g:a.mode===R&&(r=1,r=t(r,i,n,0),r!==a.check)?p:(o=P(e,i,n,n),o?(a.mode=16210,v):(a.havedict=1,m)))},inflateInfo:"pako inflate (from Nodeca project)"};const G=(e,t)=>Object.prototype.hasOwnProperty.call(e,t);var X=function(e){const t=Array.prototype.slice.call(arguments,1);for(;t.length;){const i=t.shift();if(i){if("object"!=typeof i)throw new TypeError(i+"must be non-object");for(const t in i)G(i,t)&&(e[t]=i[t])}}return e},W=e=>{let t=0;for(let i=0,n=e.length;i<n;i++)t+=e[i].length;const i=new Uint8Array(t);for(let t=0,n=0,a=e.length;t<a;t++){let a=e[t];i.set(a,n),n+=a.length}return i};let q=!0;try{String.fromCharCode.apply(null,new Uint8Array(1))}catch(e){q=!1}const J=new Uint8Array(256);for(let e=0;e<256;e++)J[e]=e>=252?6:e>=248?5:e>=240?4:e>=224?3:e>=192?2:1;J[254]=J[254]=1;var Q=e=>{if("function"==typeof TextEncoder&&TextEncoder.prototype.encode)return(new TextEncoder).encode(e);let t,i,n,a,r,o=e.length,s=0;for(a=0;a<o;a++)i=e.charCodeAt(a),55296==(64512&i)&&a+1<o&&(n=e.charCodeAt(a+1),56320==(64512&n)&&(i=65536+(i-55296<<10)+(n-56320),a++)),s+=i<128?1:i<2048?2:i<65536?3:4;for(t=new Uint8Array(s),r=0,a=0;r<s;a++)i=e.charCodeAt(a),55296==(64512&i)&&a+1<o&&(n=e.charCodeAt(a+1),56320==(64512&n)&&(i=65536+(i-55296<<10)+(n-56320),a++)),i<128?t[r++]=i:i<2048?(t[r++]=192|i>>>6,t[r++]=128|63&i):i<65536?(t[r++]=224|i>>>12,t[r++]=128|i>>>6&63,t[r++]=128|63&i):(t[r++]=240|i>>>18,t[r++]=128|i>>>12&63,t[r++]=128|i>>>6&63,t[r++]=128|63&i);return t},V=(e,t)=>{const i=t||e.length;if("function"==typeof TextDecoder&&TextDecoder.prototype.decode)return(new TextDecoder).decode(e.subarray(0,t));let n,a;const r=new Array(2*i);for(a=0,n=0;n<i;){let t=e[n++];if(t<128){r[a++]=t;continue}let o=J[t];if(o>4)r[a++]=65533,n+=o-1;else{for(t&=2===o?31:3===o?15:7;o>1&&n<i;)t=t<<6|63&e[n++],o--;o>1?r[a++]=65533:t<65536?r[a++]=t:(t-=65536,r[a++]=55296|t>>10&1023,r[a++]=56320|1023&t)}}return((e,t)=>{if(t<65534&&e.subarray&&q)return String.fromCharCode.apply(null,e.length===t?e:e.subarray(0,t));let i="";for(let n=0;n<t;n++)i+=String.fromCharCode(e[n]);return i})(r,a)},$=(e,t)=>{(t=t||e.length)>e.length&&(t=e.length);let i=t-1;for(;i>=0&&128==(192&e[i]);)i--;return i<0||0===i?t:i+J[e[i]]>t?i:t},ee={2:"need dictionary",1:"stream end",0:"","-1":"file error","-2":"stream error","-3":"data error","-4":"insufficient memory","-5":"buffer error","-6":"incompatible version"};var te=function(){this.input=null,this.next_in=0,this.avail_in=0,this.total_in=0,this.output=null,this.next_out=0,this.avail_out=0,this.total_out=0,this.msg="",this.state=null,this.data_type=2,this.adler=0};var ie=function(){this.text=0,this.time=0,this.xflags=0,this.os=0,this.extra=null,this.extra_len=0,this.name="",this.comment="",this.hcrc=0,this.done=!1};const ne=Object.prototype.toString,{Z_NO_FLUSH:ae,Z_FINISH:re,Z_OK:oe,Z_STREAM_END:se,Z_NEED_DICT:le,Z_STREAM_ERROR:de,Z_DATA_ERROR:fe,Z_MEM_ERROR:ce}=h;function he(e){this.options=X({chunkSize:65536,windowBits:15,to:""},e||{});const t=this.options;t.raw&&t.windowBits>=0&&t.windowBits<16&&(t.windowBits=-t.windowBits,0===t.windowBits&&(t.windowBits=-15)),!(t.windowBits>=0&&t.windowBits<16)||e&&e.windowBits||(t.windowBits+=32),t.windowBits>15&&t.windowBits<48&&0==(15&t.windowBits)&&(t.windowBits|=15),this.err=0,this.msg="",this.ended=!1,this.chunks=[],this.strm=new te,this.strm.avail_out=0;let i=Y.inflateInit2(this.strm,t.windowBits);if(i!==oe)throw new Error(ee[i]);if(this.header=new ie,Y.inflateGetHeader(this.strm,this.header),t.dictionary&&("string"==typeof t.dictionary?t.dictionary=Q(t.dictionary):"[object ArrayBuffer]"===ne.call(t.dictionary)&&(t.dictionary=new Uint8Array(t.dictionary)),t.raw&&(i=Y.inflateSetDictionary(this.strm,t.dictionary),i!==oe)))throw new Error(ee[i])}function ue(e,t){const i=new he(t);if(i.push(e),i.err)throw i.msg||ee[i.err];return i.result}he.prototype.push=function(e,t){const i=this.strm,n=this.options.chunkSize,a=this.options.dictionary;let r,o,s;if(this.ended)return!1;for(o=t===~~t?t:!0===t?re:ae,"[object ArrayBuffer]"===ne.call(e)?i.input=new Uint8Array(e):i.input=e,i.next_in=0,i.avail_in=i.input.length;;){for(0===i.avail_out&&(i.output=new Uint8Array(n),i.next_out=0,i.avail_out=n),r=Y.inflate(i,o),r===le&&a&&(r=Y.inflateSetDictionary(i,a),r===oe?r=Y.inflate(i,o):r===fe&&(r=le));i.avail_in>0&&r===se&&i.state.wrap>0&&0!==e[i.next_in];)Y.inflateReset(i),r=Y.inflate(i,o);switch(r){case de:case fe:case le:case ce:return this.onEnd(r),this.ended=!0,!1}if(s=i.avail_out,i.next_out&&(0===i.avail_out||r===se))if("string"===this.options.to){let e=$(i.output,i.next_out),t=i.next_out-e,a=V(i.output,e);i.next_out=t,i.avail_out=n-t,t&&i.output.set(i.output.subarray(e,e+t),0),this.onData(a)}else this.onData(i.output.length===i.next_out?i.output:i.output.subarray(0,i.next_out));if(r!==oe||0!==s){if(r===se)return r=Y.inflateEnd(this.strm),this.onEnd(r),this.ended=!0,!0;if(0===i.avail_in)break}}return!0},he.prototype.onData=function(e){this.chunks.push(e)},he.prototype.onEnd=function(e){e===oe&&("string"===this.options.to?this.result=this.chunks.join(""):this.result=W(this.chunks)),this.chunks=[],this.err=e,this.msg=this.strm.msg};var we=he,be=ue,me=function(e,t){return(t=t||{}).raw=!0,ue(e,t)},ke=ue,_e=h,ge={Inflate:we,inflate:be,inflateRaw:me,ungzip:ke,constants:_e};e.Inflate=we,e.constants=_e,e.default=ge,e.inflate=be,e.inflateRaw=me,e.ungzip=ke,Object.defineProperty(e,"__esModule",{value:!0})}));

function fromZippedBase64(s) {
    let binary = atob(s);
    
    let bytesCompressed = new Uint8Array(binary.length);
    for (let i = 0; i < bytesCompressed.length; i++) {
        bytesCompressed[i] = binary.charCodeAt(i);
    }
    let inflated = pako.inflate(bytesCompressed);
    return inflated;
}


let size = 0;
let result = [];
for (const chunk of chunks) {
    const arr = fromZippedBase64(chunk);
    result.push(arr);
    size += arr.length;
}

let mergedArray = new Uint8Array(size);
let offset = 0;
for(const item of result){
    mergedArray.set(item, offset);
    offset += item.length;
}

return new TextDecoder().decode(mergedArray);
"""
        )

        stream.write(contents[end_index:].encode("utf-8"))
