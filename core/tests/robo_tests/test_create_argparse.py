import pytest

import io
from contextlib import redirect_stdout, redirect_stderr


def test_argparse():
    from robo._argdispatch import arg_dispatch

    parser = arg_dispatch.argparser

    s = io.StringIO()
    with redirect_stdout(s):
        with pytest.raises(SystemExit) as e:
            parser.parse_args(["--help"])
        assert e.value.code == 0
    assert "show this help message and exit" in s.getvalue()

    s = io.StringIO()
    with redirect_stdout(s):
        with pytest.raises(SystemExit) as e:
            parser.parse_args(["run", "--help"])
        assert e.value.code == 0
    assert "show this help message and exit" in s.getvalue()

    parsed = parser.parse_args(["run", "target_dir", "-o=./out", "-t=task-name"])
    assert parsed.command == "run"
    assert parsed.path == "target_dir"
    assert parsed.output_dir == "./out"
    assert parsed.task_name == "task-name"


def test_argparse_command_invalid():
    from robo.cli import main

    s = io.StringIO()
    with redirect_stdout(s):
        assert main([], exit=False) == 1  # No arguments
    assert "show this help message and exit" in s.getvalue()

    s = io.StringIO()
    with redirect_stdout(s):
        assert main(["-h"], exit=False) == 0  # Help
    assert "show this help message and exit" in s.getvalue()

    s = io.StringIO()
    with redirect_stderr(s):
        assert main(["wrong"], exit=False) == 2  # Wrong choice.
    assert "invalid choice: 'wrong'" in s.getvalue()
