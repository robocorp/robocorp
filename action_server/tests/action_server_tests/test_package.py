import os
import re
import zipfile


def check_regexp_in_lines(text, regexp):
    """Checks if the given regexp is found in any line of the text.

    Args:
      text: The text to search in.
      regexp: The regular expression to search for.

    Returns:
      True if the regexp is found in any line, False otherwise.
    """

    compiled_regexp = re.compile(regexp)
    for line in text.splitlines():
        if compiled_regexp.search(line) is not None:
            return
    raise RuntimeError(f"Did not find regexp: {regexp} in text:\n{text}")


def test_package_zip(datadir):
    from robocorp.action_server._selftest import robocorp_action_server_run

    output = robocorp_action_server_run(
        [
            "package",
            "build",
            "--output-dir",
            str(datadir),
            "--datadir",
            str(datadir / "data"),
            # "-v",
        ],
        returncode=0,
        cwd=datadir / "pack1",
    )
    zip_name = "pack1-name-0.2a1.zip"
    escaped = re.escape(zip_name)
    check_regexp_in_lines(output.stderr, f"Created(.*){escaped}")

    target_zip = datadir / zip_name
    assert os.path.exists(target_zip)

    with zipfile.ZipFile(target_zip, "r") as zip_file:
        file_names = set(zip_file.namelist())

    assert file_names == {
        "another/ok.txt",
        "folder/dont_ignore",
        "hello_action.py",
        "package.yaml",
        "folder/ignore_only_at_root",
    }

    # Extract it
    extract_to = datadir / "extracted"

    def extract():
        robocorp_action_server_run(
            [
                "package",
                "extract",
                "--override",
                "--output-dir",
                str(extract_to),
                str(target_zip),
            ],
            returncode=0,
            cwd=datadir,
        )
        files = set(f.name for f in extract_to.glob("*"))
        assert files == {
            "another",
            "folder",
            "hello_action.py",
            "package.yaml",
        }

    extract()
    # Just remove the package.yaml and see if it's restored.
    os.remove(extract_to / "package.yaml")
    extract()


def test_package_zip_no_actions(datadir):
    from robocorp.action_server._selftest import robocorp_action_server_run

    output = robocorp_action_server_run(
        [
            "package",
            "build",
            "--output-dir",
            str(datadir),
            "--datadir",
            str(datadir / "data"),
        ],
        returncode=1,
        cwd=datadir / "pack2",
    )
    assert "No actions found in " in output.stderr


def test_package_metadata(datadir, data_regression):
    import json

    from robocorp.action_server._selftest import robocorp_action_server_run

    output = robocorp_action_server_run(
        [
            "package",
            "metadata",
            "--datadir",
            str(datadir / "data"),
        ],
        returncode=0,
        cwd=datadir / "pack1",
    )
    data_regression.check(json.loads(output.stdout))
