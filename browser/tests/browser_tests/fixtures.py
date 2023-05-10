import os
import sys

import pytest


def robo_run(cmdline, returncode, cwd=None, additional_env=None):
    import subprocess

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
