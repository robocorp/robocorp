import os.path
import subprocess
import sys
from contextlib import nullcontext
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import pytest


@pytest.fixture(scope="session")
def ci_endpoint() -> str:
    ci_endpoint = os.environ.get("CI_ENDPOINT")
    if ci_endpoint is None:
        raise AssertionError("CI_ENDPOINT env variable must be specified for tests.")
    return ci_endpoint


@pytest.fixture(scope="session")
def ci_credentials() -> str:
    ci_credentials = os.environ.get("CI_CREDENTIALS")
    if ci_credentials is None:
        raise AssertionError("CI_CREDENTIALS env variable must be specified for tests.")
    return ci_credentials


@pytest.fixture(scope="session")
def rcc_loc(tmpdir_factory):
    tests_rcc_dir = os.path.expanduser("~/.robocorp_tests_rcc")
    os.makedirs(tests_rcc_dir, exist_ok=True)

    # tests_rcc_dir = tmpdir_factory.mktemp("rcc_dir")

    location = os.path.join(str(tests_rcc_dir), f"rcc_{RCC_VERSION}")
    if sys.platform == "win32":
        location += ".exe"
    _download_rcc(location, force=False)
    assert os.path.exists(location)

    # Disable tracking for tests
    subprocess.check_call([location] + "configure identity --do-not-track".split())
    return Path(location)


@pytest.fixture
def rcc(rcc_loc, robocorp_home, ci_endpoint):
    from devutils.rcc import Rcc

    return Rcc(rcc_loc, robocorp_home, ci_endpoint)


def run_in_rcc(rcc_loc: Path, cwd: Path, args: Sequence[str] = (), expect_error=False):
    from subprocess import CalledProcessError

    env = os.environ.copy()
    env.pop("PYTHONPATH", "")
    env.pop("PYTHONHOME", "")
    env.pop("VIRTUAL_ENV", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    if expect_error:
        ctx: Any = pytest.raises(CalledProcessError)
    else:
        ctx = nullcontext()

    with ctx:
        subprocess.check_call(
            [str(rcc_loc), "task", "run", "--trace"] + list(args), cwd=cwd, env=env
        )


@pytest.fixture(scope="session")
def robocorp_home(tmpdir_factory) -> str:
    # import shutil
    #
    # ret = "c:/temp/tests_robohome"
    # shutil.rmtree(os.path.join(ret, ".robocorp_code"), ignore_errors=True)
    # return ret

    dirname = tmpdir_factory.mktemp("robocorp_home")

    return str(dirname)


RCC_VERSION = "v14.6.0"


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
                os.chmod(location, 0x755)
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

    def check(self, obtained: str, basename=None, fullpath=None):
        """
        Checks the given str against a previously recorded version, or generate
        a new file.

        :param str obtained: The contents obtained

        :param str basename: basename of the file to test/record. If not given the name
            of the test is used.
            Use either `basename` or `fullpath`.

        :param str fullpath: complete path to use as a reference file. This option
            will ignore ``datadir`` fixture when reading *expected* files but
            will still use it to write *obtained* files. Useful if a reference
            file is located in the session data dir for example.

        ``basename`` and ``fullpath`` are exclusive.
        """
        from pytest_regressions.common import perform_regression_check  # type: ignore

        __tracebackhide__ = True

        def dump(f):
            # Change the binary chars for its repr.
            new_obtained = "".join(
                (x if (x.isprintable() or x in ("\r", "\n")) else repr(x))
                for x in obtained
            )
            f.write_bytes(
                "\n".join(new_obtained.splitlines(keepends=False)).encode("utf-8")
            )

        def check_fn(obtained_path, expected_path):
            from io import StringIO
            from itertools import zip_longest

            obtained = obtained_path.read_bytes().decode("utf-8", "replace")
            expected = expected_path.read_bytes().decode("utf-8", "replace")

            lines1 = obtained.strip().splitlines(keepends=False)
            lines2 = expected.strip().splitlines(keepends=False)
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
                    f"Strings don't match. "
                    f"Obtained:\n\n{obtained}\n\nComparison:\n{stream.getvalue()}"
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

    def check_until_header(self, found: str):
        header_end = "=" * 80
        header_end_i = found.rfind(header_end)
        assert header_end_i > 0
        found = found[: header_end_i + len(header_end)]

        self.check(found)


@pytest.fixture
def str_regression(datadir, original_datadir, request):
    return StrRegression(datadir, original_datadir, request)


def robocorp_tasks_run(
    cmdline, returncode, cwd=None, additional_env: Optional[Dict[str, str]] = None
):
    cp = os.environ.copy()
    cp["PYTHONPATH"] = os.pathsep.join([x for x in sys.path if x])
    if additional_env:
        cp.update(additional_env)
    args = [sys.executable, "-m", "robocorp.tasks"] + cmdline
    result = subprocess.run(args, capture_output=True, env=cp, cwd=cwd)
    if result.returncode != returncode:
        env_str = "\n".join(str(x) for x in sorted(cp.items()))

        raise AssertionError(
            f"""Expected returncode: {returncode}. Found: {result.returncode}.
=== stdout:
{result.stdout.decode('utf-8')}

=== stderr:
{result.stderr.decode('utf-8')}

=== Env:
{env_str}

=== Args:
{args}

"""
        )
    return result


@pytest.fixture
def pyfile(request, datadir):
    """
    Based on debugpy pyfile fixture.

    A fixture providing a factory function that generates .py files.

    The returned factory takes a single function with an empty argument list,
    generates a temporary file that contains the code corresponding to the
    function body, and returns the full path to the generated file. Idiomatic
    use is as a decorator, e.g.:

        @pyfile
        def script_file():
            print('fizz')
            print('buzz')

    will produce a temporary file named script_file.py containing:

        print('fizz')
        print('buzz')

    and the variable script_file will contain the path to that file.

    In order for the factory to be able to extract the function body properly,
    function header ("def") must all be on a single line, with nothing after
    the colon but whitespace.

    Note that because the code is physically in a separate file when it runs,
    it cannot reuse top-level module imports - it must import all the modules
    that it uses locally. When linter complains, use #noqa.

    Returns a string to the generated file written to disk.
    """
    import types
    import inspect

    def factory(source) -> str:
        assert isinstance(source, types.FunctionType)
        name = source.__name__
        source, _ = inspect.getsourcelines(source)

        # First, find the "def" line.
        def_lineno = 0
        for line in source:
            line = line.strip()
            if line.startswith("def") and line.endswith(":"):
                break
            def_lineno += 1
        else:
            raise ValueError("Failed to locate function header.")

        # Remove everything up to and including "def".
        source = source[def_lineno + 1 :]
        assert source

        # Now we need to adjust indentation. Compute how much the first line of
        # the body is indented by, then dedent all lines by that amount. Blank
        # lines don't matter indentation-wise, and might not be indented to begin
        # with, so just replace them with a simple newline.
        for line in source:
            if line.strip():
                break  # i.e.: use first non-empty line
        indent = len(line) - len(line.lstrip())
        source = [line[indent:] if line.strip() else "\n" for line in source]
        source = "".join(source)

        # Write it to file.
        tmpfile = os.path.join(str(datadir), name + ".py")
        assert not os.path.exists(tmpfile), "%s already exists." % (tmpfile,)
        with open(tmpfile, "w") as stream:
            stream.write(source)

        return tmpfile

    return factory
