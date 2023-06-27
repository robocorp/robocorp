import os
import subprocess
import sys
import typing
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional

import pytest

from robocorp.log import AutoLogConfigBase, FilterKind
from robocorp.log.protocols import IReadLines, LogHTMLStyle


class _SetupInfo:
    def __init__(self, log_target):
        self.log_target = log_target

    def open_log_target(self):
        import webbrowser

        webbrowser.open(self.log_target.as_uri())


class UIRegenerateFixture:
    # Must be set to False when merging to master and
    # inv build-output-view-react
    # must also be manually called afterwards.
    FORCE_REGEN: List[typing.Union[str, int]] = []

    OPEN_IN_BROWSER = False

    PRINT_MESSAGES = False

    LOG_HTML_STYLE: LogHTMLStyle = "standalone"

    def regenerate(self) -> None:
        if not self.FORCE_REGEN:
            return

        cwd = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        cmd = [sys.executable, "-m", "invoke", "build-output-view-react"]

        subprocess.check_call(cmd, cwd=cwd)


@pytest.fixture
def ui_regenerate():
    DEFAULT = False

    # Flags to be changed (keep to False in repository).

    # Set to True to get new contents to be added to `samples.ts / getSampleContents()`.
    PRINT_SAMPLE_CONTENTS = DEFAULT

    # Set to True to regenerate the html.
    REGEN = DEFAULT

    # Set to True open test result in browser
    OPEN_IN_BROWSER = DEFAULT

    # Set to True to print messages found.
    PRINT_MESSAGES = DEFAULT

    # --- Implementation
    if PRINT_SAMPLE_CONTENTS:
        from robocorp.log import _robo_output_impl

        _robo_output_impl.WRITE_CONTENTS_TO_STDERR = True

    uiregenerate_fixture = UIRegenerateFixture()

    if OPEN_IN_BROWSER:
        uiregenerate_fixture.OPEN_IN_BROWSER = True

    if REGEN:
        # LOG_HTML_STYLE = "vscode"
        uiregenerate_fixture.LOG_HTML_STYLE = "standalone"

        uiregenerate_fixture.FORCE_REGEN.append("dev")

    uiregenerate_fixture.PRINT_MESSAGES = PRINT_MESSAGES

    matrix_name = os.environ.get("GITHUB_ACTIONS_MATRIX_NAME")
    if matrix_name:
        if (
            DEFAULT
            or PRINT_SAMPLE_CONTENTS
            or REGEN
            or OPEN_IN_BROWSER
            or PRINT_MESSAGES
        ):
            raise AssertionError("Expected all flags to be False in the CI.")

    uiregenerate_fixture.regenerate()
    return uiregenerate_fixture


@contextmanager
def basic_log_setup(
    tmpdir, max_file_size="1MB", max_files=5, config: Optional[AutoLogConfigBase] = None
):
    from robocorp import log

    log_target = Path(tmpdir.join("log.html"))

    with log.setup_auto_logging(config):
        with log.add_log_output(
            tmpdir,
            max_file_size=max_file_size,
            max_files=max_files,
            log_html=log_target,
        ):
            log.start_run("Root Suite")
            log.start_task("my_task", "task_mod", __file__, 0)

            yield _SetupInfo(log_target)

            log.end_task("my_task", "task_mod", "PASS", "Ok")
            log.end_run("Root Suite", "PASS")

        assert log_target.exists()


class AutoLogConfigForTest(AutoLogConfigBase):
    def get_filter_kind_by_module_name(self, module_name: str) -> Optional[FilterKind]:
        if "check_lib_lib" in module_name or "check_iterators_lib" in module_name:
            return FilterKind.log_on_project_call

        if "check" in module_name:
            return FilterKind.full_log

        return FilterKind.exclude

    def get_filter_kind_by_module_name_and_path(
        self, module_name: str, filename: str
    ) -> FilterKind:
        filter_kind = self.get_filter_kind_by_module_name(module_name)
        assert filter_kind
        return filter_kind


@pytest.fixture(scope="session")
def resources_dir():
    f = __file__
    resources_dir = os.path.join(os.path.dirname(f), "_resources")
    assert os.path.exists(resources_dir)
    return resources_dir


@pytest.fixture(scope="session", autouse=True)
def raise_exceptions():
    from robocorp.log import _lifecycle_hooks

    for callback in _lifecycle_hooks.iter_all_callbacks():
        callback.raise_exceptions = True


@pytest.fixture()
def log_setup(tmpdir):
    import io

    from robocorp import log

    log_target = Path(tmpdir.join("log.html"))

    stream = io.StringIO()

    with log.setup_auto_logging():
        with log.add_log_output(
            tmpdir, max_file_size="30kb", max_files=1, log_html=log_target
        ):
            with log.add_in_memory_log_output(write=stream.write):
                yield {"stream": stream, "log_target": log_target}


@pytest.fixture(scope="session")
def path_for_output_view_react_tests_robo() -> Path:
    f = Path(__file__).parent
    robotframework_output_stream_root = f / ".." / ".."
    contents = os.listdir(robotframework_output_stream_root)
    assert "output-react" in contents
    ret = robotframework_output_stream_root / "output-react"
    assert ret.exists()

    return (ret / "test_view_integrated_react").absolute()


@pytest.fixture(scope="session")
def run_integration_tests_flag():
    matrix_name = os.environ.get("GITHUB_ACTIONS_MATRIX_NAME")
    if matrix_name:
        # On ci run just if 'outviewintegrationtests' is in the matrix name.
        return "outviewintegrationtests" in matrix_name

    # Run locally
    return True


@pytest.fixture(scope="session")
def robo_loc(tmpdir_factory, run_integration_tests_flag):
    if not run_integration_tests_flag:
        return

    dirname = tmpdir_factory.mktemp("robo_dir")
    location = os.path.join(str(dirname), "robo")

    if sys.platform == "win32":
        location += ".exe"

    _build_and_copy_robo(location, force=False)
    assert os.path.exists(location), f"robo not found at: {location}."

    return Path(location)


def _build_and_copy_robo(location: str, force: bool = False) -> None:
    """
    Downloads robo to the given location. Note that we don't overwrite it if it
    already exists (unless force == True).

    :param location:
        The location to store the robo executable in the filesystem.
    :param force:
        Whether we should overwrite an existing installation.
    """

    if not os.path.exists(location) or force:
        repo_root = Path(__file__).absolute().parent.parent.parent.parent
        cli_dir = repo_root / "cli"
        assert cli_dir.exists()

        subprocess.check_call(["inv", "prepare"], cwd=cli_dir)
        subprocess.check_call(["inv", "build"], cwd=cli_dir)

        name = "robo"
        if sys.platform == "win32":
            name = "robo.exe"
        robo_at = cli_dir / "build" / name
        assert robo_at.exists()
        Path(location).write_bytes(robo_at.read_bytes())
        os.chmod(location, 0x755)


_format_msg: dict = {}
_format_msg["SE"] = lambda msg: f"SE: {msg['type']}: {msg['name']}"
_format_msg["EE"] = lambda msg: f"EE: {msg['type']}: {msg['status']}"
_format_msg["EA"] = lambda msg: f"EA: {msg['type']}: {msg['name']}: {msg['value']}"
_format_msg["STB"] = lambda msg: f"STB: {msg['message']}"
_format_msg["AS"] = lambda msg: f"AS: {msg['target']}: {msg['value']}"
_format_msg["ST"] = lambda msg: f"ST: {msg['name']}"
_format_msg["ET"] = lambda msg: f"ET: {msg['status']}"
_format_msg["SR"] = lambda msg: f"SR: {msg['name']}"
_format_msg["ER"] = lambda msg: f"ER: {msg['status']}"

_format_msg["RR"] = lambda msg: f"RR: {msg['name']}"
_format_msg["RT"] = lambda msg: f"RT: {msg['name']}"
_format_msg["RE"] = lambda msg: f"RE: {msg['type']}: {msg['name']}"
_format_msg["R"] = lambda msg: f"R: {msg['type']}: {msg['value']}"


_ignore = {
    "ETB",
    "TBV",
    "TBE",
    "I",
    "T",
    "ID",
    "V",
    "C",
    "STD",
    "ETD",
    "EPS",
    "L",
    "SPS",
}


def pretty_format_logs_from_log_html(log_html: Path, show_exception_vars=False):
    from robocorp.log import iter_decoded_log_format_from_log_html

    iter_in = iter_decoded_log_format_from_log_html(log_html)
    return pretty_format_logs_from_iter(
        iter_in, show_exception_vars=show_exception_vars
    )


def pretty_format_logs_from_stream(stream: IReadLines, show_exception_vars=False):
    from robocorp.log import iter_decoded_log_format_from_stream

    iter_in = iter_decoded_log_format_from_stream(stream)
    return pretty_format_logs_from_iter(
        iter_in, show_exception_vars=show_exception_vars
    )


def pretty_format_logs_from_iter(iter_in, show_exception_vars=False):
    import re

    format_msg = _format_msg
    ignore = _ignore
    if show_exception_vars:
        ignore = _ignore.copy()
        ignore.remove("TBV")
        ignore.remove("TBE")
        format_msg = _format_msg.copy()
        format_msg["TBE"] = lambda msg: f"TBE --- {msg['method']} ---"
        format_msg["TBV"] = lambda msg: f"TBV: {msg['name']}: {msg['value']}"

    level = 0
    indent = ""
    out = ["\n"]
    regular_start_found = False
    for msg in iter_in:
        msg_type = msg["message_type"]
        if msg_type not in format_msg:
            if msg_type in ignore:
                continue
            print("Check: ", msg)
            continue

        if msg_type in ("EE", "ET", "ER"):
            level -= 1
            indent = "    " * level

        try:
            formatted = format_msg[msg_type](msg)
            pattern = r"at 0x[0-9A-Fa-f]+>"
            formatted = re.sub(pattern, "at 0xXXXXXXXXX>", formatted)
            out.append(f"{indent}{formatted}\n")
        except:
            raise RuntimeError(f"Error handling message: {msg}")

        is_restart = msg_type in ("RR", "RT", "RE")
        if is_restart and regular_start_found:
            continue

        if not regular_start_found:
            if msg_type in ("SE", "ST", "SR"):
                regular_start_found = True

        if msg_type in ("SE", "ST", "SR") or is_restart:
            if msg_type == "SE" and msg["type"] in (
                "UNTRACKED_GENERATOR",
                "IF",
                "ELSE",
            ):
                continue

            level += 1
            indent = "    " * level
    return "".join(out)
