from contextlib import contextmanager
from pathlib import Path
from robocorp.log import BaseConfig, FilterKind
from robocorp.log.protocols import LogHTMLStyle
from typing import Optional, List

import os
import pytest
import sys
import typing


class _SetupInfo:
    def __init__(self, log_target):
        self.log_target = log_target

    def open_log_target(self):
        import webbrowser

        webbrowser.open(self.log_target.as_uri())


class UIRegenerateFixture:
    # Must be set to False when merging to master and
    # python -m dev build-output-view
    # must also be manually called afterwards.
    FORCE_REGEN: List[typing.Union[str, int]] = []

    OPEN_IN_BROWSER = False

    PRINT_MESSAGES = False

    LOG_HTML_STYLE: LogHTMLStyle = "standalone"

    def regenerate(self) -> None:
        if not self.FORCE_REGEN:
            return

        import subprocess

        cwd = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        cmd = [sys.executable, "-m", "dev", "build-output-view"]
        if "dev" in self.FORCE_REGEN:
            cmd.append("--dev")

        versions: List[int] = []
        for setting in self.FORCE_REGEN:
            if isinstance(setting, int):
                versions.append(setting)

        if versions:
            cmd.append(f"--version={','.join(str(x) for x in versions)}")
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
        if uiregenerate_fixture.LOG_HTML_STYLE == "vscode":
            uiregenerate_fixture.FORCE_REGEN.append(1)
        else:
            uiregenerate_fixture.FORCE_REGEN.append(2)

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
    tmpdir, max_file_size="1MB", max_files=5, config: Optional[BaseConfig] = None
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


class ConfigForTest(BaseConfig):
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
def resources_dir(tmpdir_factory):
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
    from robocorp import log
    import io

    log_target = Path(tmpdir.join("log.html"))

    stream = io.StringIO()

    with log.setup_auto_logging():
        with log.add_log_output(
            tmpdir, max_file_size="30kb", max_files=1, log_html=log_target
        ):
            with log.add_in_memory_log_output(write=stream.write):
                yield {"stream": stream, "log_target": log_target}


@pytest.fixture(scope="session")
def rcc_loc(tmpdir_factory):
    import subprocess

    dirname = tmpdir_factory.mktemp("rcc_dir")
    location = os.path.join(str(dirname), "rcc")
    if sys.platform == "win32":
        location += ".exe"
    _download_rcc(location, force=False)
    assert os.path.exists(location)

    # Disable tracking for tests
    subprocess.check_call([location] + "configure identity --do-not-track".split())
    return location


@pytest.fixture(scope="session")
def path_for_tests_robot() -> Path:
    f = Path(__file__).parent
    robotframework_output_stream_root = f / ".." / ".."
    contents = os.listdir(robotframework_output_stream_root)
    assert "output-webview" in contents
    ret = robotframework_output_stream_root / "output-webview"
    assert ret.exists()
    ret = ret / "tests"
    assert ret.exists()
    return ret


def _download_rcc(location: str, force: bool = False) -> None:
    """
    Downloads rcc to the given location. Note that we don't overwrite it if it
    already exists (unless force == True).

    :param location:
        The location to store the rcc executable in the filesystem.
    :param force:
        Whether we should overwrite an existing installation.
    """

    if not os.path.exists(location) or force:
        if not os.path.exists(location) or force:
            import platform
            import urllib.request

            machine = platform.machine()
            is_64 = not machine or "64" in machine

            if sys.platform == "win32":
                if is_64:
                    relative_path = "/windows64/rcc.exe"
                else:
                    relative_path = "/windows32/rcc.exe"

            elif sys.platform == "darwin":
                relative_path = "/macos64/rcc"

            else:
                if is_64:
                    relative_path = "/linux64/rcc"
                else:
                    relative_path = "/linux32/rcc"

            RCC_VERSION = "v13.5.5"
            prefix = f"https://downloads.robocorp.com/rcc/releases/{RCC_VERSION}"
            url = prefix + relative_path

            # log.info(f"Downloading rcc from: {url} to: {location}.")
            response = urllib.request.urlopen(url)

            # Put it all in memory before writing (i.e. just write it if
            # we know we downloaded everything).
            data = response.read()

            try:
                os.makedirs(os.path.dirname(location))
            except Exception:
                pass  # Error expected if the parent dir already exists.

            try:
                with open(location, "wb") as stream:
                    stream.write(data)
                os.chmod(location, 0x744)
            except Exception:
                sys.stderr.write(
                    f"Error writing to: {location}.\nParent dir exists: {os.path.exists(os.path.dirname(location))}\n"
                )
                raise


class StrRegression:
    def __init__(self, datadir, original_datadir, request):
        """
        :type datadir: Path
        :type original_datadir: Path
        :type request: FixtureRequest
        """
        self.request = request
        self.datadir = datadir
        self.original_datadir = original_datadir
        self.force_regen = False

    def check(self, expected: Path, basename=None, fullpath=None):
        """
        Checks the given str against a previously recorded version, or generate a new file.

        :param str expected: The path with contents expected

        :param str basename: basename of the file to test/record. If not given the name
            of the test is used.
            Use either `basename` or `fullpath`.

        :param str fullpath: complete path to use as a reference file. This option
            will ignore ``datadir`` fixture when reading *expected* files but will still use it to
            write *obtained* files. Useful if a reference file is located in the session data dir for example.

        ``basename`` and ``fullpath`` are exclusive.
        """
        from pytest_regressions.common import perform_regression_check  # type: ignore

        __tracebackhide__ = True

        def dump(filename):
            with filename.open("w", encoding="utf-8") as f:
                f.write(expected)

        def check_fn(obtained_path, expected_path):
            from itertools import zip_longest
            from io import StringIO

            obtained = obtained_path.read_text()
            expected = expected_path.read_text()

            lines1 = obtained.strip().splitlines()
            lines2 = expected.strip().splitlines()
            if lines1 != lines2:
                max_line_length = max(
                    len(line) for line in lines1 + lines2 + ["=== Obtained ==="]
                )
                stream = StringIO()

                status = "   "
                print(
                    status
                    + "{:<{width}}\t{:<{width}}".format(
                        "=== Obtained ===", "=== Expected ===", width=max_line_length
                    ),
                    file=stream,
                )
                for line1, line2 in zip_longest(lines1, lines2, fillvalue=""):
                    if line1 != line2:
                        status = "!! "
                    else:
                        status = "   "
                    print(
                        status
                        + "{:<{width}}\t{:<{width}}".format(
                            line1, line2, width=max_line_length
                        ),
                        file=stream,
                    )
                raise AssertionError(
                    f"Strings don't match. Obtained:\n\n{obtained}\n\nComparison:\n{stream.getvalue()}"
                )

        perform_regression_check(
            datadir=self.datadir,
            original_datadir=self.original_datadir,
            request=self.request,
            check_fn=check_fn,
            dump_fn=dump,
            extension=".txt",
            basename=basename,
            fullpath=fullpath,
            force_regen=self.force_regen,
        )


@pytest.fixture
def str_regression(datadir, original_datadir, request):
    return StrRegression(datadir, original_datadir, request)
