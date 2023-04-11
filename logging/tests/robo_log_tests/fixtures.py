import pytest
import os
import sys
from pathlib import Path
from typing import List, Sequence


@pytest.fixture(scope="session")
def resources_dir(tmpdir_factory):
    f = __file__
    resources_dir = os.path.join(os.path.dirname(f), "_resources")
    assert os.path.exists(resources_dir)
    return resources_dir


@pytest.fixture(scope="session", autouse=True)
def raise_exceptions():
    from robo_log import _rewrite_callbacks

    for callback in _rewrite_callbacks.iter_all_callbacks():
        callback.raise_exceptions = True


def verify_log_messages_from_messages_iterator(
    messages_iterator, expected: Sequence[dict]
) -> Sequence[dict]:
    expected_lst: List[dict] = list(expected)
    log_messages = tuple(messages_iterator)
    log_msg: dict
    for log_msg in log_messages:
        for expected_dct in expected_lst:
            for key, val in expected_dct.items():
                if log_msg.get(key) != val:
                    break
            else:
                expected_lst.remove(expected_dct)
                break

    if expected_lst:
        new_line = "\n"
        raise AssertionError(
            f"Did not find {expected_lst}.\nFound:\n{new_line.join(str(x) for x in log_messages)}"
        )
    return log_messages


def verify_log_messages(stream, expected: Sequence[dict]) -> Sequence[dict]:
    from robo_log import iter_decoded_log_format

    return verify_log_messages_from_messages_iterator(
        iter_decoded_log_format(stream), expected
    )


@pytest.fixture()
def log_setup(tmpdir):
    import robo_log
    import io

    log_target = Path(tmpdir.join("log.html"))

    stream = io.StringIO()

    with robo_log.setup_auto_logging():
        with robo_log.add_log_output(
            tmpdir, max_file_size="30kb", max_files=1, log_html=log_target
        ):
            with robo_log.add_in_memory_log_output(write=stream.write):
                yield {"stream": stream}


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
