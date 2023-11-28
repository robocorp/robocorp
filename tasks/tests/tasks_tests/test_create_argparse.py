import io
from contextlib import redirect_stderr, redirect_stdout

import pytest


def test_argparse():
    from robocorp.tasks._argdispatch import arg_dispatch

    parser = arg_dispatch._create_argparser()

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
    assert parsed.task_name == ["task-name"]

    parsed = parser.parse_args(
        ["run", "target_dir", "--max-log-files=5", "--max-log-file-size=2MB"]
    )
    assert parsed.command == "run"
    assert parsed.path == "target_dir"
    assert parsed.max_log_files == 5
    assert parsed.max_log_file_size == "2MB"

    parsed = arg_dispatch.parse_args(
        [
            "run",
            "target_dir",
            "--max-log-files=5",
            "--max-log-file-size=2MB",
            "--",
            "a=2",
            "b=3",
        ]
    )
    assert parsed.command == "run"
    assert parsed.path == "target_dir"
    assert parsed.max_log_files == 5
    assert parsed.max_log_file_size == "2MB"
    assert parsed.additional_arguments == ["a=2", "b=3"]


def test_argparse_command_invalid():
    from robocorp.tasks.cli import main

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
