import os
import subprocess
import sys

from robocorp.log._safe_write_to_stream import safe_write_to_stream


def test_write_to_stream():
    """
    We run in a subprocess that only accepts ascii in the output
    to check that our safe_write_to_stream works properly.
    """
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "ascii"
    result = subprocess.run(
        [sys.executable, __file__], encoding="ascii", env=env, stdout=subprocess.PIPE
    )
    assert result.stdout == "a??o\n"


def check_safe_write_to_stream():
    stdout = sys.stdout
    encoding = stdout.encoding
    assert encoding == "ascii", f"Found encoding: {encoding}"
    try:
        stdout.write("ação\n")
    except UnicodeEncodeError:
        pass
    else:
        raise AssertionError(
            "Expected an error when writing to stdout with unicode chars."
        )

    safe_write_to_stream(stdout, "ação\n")


if __name__ == "__main__":
    check_safe_write_to_stream()
